"""Durable, append-only pre-match snapshots for the FAS football grade."""

from __future__ import annotations

import copy
import datetime as dt
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


LOCAL_TZ = ZoneInfo("America/Sao_Paulo")
FINAL_STATUSES = {"SETTLED", "AUDITED", "LIQUIDATED", "LIQUIDADO"}


class SnapshotError(ValueError):
    """Raised when a grade cannot be safely frozen as a new snapshot."""


def _canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _atomic_json_write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def _parse_time(value: Any) -> dt.datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed


def _first(mapping: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if mapping.get(key) is not None:
            return mapping[key]
    return None


def _normalize_selection(selection: Any, captured_at: dt.datetime) -> tuple[dict[str, Any], bool]:
    if isinstance(selection, dict):
        kickoff = _first(selection, "kickoff", "startAt", "startTime")
        parsed = _parse_time(kickoff)
        started = bool(parsed and parsed.astimezone(LOCAL_TZ) <= captured_at.astimezone(LOCAL_TZ))
        record = {
            "fixture": _first(selection, "match", "fixture", "event"),
            "kickoff": kickoff,
            "period": _first(selection, "period", "timeframe"),
            "market": _first(selection, "market", "marketName"),
            "side": _first(selection, "side", "selection", "pick"),
            "line": _first(selection, "line", "handicap", "total"),
            "odd": _first(selection, "odd", "odds", "price"),
            "quoteAt": _first(selection, "quoteAt", "oddsAt", "capturedAt"),
            "quoteSource": _first(selection, "quoteSource", "oddsSource", "source"),
            "raw": copy.deepcopy(selection),
        }
        return record, started
    return {
        "fixture": None,
        "kickoff": None,
        "period": None,
        "market": None,
        "side": None,
        "line": None,
        "odd": None,
        "quoteAt": None,
        "quoteSource": None,
        "raw": copy.deepcopy(selection),
    }, False


def _snapshot_tickets(data: dict[str, Any], captured_at: dt.datetime) -> tuple[list[dict[str, Any]], int]:
    source_tickets: list[tuple[str, dict[str, Any]]] = []
    supremo = data.get("supremoTicket")
    if isinstance(supremo, dict) and supremo:
        source_tickets.append(("supremoTicket", supremo))
    for index, ticket in enumerate(data.get("structuredTickets", [])):
        if isinstance(ticket, dict):
            source_tickets.append((f"structuredTickets[{index}]", ticket))
    soros = data.get("sorosTicket")
    if isinstance(soros, dict) and soros:
        source_tickets.append(("sorosTicket", soros))

    tickets: list[dict[str, Any]] = []
    excluded = 0
    for source_key, original in source_tickets:
        ticket = copy.deepcopy(original)
        components: list[tuple[str, Any]] = []
        total_components = 0
        for key in ("selections", "legs"):
            values = ticket.get(key)
            if isinstance(values, list):
                total_components += len(values)
                kept = []
                for item in values:
                    normalized, started = _normalize_selection(item, captured_at)
                    if started:
                        excluded += 1
                    else:
                        kept.append(item)
                        components.append((key, normalized))
                ticket[key] = kept

        stop_points = ticket.get("stopPoints")
        if isinstance(stop_points, list):
            for stop_index, stop in enumerate(stop_points):
                if not isinstance(stop, dict) or not isinstance(stop.get("legs"), list):
                    continue
                total_components += len(stop["legs"])
                kept = []
                for item in stop["legs"]:
                    normalized, started = _normalize_selection(item, captured_at)
                    if started:
                        excluded += 1
                    else:
                        kept.append(item)
                        components.append((f"stopPoints[{stop_index}].legs", normalized))
                stop["legs"] = kept

        if total_components and not components:
            continue

        ticket_record = {
            "sourceKey": source_key,
            "name": ticket.get("name"),
            "type": ticket.get("type"),
            "track": ticket.get("track"),
            "stakeTotal": ticket.get("stake"),
            "components": [entry for _, entry in components],
            "sourceTicket": ticket,
        }
        tickets.append(ticket_record)
    return tickets, excluded


def save_snapshot(
    data: dict[str, Any],
    snapshots_root: str | Path,
    *,
    captured_at: dt.datetime | None = None,
) -> tuple[dict[str, Any], bool]:
    """Save a date-scoped immutable grade. Returns (snapshot, created)."""
    if not isinstance(data, dict):
        raise SnapshotError("A grade precisa ser um objeto JSON.")
    if str(data.get("status", "")).upper() in FINAL_STATUSES:
        raise SnapshotError("A grade já está liquidada; snapshot pré-jogo recusado.")

    date_value = data.get("date")
    try:
        date_value = dt.date.fromisoformat(date_value).isoformat()
    except (TypeError, ValueError):
        raise SnapshotError("A grade precisa de date no formato YYYY-MM-DD.") from None

    captured = captured_at or dt.datetime.now(LOCAL_TZ)
    if captured.tzinfo is None:
        raise SnapshotError("captured_at precisa incluir fuso horário.")
    captured = captured.astimezone(LOCAL_TZ).replace(microsecond=0)
    snapshot_id = data.get("snapshotId")
    if not isinstance(snapshot_id, str) or not snapshot_id.strip():
        raise SnapshotError("A grade precisa de snapshotId explícito para impedir sobrescrita de versões.")
    if not re.fullmatch(r"[A-Za-z0-9._-]+", snapshot_id) or snapshot_id in {".", ".."}:
        raise SnapshotError("snapshotId contém caracteres inválidos para um arquivo de snapshot.")

    root = Path(snapshots_root) / date_value
    manifest_path = root / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        manifest = {"date": date_value, "latestSnapshotId": None, "snapshots": []}

    content_hash = hashlib.sha256(_canonical_json(data)).hexdigest()
    existing_entry = next((entry for entry in manifest["snapshots"] if entry["snapshotId"] == snapshot_id), None)
    target_path = root / f"{snapshot_id}.json"
    if existing_entry:
        if existing_entry.get("sourceHash") != content_hash:
            raise SnapshotError(f"snapshotId {snapshot_id} já existe com conteúdo diferente; use uma nova versão.")
        return json.loads(target_path.read_text(encoding="utf-8")), False

    previous_id = manifest.get("latestSnapshotId")
    tickets, excluded = _snapshot_tickets(data, captured)
    metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
    snapshot = {
        "schemaVersion": 1,
        "metadata": {
            "date": date_value,
            "snapshotId": snapshot_id,
            "methodologyVersion": _first(data, "methodologyVersion") or metadata.get("methodologyVersion") or "unknown",
            "track": _first(data, "track") or metadata.get("track") or "unknown",
            "capturedAt": captured.isoformat(),
            "previousSnapshotId": previous_id,
            "changeReason": _first(data, "changeReason") or metadata.get("changeReason") or "unknown",
            "timezone": "America/Sao_Paulo",
        },
        "sourceHash": content_hash,
        "excludedStartedSelections": excluded,
        "tickets": tickets,
        "sourceGradeMetadata": {
            key: copy.deepcopy(value)
            for key, value in data.items()
            if key not in {"supremoTicket", "structuredTickets", "sorosTicket"}
        },
    }

    _atomic_json_write(target_path, snapshot)
    updated_manifest = copy.deepcopy(manifest)
    updated_manifest["snapshots"].append({"snapshotId": snapshot_id, "sourceHash": content_hash})
    updated_manifest["latestSnapshotId"] = snapshot_id
    _atomic_json_write(manifest_path, updated_manifest)
    return snapshot, True
