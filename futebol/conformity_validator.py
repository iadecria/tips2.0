"""Conservative, track-aware implementation of FAS V7.5 grade rules."""

from __future__ import annotations

import re
import unicodedata
import math
from collections import defaultdict
from typing import Any


SYSTEM_FORMATS = {(6, 8), (7, 8)}
SHORT_SLATE_LIMIT = 10


def _key(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return " ".join(value.casefold().split())


def _split_fixture(value: Any) -> tuple[str | None, str | None, str | None]:
    if not isinstance(value, str):
        return None, None, None
    text = value.strip()
    text = re.split(r"\s+[—–]\s+", text, maxsplit=1)[0].strip()
    text = re.sub(r"\s*\([^)]*\)\s*$", "", text).strip()
    score = re.search(r"^(.+?)\s+\d+\s*[x×]\s*\d+\s+(.+?)(?:\s+[—–-]\s+|$)", text, re.IGNORECASE)
    if score:
        home, away = score.group(1).strip(), score.group(2).strip()
        return f"{home} x {away}", _key(home), _key(away)
    if ":" in text:
        text = text.split(":", 1)[0].strip()
    parts = re.split(r"\s+(?:x|×|vs\.?)\s+", text, maxsplit=1, flags=re.IGNORECASE)
    if len(parts) != 2 or not all(part.strip() for part in parts):
        return None, None, None
    home, away = (part.strip() for part in parts)
    return f"{home} x {away}", _key(home), _key(away)


def _selection(raw: Any) -> dict[str, Any]:
    if isinstance(raw, dict):
        fixture_value = raw.get("match") or raw.get("fixture") or raw.get("event")
        parsed, home, away = _split_fixture(fixture_value)
        market = raw.get("market") or raw.get("marketName")
        kickoff = raw.get("kickoff") or raw.get("startAt") or raw.get("startTime")
        return {
            "fixture": parsed,
            "fixtureKey": _key(parsed) if parsed else None,
            "home": home,
            "away": away,
            "market": str(market) if market is not None else None,
            "kickoff": kickoff,
            "raw": raw,
        }
    value = raw
    if isinstance(value, str):
        value = re.sub(r"^.*?TRILHA\s+[AB][^:]*:\s*", "", value, count=1, flags=re.IGNORECASE)
    parsed, home, away = _split_fixture(value)
    if isinstance(value, str) and ":" in value:
        market = value.split(":", 1)[1].strip()
    elif isinstance(value, str) and re.search(r"\s+[—–]\s+", value):
        market = re.split(r"\s+[—–]\s+", value, maxsplit=1)[1].strip()
    else:
        market = None
    return {
        "fixture": parsed,
        "fixtureKey": _key(parsed) if parsed else None,
        "home": home,
        "away": away,
        "market": market,
        "kickoff": None,
        "raw": raw,
    }


def _track_tag(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    match = re.search(r"(?:TRILHA|TRACK)[ _-]*([AB])(?![A-Za-z0-9])", value, re.IGNORECASE)
    return match.group(1).upper() if match else None


def _ticket_records(data: dict[str, Any], track: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    declared_tracks = {
        tag for ticket in data.get("structuredTickets", []) if isinstance(ticket, dict)
        for tag in [_track_tag(ticket.get("track"))] if tag
    }
    dual_track = {"A", "B"}.issubset(declared_tracks)

    def add(source_id: str, ticket: dict[str, Any], selections: list[Any] | None = None):
        if ticket.get("informationalOnly") is True or (
            str(ticket.get("type", "")).upper() == "RODADA" and ticket.get("stake") == 0
        ):
            return
        raw_items = selections
        if raw_items is None:
            raw_items = []
            for name in ("selections", "legs"):
                value = ticket.get(name)
                if isinstance(value, list):
                    raw_items.extend(value)
            for stop in ticket.get("stopPoints", []) if isinstance(ticket.get("stopPoints"), list) else []:
                if isinstance(stop, dict) and isinstance(stop.get("legs"), list):
                    raw_items.extend(stop["legs"])
        parsed = [_selection(item) for item in raw_items]
        unique = {}
        for selection in parsed:
            if selection["fixtureKey"]:
                unique.setdefault(selection["fixtureKey"], selection)
        records.append({
            "id": source_id,
            "name": ticket.get("name", source_id),
            "type": str(ticket.get("type", "")).upper(),
            "track": track,
            "stake": ticket.get("stake"),
            "selections": parsed,
            "fixtures": unique,
            "source": ticket,
        })

    supremo = data.get("supremoTicket")
    if isinstance(supremo, dict) and supremo:
        add("supremoTicket", supremo)

    for index, ticket in enumerate(data.get("structuredTickets", [])):
        if not isinstance(ticket, dict):
            continue
        declared_track = _track_tag(ticket.get("track"))
        if declared_track and declared_track != track:
            continue
        add(f"structuredTickets[{index}]", ticket)

    soros = data.get("sorosTicket")
    if isinstance(soros, dict) and soros:
        items = soros.get("legs") if isinstance(soros.get("legs"), list) else []
        tagged = [(item, _track_tag(item)) for item in items]
        if any(tag for _, tag in tagged):
            selected_items = [item for item, tag in tagged if tag in (None, track)]
            if selected_items:
                add(f"sorosTicket:{track}", soros, selected_items)
        else:
            declared_track = _track_tag(soros.get("track"))
            root_track = _track_tag(data.get("track"))
            if declared_track == track or (not declared_track and root_track == track) or (not dual_track and not declared_track):
                add("sorosTicket", soros)
    return records


def _is_safe(ticket: dict[str, Any]) -> bool:
    return ticket["type"] == "SAFE" or "SAFE" in str(ticket["name"]).upper()


def _is_soros(ticket: dict[str, Any]) -> bool:
    return ticket["type"] == "SOROS" or "SOROS" in str(ticket["name"]).upper()


def _is_supremo(ticket: dict[str, Any]) -> bool:
    return ticket["id"] == "supremoTicket" or "SUPREMO" in str(ticket["name"]).upper()


def _is_secondary(ticket: dict[str, Any]) -> bool:
    name = _key(str(ticket["name"]))
    typ = ticket["type"]
    return (
        typ in {"ATTACK", "SAFE_PLUS", "SAFE+", "RODADA", "IMPROVAVEL", "NETO"}
        or any(term in name for term in ("ataque", "safe+", "improvavel", "brasileirao", "rodada", "aposentar o neto"))
    )


def _system_shape(ticket: dict[str, Any]) -> tuple[int, int] | None:
    source = ticket["source"]
    system = source.get("system")
    if isinstance(system, str):
        match = re.search(r"(\d+)\s*/\s*(\d+)", system)
        if match:
            return int(match.group(1)), int(match.group(2))
    text = f"{ticket['name']} {source.get('format', '')}"
    match = re.search(r"(\d+)\s*/\s*(\d+)", text)
    return (int(match.group(1)), int(match.group(2))) if match else None


def _combination_exposure(ticket: dict[str, Any], fixture_key: str | None = None) -> dict[str, Any]:
    system = _system_shape(ticket)
    stake = ticket["stake"] if isinstance(ticket["stake"], (int, float)) else None
    if system and system[0] <= system[1] and system[1] > 0:
        combinations = math.comb(system[1], system[0])
        containing = math.comb(system[1] - 1, system[0] - 1) if fixture_key and fixture_key in ticket["fixtures"] else combinations
        per_combination = stake / combinations if stake is not None else None
        exposed = per_combination * containing if per_combination is not None else None
        return {
            "ticket": ticket["name"],
            "system": f"{system[0]}/{system[1]}",
            "combinationCount": combinations,
            "combinationsContainingFixture": containing if fixture_key else None,
            "stakeTotal": stake,
            "stakePerCombinationEstimated": round(per_combination, 4) if per_combination is not None else None,
            "stakeExposedToFixtureEstimated": round(exposed, 4) if exposed is not None else None,
            "allocationAssumption": "divisão igual da stake pelas combinações; estimativa, validar recibo/regra da casa",
        }
    return {
        "ticket": ticket["name"],
        "system": None,
        "combinationCount": 1,
        "combinationsContainingFixture": 1 if fixture_key else None,
        "stakeTotal": stake,
        "stakePerCombinationEstimated": stake,
        "stakeExposedToFixtureEstimated": stake if fixture_key else None,
        "allocationAssumption": "stake integral do bilhete acumulado; não representa retorno",
    }


def _market_family(market: str | None) -> str | None:
    if not market:
        return None
    text = _key(market)
    if any(term in text for term in ("escanteir", "corner", "canto")):
        return "corners"
    if any(term in text for term in ("gol", "over", "under", "btts", "ambos marcam")):
        return "goals"
    if any(term in text for term in ("dupla chance", "1x", "x2", "dnb", "handicap", "moneyline", "vence", "v1", "v2", "w1", "w2")):
        return "result"
    return None


def _short_slate(data: dict[str, Any]) -> tuple[bool | None, list[str]]:
    review: list[str] = []
    metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
    gate = data.get("validation") if isinstance(data.get("validation"), dict) else {}
    count = gate.get("qualityFixtureCount", metadata.get("qualityFixtureCount", data.get("qualityFixtureCount")))
    fixtures = gate.get("qualityFixtures", metadata.get("qualityFixtures", data.get("qualityFixtures")))
    declared = gate.get("shortSlateDeclared", metadata.get("shortSlateDeclared", data.get("shortSlateDeclared")))
    if count is None and isinstance(fixtures, list):
        identities = {str(item.get("fixtureKey") or item.get("match") or item.get("fixture"))
                      for item in fixtures if isinstance(item, dict) and (item.get("fixtureKey") or item.get("match") or item.get("fixture"))}
        count = len(identities)
    if isinstance(count, int) and not isinstance(count, bool) and count >= 0:
        calculated = count < SHORT_SLATE_LIMIT
        if isinstance(fixtures, list):
            listed = {str(item.get("fixtureKey") or item.get("match") or item.get("fixture"))
                      for item in fixtures if isinstance(item, dict) and (item.get("fixtureKey") or item.get("match") or item.get("fixture"))}
            if len(listed) != count:
                review.append(f"qualityFixtureCount={count} difere de {len(listed)} fixtures qualificadas listadas.")
        if isinstance(declared, bool) and declared != calculated:
            review.append(f"shortSlateDeclared diverge de qualityFixtureCount={count}; aplicar o limite V7.5 (<{SHORT_SLATE_LIMIT}) e revisar a declaração.")
        return calculated, review
    if isinstance(declared, bool):
        review.append("qualityFixtureCount ausente; a grade curta foi considerada conforme a declaração explícita, mas o limiar não pôde ser verificado.")
        return declared, review
    review.append("qualityFixtureCount/shortSlateDeclared ausente; classificação de grade curta requer revisão.")
    return None, review


def _brazil_quality_fixture_count(data: dict[str, Any]) -> int | None:
    metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
    gate = data.get("validation") if isinstance(data.get("validation"), dict) else {}
    fixtures = gate.get("qualityFixtures", metadata.get("qualityFixtures", data.get("qualityFixtures")))
    if not isinstance(fixtures, list):
        return None
    target_date = data.get("date")
    matches = set()
    for fixture in fixtures:
        if not isinstance(fixture, dict) or fixture.get("date", target_date) != target_date:
            continue
        competition = _key(str(fixture.get("competition", "")))
        is_brazil = any(term in competition for term in ("brasileirao", "serie a brasil", "serie b brasil", "campeonato brasileiro"))
        identifier = fixture.get("fixtureKey") or fixture.get("match") or fixture.get("fixture")
        if is_brazil and identifier:
            matches.add(str(identifier))
    return len(matches)


def validate_grade(data: dict[str, Any]) -> dict[str, Any]:
    """Return a local compliance report. Definite violations block publication."""
    if not isinstance(data, dict):
        return {"status": "NON_COMPLIANT", "canPublish": False, "complianceSeal": False,
                "violations": [{"rule": "grade_object", "message": "A grade precisa ser um objeto."}], "review": []}

    tracks = sorted({tag for ticket in data.get("structuredTickets", []) if isinstance(ticket, dict)
                     for tag in [_track_tag(ticket.get("track"))] if tag})
    if len(tracks) < 2:
        tracks = [_track_tag(data.get("track")) or "DEFAULT"]
    violations: list[dict[str, Any]] = []
    review: list[str] = []
    by_track: dict[str, Any] = {}

    if not data.get("supremoTicket") and not data.get("structuredTickets") and not data.get("sorosTicket"):
        return {"status": "NO_BET", "canPublish": True, "complianceSeal": False,
                "tracks": {}, "violations": [], "review": []}

    short, short_review = _short_slate(data)
    review.extend(short_review)
    soros = data.get("sorosTicket")
    soros_legs = soros.get("legs", []) if isinstance(soros, dict) and isinstance(soros.get("legs"), list) else []
    dual_soros_tags = {_track_tag(item) for item in soros_legs if _track_tag(item)}
    if len(tracks) > 1 and len(dual_soros_tags) < 2 and not _track_tag(data.get("track")):
        if isinstance(soros, dict) and soros_legs and not _track_tag(soros.get("track")):
            review.append("Grade possui trilhas A/B, mas o Soros não declara trilha por perna; stake e exposição do Soros requerem revisão.")
    brazil_fixture_count = _brazil_quality_fixture_count(data)
    if short is False and brazil_fixture_count is None:
        review.append("qualityFixtures sem competição/data; não foi possível verificar o gatilho >3 do Brasileirão no dia.")
    all_ticket_records: dict[str, list[dict[str, Any]]] = {}

    for track in tracks:
        tickets = _ticket_records(data, track)
        all_ticket_records[track] = tickets
        track_violations: list[dict[str, Any]] = []
        track_review: list[str] = []

        if short is True:
            secondary = [ticket for ticket in tickets if _is_secondary(ticket)]
            if secondary:
                ticket_names = [ticket["name"] for ticket in secondary]
                stake_known = all(isinstance(ticket["stake"], (int, float)) for ticket in secondary)
                track_violations.append({
                    "rule": "short_slate_secondary_ticket",
                    "tickets": ticket_names,
                    "stakeInvolved": round(sum(ticket["stake"] for ticket in secondary), 2) if stake_known else None,
                    "internalCombinationExposure": [_combination_exposure(ticket) for ticket in secondary],
                    "message": "Em grade curta, bilhetes secundários (incluindo uma múltipla própria do Brasileirão) ficam suspensos; FAS Rodada pode permanecer apenas como scanner informativo.",
                })
        elif short is False and brazil_fixture_count is not None and brazil_fixture_count > 3:
            has_brazil_ticket = any(
                (ticket["type"] == "RODADA" or "BRASILEIRAO" in _key(str(ticket["name"])))
                and ticket["source"].get("informationalOnly") is not True
                and ticket["stake"] != 0
                for ticket in tickets
            )
            if not has_brazil_ticket:
                track_violations.append({
                    "rule": "brazil_round_ticket_missing",
                    "tickets": [],
                    "stakeInvolved": 0.0,
                    "message": f"Há {brazil_fixture_count} fixtures qualificados do Brasileirão no dia (gatilho >3) e falta a múltipla da rodada; grade cheia.",
                })

        for ticket in tickets:
            system = _system_shape(ticket)
            if _key(str(ticket["name"])).find("improvavel") >= 0 or "IMPROVAVEL" in ticket["type"]:
                count = len(ticket["selections"])
                if system is None:
                    track_review.append(f"{ticket['name']}: formato de sistema não declarado; não é possível validar a grade.")
                elif system not in SYSTEM_FORMATS or count != system[1]:
                    track_violations.append({
                        "rule": "improvavel_system_format",
                        "tickets": [ticket["name"]],
                        "stakeInvolved": ticket["stake"],
                        "message": f"Formato Sistema {system[0]}/{system[1]} com {count} seleções; V7.5 permite 6/8 ou 7/8 com oito seleções.",
                        "internalCombinationExposure": _combination_exposure(ticket),
                    })

            if _is_safe(ticket):
                stops = ticket["source"].get("stopPoints", [])
                stop2 = next((stop for stop in stops if isinstance(stop, dict) and "stop point 2" in _key(str(stop.get("level", "")))), None)
                if stop2 is None:
                    track_review.append(f"{ticket['name']}: Stop Point 2 não está estruturado; proteção DNB requer revisão.")
                else:
                    legs = stop2.get("legs", []) if isinstance(stop2.get("legs"), list) else []
                    dnb = any(re.search(r"\bDNB\b|DRAW[_ -]?NO[_ -]?BET|HANDICAP[^\n]*\(\s*0(?:\.0)?\s*\)", str(leg), re.IGNORECASE)
                              or (isinstance(leg, dict) and str(leg.get("market", "")).upper() in {"DNB", "DRAW_NO_BET"})
                              for leg in legs)
                    if not dnb:
                        track_violations.append({
                            "rule": "safe_stop2_dnb",
                            "tickets": [ticket["name"]],
                            "stakeInvolved": ticket["stake"],
                            "message": "SAFE Stop Point 2 não declara proteção DNB/Handicap 0.",
                        })

        fixture_tickets: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
        team_tickets: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
        shared_fixture_details: dict[str, dict[str, Any]] = {}
        for ticket in tickets:
            for fixture_key, selection in ticket["fixtures"].items():
                fixture_tickets[fixture_key][ticket["id"]] = ticket
                for team in (selection["home"], selection["away"]):
                    if team:
                        team_tickets[team][ticket["id"]] = ticket
            if any(not item["fixtureKey"] for item in ticket["selections"]):
                track_review.append(f"{ticket['name']}: uma ou mais seleções não identificam a partida; exposição não pôde ser contada para todas as pernas.")

        def add_exposure_violation(rule: str, key: str, affected: dict[str, dict[str, Any]]):
            items = list(affected.values())
            known = all(isinstance(ticket["stake"], (int, float)) for ticket in items)
            track_violations.append({
                "rule": rule,
                "item": key,
                "tickets": [ticket["name"] for ticket in items],
                "stakeInvolved": round(sum(ticket["stake"] for ticket in items), 2) if known else None,
                "message": f"Exposição em {key}: consta em {len(items)} bilhetes (limite V7.5: 2).",
            })

        for fixture_key, affected in fixture_tickets.items():
            if len(affected) > 2:
                add_exposure_violation("exposure_cap_fixture", fixture_key, affected)
            if len(affected) > 1:
                selections = []
                for ticket in affected.values():
                    selections.extend(item for item in ticket["selections"] if item["fixtureKey"] == fixture_key)
                families = {_market_family(item["market"]) for item in selections}
                families.discard(None)
                stake_known = all(isinstance(ticket["stake"], (int, float)) for ticket in affected.values())
                shared_fixture_details[fixture_key] = {
                    "tickets": [ticket["name"] for ticket in affected.values()],
                    "stakeInvolved": round(sum(ticket["stake"] for ticket in affected.values()), 2) if stake_known else None,
                    "marketFamilies": sorted(families),
                    "independenceDemonstrated": "corners" in families and len(families) > 1,
                    "internalCombinationExposure": [_combination_exposure(ticket, fixture_key) for ticket in affected.values()],
                }
                if "corners" in families and len(families) > 1:
                    continue  # Explicit independence example in methodology V7.5.
                track_review.append(f"Fixture {fixture_key} aparece em {len(affected)} bilhetes; mercados diferentes não comprovam independência estatística.")

        for team, affected in team_tickets.items():
            if len(affected) > 2:
                add_exposure_violation("exposure_cap_team", team, affected)

        supremo_fixtures = set()
        safe_anchor_fixtures = set()
        soros_fixtures: dict[str, dict[str, Any]] = {}
        for ticket in tickets:
            if _is_supremo(ticket):
                supremo_fixtures.update(ticket["fixtures"])
            if _is_safe(ticket):
                stops = ticket["source"].get("stopPoints", [])
                if stops and isinstance(stops[0], dict):
                    anchor_items = stops[0].get("legs", [])
                    safe_anchor_fixtures.update(item["fixtureKey"] for item in map(_selection, anchor_items) if item["fixtureKey"])
                elif ticket["source"].get("anchorFixture"):
                    parsed, _, _ = _split_fixture(ticket["source"]["anchorFixture"])
                    if parsed:
                        safe_anchor_fixtures.add(_key(parsed))
                else:
                    track_review.append(f"{ticket['name']}: âncora da SAFE não está identificável; isolamento do Soros requer revisão.")
            if _is_soros(ticket):
                soros_fixtures.update(ticket["fixtures"])

        soros_hits_supremo = sorted(set(soros_fixtures) & supremo_fixtures)
        soros_hits_anchor = sorted(set(soros_fixtures) & safe_anchor_fixtures)
        if soros_hits_supremo or soros_hits_anchor:
            affected_soros = [ticket for ticket in tickets if _is_soros(ticket)]
            affected_reference = [ticket for ticket in tickets if _is_supremo(ticket) or _is_safe(ticket)]
            affected = {ticket["id"]: ticket for ticket in affected_soros + affected_reference}
            known = all(isinstance(ticket["stake"], (int, float)) for ticket in affected.values())
            track_violations.append({
                "rule": "soros_isolation",
                "fixtures": sorted(set(soros_hits_supremo + soros_hits_anchor)),
                "tickets": [ticket["name"] for ticket in tickets if _is_soros(ticket) or _is_supremo(ticket) or _is_safe(ticket)],
                "stakeInvolved": round(sum(ticket["stake"] for ticket in affected.values()), 2) if known else None,
                "message": "Seleção do Soros coincide com fixture do Supremo ou âncora da SAFE.",
            })

        soros_all = set(soros_fixtures)
        soros_other = set().union(*(set(ticket["fixtures"]) for ticket in tickets if not _is_soros(ticket))) if tickets else set()
        labels = [str(ticket.get("track", "")) for ticket in data.get("structuredTickets", [])
                  if isinstance(ticket, dict) and _track_tag(ticket.get("track")) == track]
        labels.append(str(data.get("track", "")))
        if track == "A" and any("MATINAL" in label.upper() for label in labels):
            stake_nature = "THEORETICAL_MODEL"
        elif track == "B" and any("OPERACIONAL" in label.upper() for label in labels):
            stake_nature = "OPERATIONAL_DECLARATION"
        else:
            stake_nature = "UNKNOWN"
        declared_stake = round(sum(ticket["stake"] for ticket in tickets if isinstance(ticket["stake"], (int, float))), 2)
        unknown_stakes = [ticket["name"] for ticket in tickets if not isinstance(ticket["stake"], (int, float))]
        if unknown_stakes:
            track_review.append(f"Stake declarada ausente em: {', '.join(unknown_stakes)}.")
        if stake_nature == "UNKNOWN":
            track_review.append("Natureza da trilha (operacional/modelo) não está declarada; stake permanece apenas declarada.")
        by_track[track] = {
            "ticketCount": len(tickets),
            "declaredStakeTotal": declared_stake,
            "stakeNature": stake_nature,
            "operationalStakeTotal": declared_stake if stake_nature == "OPERATIONAL_DECLARATION" else None,
            "stakeTotal": declared_stake,
            "stakeUnknownTickets": unknown_stakes,
            "fixtureTicketCounts": {key: len(value) for key, value in sorted(fixture_tickets.items())},
            "sharedFixtureDetails": shared_fixture_details,
            "teamTicketCounts": {key: len(value) for key, value in sorted(team_tickets.items())},
            "sorosIsolation": {
                "differentFromSupremo": not bool(soros_hits_supremo),
                "differentFromSafeAnchor": not bool(soros_hits_anchor),
                "exclusiveInTrack": not bool(soros_all & soros_other),
            },
            "violations": track_violations,
            "review": track_review,
        }
        violations.extend({**item, "track": track} for item in track_violations)
        review.extend(f"{track}: {item}" for item in track_review)

    if violations:
        status = "NON_COMPLIANT"
    elif review:
        status = "REVIEW"
    else:
        status = "COMPLIANT"
    return {
        "status": status,
        "canPublish": not bool(violations),
        "complianceSeal": status == "COMPLIANT",
        "shortSlate": short,
        "shortSlateLimit": SHORT_SLATE_LIMIT,
        "brazilQualifiedFixturesForDay": brazil_fixture_count,
        "systemFormatsAllowed": ["6/8", "7/8"],
        "tracks": by_track,
        "violations": violations,
        "review": review,
    }
