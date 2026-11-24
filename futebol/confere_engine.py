"""
FAS 3 - Motor de Auditoria e Disparo Noturno (Confere Engine V7.0)
Responsável por auditar os resultados, liquidar os bilhetes, atualizar o Soros e notificar o mensageiro.
"""

import os
import sys
import json
import datetime
import subprocess
import copy

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(current_dir)
sys.path.append(parent_dir)

import notifier
from settlement_engine import (
    SettlementError,
    apply_soros_settlement,
    atomic_json_write,
    settle_ticket,
)


def _same_finalization(existing, incoming):
    if existing == incoming:
        return True
    old_result = existing.get("result", {})
    new_result = incoming.get("result", {})
    return (
        old_result.get("actualGrossReturn") is None
        and new_result.get("actualGrossReturn") is not None
        and old_result.get("status") in {"PENDING", new_result.get("status")}
    )


def _overlay_leg_outcomes(frozen_legs, reported_legs):
    if not isinstance(frozen_legs, list) or not isinstance(reported_legs, list) or len(frozen_legs) != len(reported_legs):
        return None, "Quantidade de pernas da evidência difere do snapshot congelado."
    merged = []
    for frozen, reported in zip(frozen_legs, reported_legs):
        if not isinstance(frozen, dict) or not isinstance(reported, dict):
            return None, "Pernas não estruturadas no snapshot; resultado permanece pendente."
        proof = reported.get("evidence")
        if not isinstance(proof, dict):
            return None, "Resultado sem evidência vinculada à seleção; manter pendente."
        expected_fixture = frozen.get("match", frozen.get("fixture", frozen.get("event")))
        expected_period = frozen.get("period", frozen.get("timeframe"))
        expected_date = frozen.get("date")
        if (not proof.get("source") or not proof.get("retrievedAt")
                or proof.get("fixture") != expected_fixture
                or proof.get("period") != expected_period
                or (expected_date and proof.get("date") != expected_date)):
            return None, "Fonte, horário, partida, data ou período da evidência não corresponde ao snapshot."
        status = reported.get("status", reported.get("settlementStatus", reported.get("result")))
        if proof.get("status") != status:
            return None, "Status divergente entre resultado informado e evidência da seleção."
        merged_leg = copy.deepcopy(frozen)
        merged_leg["status"] = status or "PENDING"
        merged.append(merged_leg)
    return merged, None


def _ticket_from_snapshot(snapshot_ticket, reported_ticket):
    frozen = snapshot_ticket.get("sourceTicket")
    if not isinstance(frozen, dict) or not isinstance(reported_ticket, dict):
        return None, "Ticket ou ticket congelado ausente."
    merged = copy.deepcopy(frozen)
    merged["stake"] = snapshot_ticket.get("stakeTotal")
    if isinstance(frozen.get("stopPoints"), list):
        reported_stops = reported_ticket.get("stopPoints")
        if not isinstance(reported_stops, list) or len(reported_stops) != len(frozen["stopPoints"]):
            return None, "Stop Points da evidência diferem do snapshot congelado."
        updated_stops = []
        for frozen_stop, reported_stop in zip(frozen["stopPoints"], reported_stops):
            if not isinstance(frozen_stop, dict) or not isinstance(reported_stop, dict):
                return None, "Stop Point sem estrutura verificável."
            legs, error = _overlay_leg_outcomes(frozen_stop.get("legs"), reported_stop.get("legs"))
            if error:
                return None, error
            updated_stop = copy.deepcopy(frozen_stop)
            updated_stop["legs"] = legs
            updated_stops.append(updated_stop)
        merged["stopPoints"] = updated_stops
        if reported_ticket.get("executedStopPoint") is not None:
            merged["executedStopPoint"] = reported_ticket["executedStopPoint"]
    else:
        source_key = "selections" if isinstance(frozen.get("selections"), list) else "legs"
        reported_legs = reported_ticket.get("legs", reported_ticket.get("selections"))
        legs, error = _overlay_leg_outcomes(frozen.get(source_key), reported_legs)
        if error:
            return None, error
        merged[source_key] = legs
        if source_key == "selections":
            merged["legs"] = legs
    return merged, None


def _linked_snapshot(data, base_dir):
    snapshot_id = data.get("snapshotId")
    date_value = data.get("date")
    if not snapshot_id or not date_value:
        return None
    path = os.path.join(base_dir, "snapshots", str(date_value), f"{snapshot_id}.json")
    try:
        with open(path, "r", encoding="utf-8") as stream:
            snapshot = json.load(stream)
    except (OSError, json.JSONDecodeError):
        return None
    return snapshot if snapshot.get("metadata", {}).get("snapshotId") == snapshot_id else None


def reconcile_financials(data, soros_state, *, snapshot=None, allow_mutation=True):
    """Calculate one snapshot's tickets and apply receipt-backed Soros once."""
    snapshot_id = data.get("snapshotId")
    evidence = data.get("settlementEvidence")
    if not isinstance(evidence, dict):
        return data, soros_state, {
            "status": "PENDING", "results": [], "sorosUpdated": False,
            "reason": "settlementEvidence ausente; nenhum saldo foi alterado.", "changed": False,
        }
    if not snapshot_id or evidence.get("snapshotId") != snapshot_id:
        raise SettlementError("settlementEvidence não corresponde ao snapshot ativo.")
    if not isinstance(snapshot, dict) or snapshot.get("metadata", {}).get("snapshotId") != snapshot_id:
        return data, soros_state, {
            "status": "PENDING", "results": [], "sorosUpdated": False,
            "reason": "Snapshot pré-jogo correspondente ausente ou divergente; liquidação não gravada.", "changed": False,
        }
    candidates = evidence.get("tickets")
    if not isinstance(candidates, list) or not candidates:
        return data, soros_state, {
            "status": "PENDING", "results": [], "sorosUpdated": False,
            "reason": "Nenhum bilhete possui evidência estruturada de liquidação.", "changed": False,
        }

    evidence_verified = evidence.get("verified") is True and bool(evidence.get("source")) and bool(evidence.get("retrievedAt"))
    updated_data = copy.deepcopy(data)
    previous_records = updated_data.setdefault("settlementResults", [])
    if not isinstance(previous_records, list):
        raise SettlementError("settlementResults precisa ser uma lista.")
    existing_by_id = {record.get("settlementId"): record for record in previous_records if isinstance(record, dict)}
    frozen_tickets = {item.get("sourceKey"): item for item in snapshot.get("tickets", []) if isinstance(item, dict)}
    new_records = []
    batch_ids = set()
    for candidate in candidates:
        if not isinstance(candidate, dict) or not candidate.get("ticketId"):
            raise SettlementError("Cada settlementEvidence.tickets precisa de ticketId.")
        ticket = candidate.get("ticket")
        if not isinstance(ticket, dict):
            raise SettlementError(f"ticket {candidate['ticketId']} precisa ter estrutura aritmética.")
        frozen_ticket = frozen_tickets.get(candidate["ticketId"])
        if frozen_ticket is None:
            raise SettlementError(f"ticketId {candidate['ticketId']} não existe no snapshot congelado.")
        ticket, merge_error = _ticket_from_snapshot(frozen_ticket, ticket)
        metadata_ticket = ticket if isinstance(ticket, dict) else candidate.get("ticket", {})
        receipt = candidate.get("receipt")
        result = ({"status": "PENDING", "grossReturn": None, "netResult": None, "actualGrossReturn": None,
                   "actualNetResult": None, "calculationBasis": "SNAPSHOT_SELECTIONS_UNSTRUCTURED", "reason": merge_error}
                  if merge_error else settle_ticket(ticket, receipt=receipt))
        divergence = None
        if receipt and receipt.get("verified") is True:
            receipt_status = receipt.get("status")
            receipt_gross = receipt.get("grossReturn")
            if ((receipt_status and receipt_status != result.get("status"))
                    or (receipt_gross is not None and result.get("actualGrossReturn") is not None
                        and float(receipt_gross) != float(result["actualGrossReturn"]))):
                divergence = {"type": "REPORT_RECEIPT_DIVERGENCE", "reportedStatus": result.get("status"),
                              "receiptStatus": receipt_status, "reportedGross": result.get("actualGrossReturn"),
                              "receiptGross": receipt_gross}
                result = {"status": "PENDING", "grossReturn": None, "netResult": None,
                          "actualGrossReturn": None, "actualNetResult": None,
                          "calculationBasis": "EVIDENCE_DIVERGENCE", "reason": "Relatório/JSON diverge do recibo."}
        track = candidate.get("track", metadata_ticket.get("track", "unknown"))
        if not evidence_verified:
            result = {
                "status": "PENDING", "grossReturn": None, "netResult": None,
                "actualGrossReturn": None, "actualNetResult": None,
                "calculationBasis": "EVIDENCE_UNVERIFIED",
                "reason": "Resultado sem fonte verificada e horário de consulta; manter pendente.",
            }
        record = {
            "settlementId": candidate.get("settlementId") or f"{snapshot_id}:{candidate['ticketId']}",
            "snapshotId": snapshot_id,
            "ticketId": candidate["ticketId"],
            "track": track,
            "ticketName": metadata_ticket.get("name", candidate["ticketId"]),
            "ticketType": metadata_ticket.get("type"),
            "stakeDeclared": frozen_ticket.get("stakeTotal"),
            "stakeSource": "FROZEN_SNAPSHOT",
            "source": evidence.get("source"),
            "retrievedAt": evidence.get("retrievedAt"),
            "result": result,
            "divergence": divergence,
        }
        reported_ticket = candidate.get("ticket", {})
        evidence_legs = reported_ticket.get("legs", reported_ticket.get("selections", []))
        if isinstance(evidence_legs, list):
            record["selectionEvidence"] = [copy.deepcopy(leg["evidence"]) for leg in evidence_legs
                                            if isinstance(leg, dict) and isinstance(leg.get("evidence"), dict)]
        if record["settlementId"] in batch_ids:
            raise SettlementError(f"settlementId repetido na mesma evidência: {record['settlementId']}.")
        batch_ids.add(record["settlementId"])
        existing = existing_by_id.get(record["settlementId"])
        if existing:
            if not _same_finalization(existing, record):
                raise SettlementError(f"settlementId {record['settlementId']} já foi gravado com resultado divergente.")
            if existing != record:
                index = previous_records.index(existing)
                previous_records[index] = record
                new_records.append(record)
        else:
            previous_records.append(record)
            existing_by_id[record["settlementId"]] = record
            new_records.append(record)

    updated_state = copy.deepcopy(soros_state)
    soros_changed = False
    soros_notes = []
    for record in [existing_by_id[c.get("settlementId") or f"{snapshot_id}:{c['ticketId']}"] for c in candidates]:
        if (str(record.get("ticketType", "")).upper() != "SOROS"
                and "SOROS" not in str(record.get("ticketName", "")).upper()
                and "SOROS" not in str(record.get("ticketId", "")).upper()):
            continue
        next_state, applied, note = apply_soros_settlement(
            updated_state,
            settlement_id=record["settlementId"],
            track=record.get("track", ""),
            settlement=record["result"],
            date=data.get("date"),
        )
        if applied:
            updated_state = next_state
            soros_changed = True
        soros_notes.append(note)

    resolved = sum(record["result"]["status"] in {"HIT", "MISS", "VOID"} for record in existing_by_id.values()
                   if record.get("snapshotId") == snapshot_id)
    pending = sum(record["result"]["status"] == "PENDING" for record in existing_by_id.values()
                  if record.get("snapshotId") == snapshot_id)
    candidate_records = [existing_by_id[c.get("settlementId") or f"{snapshot_id}:{c['ticketId']}"] for c in candidates]
    if pending:
        batch_status = "PENDING"
    elif candidate_records and all(item["result"].get("calculationBasis") == "VERIFIED_RECEIPT" for item in candidate_records):
        batch_status = "SETTLED"
    else:
        batch_status = "ESTIMATED"
    report = {
        "status": batch_status,
        "results": candidate_records,
        "resolvedCount": resolved,
        "pendingCount": pending,
        "sorosUpdated": soros_changed,
        "sorosNotes": soros_notes,
        "changed": bool(new_records),
        "stateChanged": soros_changed,
    }
    if not allow_mutation:
        return data, soros_state, report
    return updated_data, updated_state, report

def run_confere_pipeline():
    print("="*60)
    print("🌙 INICIANDO PIPELINE DE CONFERE NOTURNO FAS V7.0")
    print("="*60)

    bilhetes_file = os.path.join(current_dir, "bilhetes_ativos.json")
    if not os.path.exists(bilhetes_file):
        print(f"❌ Arquivo {bilhetes_file} não encontrado.")
        return False

    with open(bilhetes_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    soros_file = os.path.join(current_dir, "soros_state.json")
    if os.path.exists(soros_file):
        with open(soros_file, "r", encoding="utf-8") as f:
            soros_state = json.load(f)
    else:
        soros_state = {"initialStake": 10.0, "currentStake": 10.0, "currentDay": 1, "status": "ACTIVE", "history": []}

    snapshot = _linked_snapshot(data, current_dir)
    try:
        updated_data, updated_soros, financials = reconcile_financials(data, soros_state, snapshot=snapshot)
    except SettlementError as exc:
        print(f"❌ Liquidação interrompida: {exc}")
        return False

    if financials["changed"]:
        atomic_json_write(bilhetes_file, updated_data)
    if financials["stateChanged"]:
        atomic_json_write(soros_file, updated_soros)
    data = updated_data

    date_str = data.get("date", datetime.date.today().isoformat())
    if financials["results"]:
        stakes = [record["stakeDeclared"] for record in financials["results"] if isinstance(record.get("stakeDeclared"), (int, float))]
        gross = [record["result"].get("grossReturn") for record in financials["results"] if isinstance(record["result"].get("grossReturn"), (int, float))]
        net = [record["result"].get("netResult") for record in financials["results"] if isinstance(record["result"].get("netResult"), (int, float))]
        has_pending = financials["pendingCount"] > 0
        audit_summary = {
            "roundResult": f"{financials['status']} — liquidação aritmética por snapshot",
            "invested": round(sum(stakes), 2),
            "returned": None if has_pending else round(sum(gross), 2),
            "netProfit": None if has_pending else round(sum(net), 2),
            "pendingCount": financials["pendingCount"],
            "financialSettlements": financials["results"],
            "sorosNextDay": updated_soros.get("currentDay", 1),
            "sorosNextStake": updated_soros.get("currentStake", 10.0),
            "sorosVaultProfit": updated_soros.get("vaultProfit", 0.0),
        }
    else:
        audit_summary = {
            "roundResult": "PENDENTE — sem settlementEvidence estruturada; saldo e Soros preservados",
            "invested": 0.0, "returned": 0.0, "netProfit": 0.0,
            "financialSettlements": [],
            "sorosNextDay": updated_soros.get("currentDay", 1),
            "sorosNextStake": updated_soros.get("currentStake", 10.0),
            "sorosVaultProfit": updated_soros.get("vaultProfit", 0.0),
        }
    placares = []

    # 1. Formata mensagem do Confere
    msg = notifier.format_confere_message(date_str, audit_summary, placares)

    # 2. Envia para o Telegram
    sent = notifier.send_telegram(msg)
    if not sent:
        print("ℹ️ Notificação Telegram não enviada ou credenciais pendentes.")

    # 3. Executa sincronização com o repositório público
    sync_script = os.path.join(parent_dir, "sync_public.py")
    if os.path.exists(sync_script):
        print("\n🚀 Executando sincronização pública (sync_public.py)...")
        try:
            res = subprocess.run([sys.executable, sync_script], capture_output=True, text=True, check=True)
            print(res.stdout)
        except Exception as e:
            print(f"⚠️ Erro ao sincronizar público: {e}")

    print("\n✅ Pipeline de confere finalizado com sucesso!")
    return True

if __name__ == "__main__":
    run_confere_pipeline()
