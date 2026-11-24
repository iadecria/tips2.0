"""Shared, conservative FAS settlement arithmetic for supported bet types."""

from __future__ import annotations

import copy
import itertools
import math
import os
import re
import tempfile
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Any


CENT = Decimal("0.01")
ZERO = Decimal("0")
ONE = Decimal("1")


class SettlementError(ValueError):
    """Invalid stake, odds, or settlement structure."""


def atomic_json_write(path: str | Path, value: Any) -> None:
    """Replace one JSON file atomically, leaving the prior file intact on failure."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=target.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            import json
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, target)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def _decimal(value: Any, label: str, *, minimum: Decimal | None = None) -> Decimal:
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        raise SettlementError(f"{label} ausente ou inválido.") from None
    if not result.is_finite() or (minimum is not None and result < minimum):
        raise SettlementError(f"{label} fora do intervalo permitido.")
    return result


def _money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def _float(value: Decimal | None) -> float | None:
    return float(value) if value is not None else None


def _status(value: Any) -> str:
    text = str(value or "PENDING").strip().upper()
    aliases = {
        "GREEN": "HIT", "WIN": "HIT", "WON": "HIT", "ACERTO": "HIT",
        "RED": "MISS", "LOSS": "MISS", "LOST": "MISS", "ERRO": "MISS",
        "REEMBOLSO": "VOID", "VOIDED": "VOID", "PUSH": "VOID", "ANULADA": "VOID",
        "PENDENTE": "PENDING", "UNKNOWN": "PENDING",
    }
    return aliases.get(text, text if text in {"HIT", "MISS", "VOID", "PENDING"} else "PENDING")


def _leg_odd(leg: dict[str, Any]) -> Decimal:
    odd = leg.get("acceptedOdd", leg.get("odd", leg.get("price")))
    return _decimal(odd, "Odd decimal", minimum=ONE)


def recalculate_odds(legs: list[dict[str, Any]], published_odd: Any = None) -> dict[str, Any]:
    """Multiply per-leg odds and identify a mismatch with a published product."""
    if not legs:
        raise SettlementError("Não há pernas para recalcular as odds.")
    product = ONE
    for leg in legs:
        product *= _leg_odd(leg)
    calculated = _money(product)
    published = _decimal(published_odd, "Odd global publicada", minimum=ONE) if published_odd is not None else None
    return {
        "calculatedOdd": _float(calculated),
        "unroundedProduct": str(product),
        "publishedOdd": _float(published),
        "difference": _float(_money(published - calculated)) if published is not None else None,
        "mismatch": published is not None and published != calculated,
        "basis": "PRODUCT_OF_PUBLISHED_DECIMAL_LEG_ODDS",
    }


def _requires_receipt(ticket: dict[str, Any], legs: list[dict[str, Any]]) -> bool:
    if ticket.get("boost") or ticket.get("specialCombination") or ticket.get("tax"):
        return True
    if ticket.get("acceptedOdd") is not None and ticket.get("multiplier") is not None:
        try:
            if _decimal(ticket["acceptedOdd"], "Odd aceita") != _decimal(ticket["multiplier"], "Odd publicada"):
                return True
        except SettlementError:
            return True
    fixtures = [leg.get("fixtureKey") or leg.get("matchKey") for leg in legs if isinstance(leg, dict)]
    duplicated_fixture = len([fixture for fixture in fixtures if fixture]) != len(set(fixture for fixture in fixtures if fixture))
    return duplicated_fixture or any(isinstance(leg, dict) and (leg.get("requiresReceipt") or leg.get("sameGameCombo") or leg.get("boost")) for leg in legs)


def _has_duplicate_fixtures(legs: list[dict[str, Any]]) -> bool:
    fixtures = [leg.get("fixtureKey") or leg.get("matchKey") for leg in legs if isinstance(leg, dict)]
    fixtures = [fixture for fixture in fixtures if fixture]
    return len(fixtures) != len(set(fixtures))


def _standard_result(stake: Decimal, legs: list[dict[str, Any]], *, equal_share: Decimal | None = None) -> dict[str, Any]:
    if not legs:
        return {"status": "PENDING", "grossReturn": None, "netResult": None, "reason": "Sem pernas verificáveis."}
    if any(not isinstance(leg, dict) for leg in legs):
        return {"status": "PENDING", "grossReturn": None, "netResult": None, "reason": "Pernas sem campos estruturados; resultado não pode ser inferido."}
    statuses = [_status(leg.get("status", leg.get("result"))) for leg in legs]
    stake_share = equal_share if equal_share is not None else stake
    if "MISS" in statuses:
        return {"status": "MISS", "grossReturn": ZERO, "netResult": -stake_share, "reason": None}
    if "PENDING" in statuses:
        return {"status": "PENDING", "grossReturn": None, "netResult": None, "reason": "Há resultado de perna ainda pendente."}
    product = ONE
    for leg, result_status in zip(legs, statuses):
        if result_status == "HIT":
            try:
                product *= _leg_odd(leg)
            except SettlementError as exc:
                return {"status": "PENDING", "grossReturn": None, "netResult": None, "reason": str(exc)}
        # VOID uses factor 1.00.
    gross = _money(stake_share * product)
    status = "VOID" if all(result_status == "VOID" for result_status in statuses) else "HIT"
    return {"status": status, "grossReturn": gross, "netResult": _money(gross - stake_share), "reason": None}


def _system_result(stake: Decimal, legs: list[dict[str, Any]], system: tuple[int, int]) -> dict[str, Any]:
    k, n = system
    if n != len(legs) or not (1 <= k <= n):
        return {"status": "PENDING", "grossReturn": None, "netResult": None,
                "reason": f"Sistema {k}/{n} declarado com {len(legs)} pernas; estrutura não confere."}
    combinations = list(itertools.combinations(range(n), k))
    per_combo = stake / Decimal(len(combinations))
    payouts: list[Decimal] = []
    pending = 0
    for indexes in combinations:
        combo_legs = [legs[index] for index in indexes]
        if any(not isinstance(leg, dict) for leg in combo_legs):
            pending += 1
            continue
        statuses = [_status(leg.get("status", leg.get("result"))) for leg in combo_legs]
        if "MISS" in statuses:
            payouts.append(ZERO)
            continue
        if "PENDING" in statuses:
            pending += 1
            continue
        product = ONE
        try:
            for leg, status in zip(combo_legs, statuses):
                if status == "HIT":
                    product *= _leg_odd(leg)
        except SettlementError:
            pending += 1
            continue
        payouts.append(per_combo * product)
    known_gross = sum(payouts, ZERO)
    if pending:
        return {"status": "PENDING", "grossReturn": None, "netResult": None,
                "knownCombinationReturn": _float(_money(known_gross)), "unroundedKnownCombinationReturn": str(known_gross),
                "settledCombinationCount": len(payouts),
                "pendingCombinationCount": pending, "combinationCount": len(combinations),
                "stakePerCombinationEstimated": _float(_money(per_combo)),
                "reason": "Há combinações com pernas pendentes; retorno total ainda desconhecido."}
    gross = _money(known_gross)
    all_void = all(_status(leg.get("status", leg.get("result"))) == "VOID" for leg in legs)
    status = "VOID" if all_void else ("HIT" if gross > ZERO else "MISS")
    return {"status": status, "grossReturn": gross, "netResult": _money(gross - stake),
            "unroundedGrossReturn": str(known_gross),
            "grossReturnPerUnit": _float((known_gross / stake).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)) if stake else 0.0,
            "combinationCount": len(combinations), "settledCombinationCount": len(combinations),
            "pendingCombinationCount": 0, "stakePerCombinationEstimated": _float(_money(per_combo)),
            "reason": None}


def _system_shape(ticket: dict[str, Any]) -> tuple[int, int] | None:
    system = ticket.get("system")
    if isinstance(system, str):
        match = re.search(r"(\d+)\s*/\s*(\d+)", system)
        if match:
            return int(match.group(1)), int(match.group(2))
    if isinstance(system, dict):
        try:
            return int(system["k"]), int(system["n"])
        except (KeyError, TypeError, ValueError):
            return None
    match = re.search(r"(?:SISTEMA\s*)?(\d+)\s*/\s*(\d+)", str(ticket.get("name", "")), re.IGNORECASE)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None


def _verified_receipt(receipt: Any) -> Decimal | None:
    if not isinstance(receipt, dict) or receipt.get("verified") is not True:
        return None
    value = receipt.get("grossReturn", receipt.get("actualGrossReturn"))
    return _decimal(value, "Retorno bruto do recibo", minimum=ZERO)


def settle_ticket(ticket: dict[str, Any], *, receipt: dict[str, Any] | None = None) -> dict[str, Any]:
    """Calculate a single, accumulator, system k/n, or independent stop variants.

    Decimal odds use half-up cent rounding for simulation. Unless a verified
    receipt is supplied, the result remains explicitly estimated.
    """
    stake = _decimal(ticket.get("stake"), "Stake total", minimum=ZERO)
    legs = ticket.get("legs") if isinstance(ticket.get("legs"), list) else []
    receipt = receipt or ticket.get("receipt")
    verified_gross = _verified_receipt(receipt)

    stop_points = ticket.get("stopPoints")
    if isinstance(stop_points, list) and stop_points:
        variants = []
        for index, stop in enumerate(stop_points):
            if not isinstance(stop, dict):
                continue
            stop_legs = stop.get("legs") if isinstance(stop.get("legs"), list) else []
            result = _standard_result(stake, stop_legs)
            if _requires_receipt(ticket, stop_legs) and verified_gross is None:
                conditional = _serialize_result(result) if _has_duplicate_fixtures(stop_legs) else None
                result = {"status": "PENDING", "grossReturn": None, "netResult": None,
                          "conditionalEstimate": conditional,
                          "reason": "Mercados combinados do mesmo jogo requerem confirmação de aceitação/recibo."}
            odds_audit = None
            if stop_legs and all(isinstance(leg, dict) and leg.get("odd", leg.get("price", leg.get("acceptedOdd"))) is not None for leg in stop_legs):
                odds_audit = recalculate_odds(stop_legs, stop.get("multiplier"))
            variants.append({
                "id": stop.get("id", stop.get("level", f"STOP_{index + 1}")),
                "publishedOdd": stop.get("multiplier"),
                "oddsAudit": odds_audit,
                **_serialize_result(result),
            })
        chosen = ticket.get("executedStopPoint")
        if chosen is None:
            return {"status": "PENDING", "grossReturn": None, "netResult": None,
                    "actualGrossReturn": None, "calculationBasis": "STOP_POINT_VARIANTS_NOT_SELECTED",
                    "stopVariants": variants, "reason": "Não foi informado qual Stop Point foi efetivamente executado."}
        selected = next((item for item in variants if item["id"] == chosen), None)
        if selected is None:
            return {"status": "PENDING", "grossReturn": None, "netResult": None,
                    "actualGrossReturn": None, "calculationBasis": "STOP_POINT_UNKNOWN",
                    "stopVariants": variants, "reason": f"Stop Point executado desconhecido: {chosen}."}
        return _apply_receipt(selected, receipt, verified_gross, stake, variants=variants, stop_id=chosen)

    special = _requires_receipt(ticket, legs)
    shape = _system_shape(ticket)
    if special and verified_gross is None:
        conditional = None
        if _has_duplicate_fixtures(legs):
            projected = _system_result(stake, legs, shape) if shape else _standard_result(stake, legs)
            conditional = _serialize_result(projected)
        return {"status": "PENDING", "grossReturn": None, "netResult": None, "actualGrossReturn": None,
                "calculationBasis": "RECEIPT_REQUIRED", "conditionalEstimate": conditional,
                "reason": "Boost, combinação especial, mesma partida em múltiplas pernas, taxa ou odd divergente requer recibo."}

    is_system = shape is not None or ticket.get("system") is not None or str(ticket.get("type", "")).upper() in {"SYSTEM", "IMPROVABLE", "IMPROVAVEL"}
    if is_system and shape is None:
        return {"status": "PENDING", "grossReturn": None, "netResult": None, "actualGrossReturn": None,
                "calculationBasis": "SYSTEM_FORMAT_UNKNOWN", "reason": "Formato k/n de sistema ausente ou inválido."}
    if shape:
        calculated = _system_result(stake, legs, shape)
        basis = "ESTIMATED_EQUAL_SYSTEM_COMBINATIONS"
    else:
        calculated = _standard_result(stake, legs)
        basis = "ESTIMATED_DECIMAL_ODDS_HALF_UP"
    if verified_gross is not None:
        return _apply_receipt(calculated, receipt, verified_gross, stake)
    return {
        **_serialize_result(calculated),
        "actualGrossReturn": None,
        "actualNetResult": None,
        "calculationBasis": basis,
        "returnEvidence": "ESTIMATE_NO_VERIFIED_RECEIPT",
    }


def _serialize_result(result: dict[str, Any]) -> dict[str, Any]:
    return {key: _float(value) if isinstance(value, Decimal) else value for key, value in result.items()}


def _apply_receipt(
    calculated: dict[str, Any], receipt: Any, gross: Decimal | None, expected_stake: Decimal,
    *, variants: list[dict[str, Any]] | None = None, stop_id: Any = None,
) -> dict[str, Any]:
    if gross is None:
        return {**_serialize_result(calculated), "actualGrossReturn": None, "actualNetResult": None,
                "calculationBasis": "ESTIMATED_DECIMAL_ODDS_HALF_UP", "returnEvidence": "ESTIMATE_NO_VERIFIED_RECEIPT"}
    stake = _decimal(receipt.get("stake"), "Stake do recibo", minimum=ZERO) if receipt.get("stake") is not None else expected_stake
    net = _money(gross - stake)
    receipt_status = _status(receipt.get("status"))
    final_status = calculated.get("status", "PENDING")
    if final_status == "PENDING" and receipt_status != "PENDING":
        final_status = receipt_status
    output = {
        **_serialize_result(calculated),
        "status": final_status,
        "grossReturn": _float(gross),
        "netResult": _float(net) if net is not None else None,
        "stakeUsed": _float(stake),
        "stakeDiffersFromDeclaration": stake != expected_stake,
        "actualGrossReturn": _float(gross),
        "actualNetResult": _float(net) if net is not None else None,
        "calculationBasis": "VERIFIED_RECEIPT",
        "returnEvidence": {"source": receipt.get("source"), "reference": receipt.get("reference")},
    }
    if variants is not None:
        output["stopVariants"] = variants
        output["executedStopPoint"] = stop_id
    return output


def apply_soros_settlement(
    state: dict[str, Any], *, settlement_id: str, track: str,
    settlement: dict[str, Any], date: str | None = None,
) -> tuple[dict[str, Any], bool, str]:
    """Advance the operational Soros cycle once, only from a verified receipt."""
    updated = copy.deepcopy(state)
    if track.upper() not in {"B", "TRILHA_B_OPERACIONAL", "OPERATIONAL"}:
        return updated, False, "Trilha teórica/não operacional; estado Soros preservado."
    history = updated.setdefault("history", [])
    if any(entry.get("liquidationId") == settlement_id for entry in history if isinstance(entry, dict)):
        return updated, False, "Liquidação já aplicada; repetição idempotente."
    if settlement.get("calculationBasis") != "VERIFIED_RECEIPT" or settlement.get("actualGrossReturn") is None:
        return updated, False, "Sem retorno confirmado por recibo; ciclo e cofre não alterados."
    status = _status(settlement.get("status"))
    if status not in {"HIT", "MISS", "VOID"}:
        return updated, False, "Resultado não liquidável; ciclo e cofre não alterados."

    day = int(updated.get("currentDay", 1))
    stake_in = _decimal(updated.get("currentStake", updated.get("initialStake", 10)), "Stake atual", minimum=ZERO)
    gross = _decimal(settlement["actualGrossReturn"], "Retorno confirmado", minimum=ZERO)
    initial = _decimal(updated.get("initialStake", 10), "Stake inicial", minimum=ZERO)
    history.append({
        "liquidationId": settlement_id,
        "date": date,
        "day": day,
        "stakeIn": _float(stake_in),
        "actualReturn": _float(gross),
        "netResult": _float(_money(gross - stake_in)),
        "status": status,
        "settlementBasis": "VERIFIED_RECEIPT",
    })

    if status == "HIT":
        vault = _decimal(updated.get("vaultProfit", ZERO), "Cofre Soros", minimum=ZERO)
        rules = updated.get("vaultRules", {})
        if day == 5:
            lock = _decimal(rules.get("day5Lock", initial), "Trava Dia 5", minimum=ZERO)
            updated["vaultProfit"] = _float(max(vault, lock))
        elif day == 7:
            lock = _decimal(rules.get("day7Lock", 20), "Trava Dia 7", minimum=ZERO)
            updated["vaultProfit"] = _float(_money(vault + lock))
        target = int(updated.get("targetDays", 30))
        if day >= target:
            updated["currentDay"] = target
            updated["currentStake"] = _float(gross)
            updated["status"] = "COMPLETE"
        else:
            updated["currentDay"] = day + 1
            updated["currentStake"] = _float(gross)
            updated["status"] = "ACTIVE"
    elif status == "MISS":
        updated["currentDay"] = 1
        updated["currentStake"] = _float(initial)
        updated["status"] = "ACTIVE"
    # VOID refunds the stake and leaves day, stake, and vault unchanged.
    return updated, True, "Liquidação operacional aplicada uma única vez."
