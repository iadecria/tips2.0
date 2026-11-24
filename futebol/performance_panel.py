"""Reproducible performance summaries from immutable snapshots and linked settlements."""

from __future__ import annotations

from collections import Counter, defaultdict
import json
from pathlib import Path
from typing import Any, Iterable


def _selection_key(selection: dict[str, Any]) -> tuple[str, str, str, str, str]:
    return tuple(str(selection.get(key) or "UNKNOWN").strip().casefold()
                 for key in ("fixture", "period", "market", "side", "line"))


def _snapshot_selection(ticket: dict[str, Any], index: int) -> dict[str, Any] | None:
    source = ticket.get("sourceTicket", {})
    selections = source.get("selections", source.get("legs", []))
    if index >= len(selections) or not isinstance(selections[index], dict):
        return None
    selection = selections[index]
    return {
        "fixture": selection.get("match", selection.get("fixture", selection.get("event"))),
        "period": selection.get("period", selection.get("timeframe")),
        "market": selection.get("market", selection.get("marketName")),
        "side": selection.get("side", selection.get("selection", selection.get("pick"))),
        "line": selection.get("line", selection.get("handicap", selection.get("total"))),
    }


def _empty_rate(wins: int, losses: int) -> float | str:
    denominator = wins + losses
    return round(wins / denominator, 4) if denominator else "sem amostra"


def build_performance_panel(snapshots: Iterable[dict[str, Any]],
                            settlements: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Summarize linked data only; simulated and executed records stay separate."""
    snapshots_by_id = {}
    rounds_by_version: dict[str, set[str]] = defaultdict(set)
    ticket_by_id = {}
    for snapshot in snapshots:
        metadata = snapshot.get("metadata", {})
        snapshot_id = metadata.get("snapshotId")
        if not snapshot_id:
            continue
        snapshots_by_id[snapshot_id] = snapshot
        version = str(metadata.get("methodologyVersion") or "unknown")
        rounds_by_version[version].add(str(metadata.get("date") or "unknown"))
        for ticket in snapshot.get("tickets", []):
            if isinstance(ticket, dict) and ticket.get("sourceKey"):
                ticket_by_id[(snapshot_id, ticket["sourceKey"])] = ticket

    strategy_rows: dict[tuple[str, str, str], dict[str, Any]] = {}
    selection_states: dict[tuple[str, str, str, tuple[str, ...]], str] = {}
    concentration: dict[tuple[str, str, str, tuple[str, ...]], set[tuple[str, str]]] = defaultdict(set)
    all_rounds_by_version = {key: len(value) for key, value in rounds_by_version.items()}

    for record in settlements:
        snapshot_id = record.get("snapshotId")
        snapshot = snapshots_by_id.get(snapshot_id)
        ticket = ticket_by_id.get((snapshot_id, record.get("ticketId")))
        if snapshot is None or ticket is None:
            continue
        metadata = snapshot.get("metadata", {})
        version = str(metadata.get("methodologyVersion") or "unknown")
        result = record.get("result", {})
        kind = "executed" if result.get("calculationBasis") == "VERIFIED_RECEIPT" else "simulated"
        strategy = str(ticket.get("type") or ticket.get("name") or "unknown")
        key = (version, kind, strategy)
        row = strategy_rows.setdefault(key, {
            "methodologyVersion": version, "mode": kind, "strategy": strategy,
            "ticketHIT": 0, "ticketMISS": 0, "ticketVOID": 0, "ticketPENDING": 0,
            "knownStake": 0.0, "knownReturn": 0.0, "financialSample": 0,
            "rounds": set(), "ticketCount": 0,
        })
        status = str(result.get("status", "PENDING")).upper()
        if status not in {"HIT", "MISS", "VOID", "PENDING"}:
            status = "PENDING"
        row[f"ticket{status}"] += 1
        row["ticketCount"] += 1
        date = str(metadata.get("date") or "unknown")
        row["rounds"].add(date)
        stake = record.get("stakeDeclared")
        actual_return = result.get("actualGrossReturn")
        if isinstance(stake, (int, float)) and isinstance(actual_return, (int, float)):
            row["knownStake"] += stake
            row["knownReturn"] += actual_return
            row["financialSample"] += 1

        evidence = record.get("selectionEvidence", [])
        for index, proof in enumerate(evidence):
            if not isinstance(proof, dict):
                continue
            selection = _snapshot_selection(ticket, index)
            if selection is None:
                continue
            selection_key = _selection_key(selection)
            identity = (version, kind, strategy, selection_key)
            concentration[identity].add((str(snapshot_id), str(record.get("ticketId"))))
            selection_states.setdefault(identity, str(proof.get("status", "PENDING")).upper())

    rows = []
    for key, row in sorted(strategy_rows.items()):
        version, kind, strategy = key
        states = Counter(status for (sel_version, sel_kind, sel_strategy, _), status in selection_states.items()
                         if sel_version == version and sel_kind == kind and sel_strategy == strategy)
        wins, losses = states["HIT"], states["MISS"]
        stake, returned = row["knownStake"], row["knownReturn"]
        rounds_seen = len(row["rounds"])
        total_rounds = all_rounds_by_version.get(row["methodologyVersion"], 0)
        rows.append({
            **{field: row[field] for field in ("methodologyVersion", "mode", "strategy", "ticketCount")},
            "HIT": wins, "MISS": losses, "VOID": states["VOID"], "PENDING": states["PENDING"],
            "ticketResults": {status: row[f"ticket{status}"] for status in ("HIT", "MISS", "VOID", "PENDING")},
            "selectionHitRate": _empty_rate(wins, losses),
            "sampleSize": wins + losses,
            "roundCoverage": {"covered": rounds_seen, "eligible": total_rounds,
                              "rate": round(rounds_seen / total_rounds, 4) if total_rounds else "sem amostra"},
            "knownFinancialSample": row["financialSample"],
            "knownStake": round(stake, 2) if row["financialSample"] else None,
            "knownGrossReturn": round(returned, 2) if row["financialSample"] else None,
            "knownNetReturn": round(returned - stake, 2) if row["financialSample"] else None,
            "roi": round((returned - stake) / stake, 4) if row["financialSample"] and stake else "sem amostra",
            "deduplication": "fixture+period+market+side+line dentro da versão/estratégia",
        })

    selection_rows = []
    grouped: dict[tuple[str, str, str], list[tuple[str, ...]]] = defaultdict(list)
    for version, kind, strategy, selection_key in selection_states:
        grouped[(version, kind, strategy)].append(selection_key)
    for (version, kind, strategy), keys in sorted(grouped.items()):
        unique = set(keys)
        state_counts = Counter(selection_states[(version, kind, strategy, key)] for key in unique)
        selection_rows.append({
            "methodologyVersion": version, "mode": kind, "strategy": strategy,
            "HIT": state_counts["HIT"], "MISS": state_counts["MISS"],
            "VOID": state_counts["VOID"], "PENDING": state_counts["PENDING"],
            "sampleSize": state_counts["HIT"] + state_counts["MISS"],
            "hitRate": _empty_rate(state_counts["HIT"], state_counts["MISS"]),
            "uniqueSelections": len(unique),
            "billetOccurrences": sum(len(concentration[(version, kind, strategy, item)]) for item in unique),
            "concentration": [
                {"selection": list(item), "ticketOccurrences": len(concentration[(version, kind, strategy, item)])}
                for item in sorted(unique) if len(concentration[(version, kind, strategy, item)]) > 1
            ],
        })

    return {
        "schemaVersion": 1,
        "source": "linked_snapshots_and_settlements_only",
        "metrics": {"hitRate": "HIT/(HIT+MISS); VOID e PENDING excluídos do denominador",
                    "roi": "(retorno bruto confirmado - stake conhecida)/stake conhecida",
                    "deduplication": "fixture+period+market+side+line dentro de versão/estratégia",
                    "simulationAndExecutionSeparated": True},
        "strategies": rows,
        "selections": selection_rows,
        "sampleStatus": "available" if rows else "sem amostra",
        "experimentProtocol": {
            "primaryMetric": "ROI líquido pareado por rodada elegível, com stake simulada total igual a 1 unidade por variante",
            "variants": ["primeira SAFE", "dupla das duas primeiras seleções de jogos distintos", "múltipla completa"],
            "period": "30 rodadas elegíveis consecutivas, máximo de 90 dias; publicar cobertura e dados faltantes",
            "pairing": "comparar somente as variantes na mesma rodada elegível; composição idêntica é uma única variante",
            "noBet": "registrar rodada e motivo; troca A→B separa atualização de dado esportivo de perda de horário",
            "promotion": "não promover antes de 30 rodadas; publicar diferença pareada, intervalo bootstrap de 95%, cobertura e impacto financeiro",
            "probabilities": "Brier somente para probabilidades numéricas definidas e registradas antes do kickoff; FAS Score ordinal excluído",
        },
    }


def load_local_panel(snapshots_root: str | Path, active_grade_path: str | Path) -> dict[str, Any]:
    """Load local immutable snapshots and settlement records without modifying files."""
    snapshots = []
    root = Path(snapshots_root)
    if root.exists():
        for path in sorted(root.glob("*/*.json")):
            if path.name == "manifest.json":
                continue
            try:
                snapshots.append(json.loads(path.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError):
                continue
    try:
        active = json.loads(Path(active_grade_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        active = {}
    return build_performance_panel(snapshots, active.get("settlementResults", []))


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Monta painel local reproduzível do FAS Futebol.")
    parser.add_argument("--snapshots", default=str(Path(__file__).resolve().parent / "snapshots"))
    parser.add_argument("--active", default=str(Path(__file__).resolve().parent / "bilhetes_ativos.json"))
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(load_local_panel(args.snapshots, args.active), ensure_ascii=False, indent=2))
