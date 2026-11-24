"""Acceptance cases for executable FAS V7.5 conformity gates."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from conformity_validator import validate_grade


HERE = Path(__file__).resolve().parent


class ConformityValidatorTests(unittest.TestCase):
    def test_2026_11_23_track_b_historical_acceptance_findings(self):
        grade = json.loads((HERE / "fixtures" / "compliance_2026-11-23_track_b.json").read_text(encoding="utf-8"))
        report = validate_grade(grade)
        rules = {item["rule"] for item in report["violations"]}
        self.assertEqual(report["status"], "NON_COMPLIANT")
        self.assertFalse(report["complianceSeal"])
        self.assertTrue({"short_slate_secondary_ticket", "improvavel_system_format", "safe_stop2_dnb",
                         "exposure_cap_fixture", "exposure_cap_team"}.issubset(rules))
        team_counts = report["tracks"]["B"]["teamTicketCounts"]
        self.assertEqual(team_counts["internacional"], 3)
        self.assertEqual(team_counts["botafogo"], 3)
        self.assertEqual(team_counts["santos"], 3)
        inter_exposure = next(item for item in report["violations"]
                              if item["rule"] == "exposure_cap_fixture" and item["item"] == "internacional x vitoria")
        self.assertEqual(inter_exposure["stakeInvolved"], 26.0)
        inter_details = report["tracks"]["B"]["sharedFixtureDetails"]["internacional x vitoria"]
        improbable_share = next(item for item in inter_details["internalCombinationExposure"]
                                if "Improvável" in item["ticket"])
        self.assertEqual(improbable_share["combinationCount"], 21)
        self.assertEqual(improbable_share["combinationsContainingFixture"], 15)
        self.assertEqual(improbable_share["stakeExposedToFixtureEstimated"], 0.7143)
        self.assertEqual(report["tracks"]["B"]["stakeTotal"], 64.8)
        self.assertTrue(report["tracks"]["B"]["sorosIsolation"]["differentFromSupremo"])
        self.assertTrue(report["tracks"]["B"]["sorosIsolation"]["differentFromSafeAnchor"])
        self.assertFalse(report["tracks"]["B"]["sorosIsolation"]["exclusiveInTrack"])
        self.assertTrue(any("mercados diferentes não comprovam" in item for item in report["review"]))

    def test_track_stake_labels_keep_theoretical_and_operational_values_separate(self):
        grade = json.loads((HERE / "fixtures" / "compliance_2026-11-23_track_b.json").read_text(encoding="utf-8"))
        grade["track"] = "TRILHA_A_MATINAL"
        grade["structuredTickets"].append({
            "name": "SAFE A", "type": "SAFE", "track": "TRILHA_A_MATINAL", "stake": 5,
            "stopPoints": [
                {"level": "Stop Point 1", "legs": ["Alpha FC x Beta FC: Alpha 1X"]},
                {"level": "Stop Point 2", "legs": ["Alpha FC x Beta FC: Alpha DNB"]}
            ]
        })
        report = validate_grade(grade)
        self.assertEqual(report["tracks"]["A"]["stakeNature"], "THEORETICAL_MODEL")
        self.assertIsNone(report["tracks"]["A"]["operationalStakeTotal"])
        self.assertEqual(report["tracks"]["B"]["stakeNature"], "OPERATIONAL_DECLARATION")

    def test_valid_full_grade_with_independent_soros_and_dnb_safe(self):
        quality_fixtures = [
            {"fixtureKey": f"team-{index}", "date": "2026-11-24",
             "competition": "Brasileirão Série A" if index < 3 else "Premier League"}
            for index in range(10)
        ]
        grade = {
            "date": "2026-11-24",
            "snapshotId": "VALID_V1",
            "track": "TRILHA_B_OPERACIONAL",
            "qualityFixtureCount": 10,
            "qualityFixtures": quality_fixtures,
            "supremoTicket": {"name": "Supremo", "stake": 5, "selections": [
                {"match": "Alpha FC x Beta FC", "market": "1X", "odd": 1.2}
            ]},
            "structuredTickets": [{
                "name": "SAFE", "type": "SAFE", "stake": 4,
                "stopPoints": [
                    {"level": "Stop Point 1", "legs": ["Gamma FC x Delta FC: Gamma 1X"]},
                    {"level": "Stop Point 2", "legs": ["Gamma FC x Delta FC: Gamma DNB"]}
                ]
            }],
            "sorosTicket": {"name": "Desafio Soros", "type": "SOROS", "stake": 2,
                            "legs": ["Epsilon FC x Zeta FC: Epsilon vence"]}
        }
        report = validate_grade(grade)
        self.assertEqual(report["status"], "COMPLIANT")
        self.assertTrue(report["canPublish"])
        self.assertTrue(report["complianceSeal"])

    def test_full_slate_brazil_trigger_requires_the_round_ticket(self):
        fixtures = [
            {"fixtureKey": f"br-{index}", "date": "2026-11-24", "competition": "Brasileirão Série A"}
            for index in range(4)
        ] + [{"fixtureKey": f"other-{index}", "date": "2026-11-24", "competition": "Premier League"}
             for index in range(6)]
        grade = {
            "date": "2026-11-24", "qualityFixtureCount": 10, "qualityFixtures": fixtures,
            "supremoTicket": {"name": "Supremo", "selections": []},
            "structuredTickets": [], "sorosTicket": {},
        }
        report = validate_grade(grade)
        self.assertIn("brazil_round_ticket_missing", {item["rule"] for item in report["violations"]})

    def test_empty_grade_is_a_no_bet_case(self):
        report = validate_grade({"date": "2026-11-24", "snapshotId": "EMPTY"})
        self.assertEqual(report["status"], "NO_BET")
        self.assertTrue(report["canPublish"])
        self.assertFalse(report["complianceSeal"])
        self.assertEqual(report["violations"], [])

    def test_short_slate_boundary_is_nine_inclusive_and_ten_is_full(self):
        for count, expected in ((9, True), (10, False)):
            grade = {
                "qualityFixtureCount": count,
                "supremoTicket": {"name": "Supremo", "selections": []},
                "structuredTickets": [],
                "sorosTicket": {},
            }
            self.assertEqual(validate_grade(grade)["shortSlate"], expected)

    def test_2026_11_21_soros_and_attack_share_palmeiras_flamengo(self):
        grade = {
            "qualityFixtureCount": 10,
            "supremoTicket": {"name": "Supremo", "stake": 25, "selections": [
                {"match": "Newcastle x Arsenal", "market": "Arsenal X2"}
            ]},
            "structuredTickets": [{
                "name": "SAFE", "type": "SAFE", "stake": 15,
                "stopPoints": [
                    {"level": "Stop Point 1", "legs": ["Sevilla x Real Betis: Under 3.5", "Napoli x Torino: Napoli 1X"]},
                    {"level": "Stop Point 2", "legs": ["Sevilla x Real Betis: Under 3.5", "Napoli x Torino: Napoli DNB"]}
                ]
            }, {
                "name": "Super Ataque", "type": "ATTACK", "stake": 5,
                "legs": ["Palmeiras x Flamengo: Ambos Marcam Sim"]
            }],
            "sorosTicket": {"name": "Desafio Soros", "type": "SOROS", "stake": 10,
                            "legs": ["Palmeiras x Flamengo: Mais de 1.5 Gols"]}
        }
        report = validate_grade(grade)
        details = report["tracks"]["DEFAULT"]["sharedFixtureDetails"]["palmeiras x flamengo"]
        self.assertEqual(set(details["tickets"]), {"Super Ataque", "Desafio Soros"})
        self.assertEqual(details["stakeInvolved"], 15)
        self.assertFalse(report["tracks"]["DEFAULT"]["sorosIsolation"]["exclusiveInTrack"])
        self.assertTrue(any("palmeiras x flamengo" in line for line in report["review"]))

    def test_definite_violation_blocks_morning_notification(self):
        import fas_engine
        import notifier

        grade = json.loads((HERE / "fixtures" / "compliance_2026-11-23_track_b.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "bilhetes_ativos.json").write_text(json.dumps(grade), encoding="utf-8")
            with mock.patch.object(fas_engine, "current_dir", str(root)), \
                    mock.patch.object(fas_engine, "parent_dir", str(root / "no-sync")), \
                    mock.patch.object(notifier, "format_grade_message") as format_message, \
                    mock.patch.object(notifier, "send_telegram") as send_message:
                self.assertFalse(fas_engine.run_morning_pipeline())
            format_message.assert_not_called()
            send_message.assert_not_called()
            self.assertFalse((root / "snapshots").exists())


if __name__ == "__main__":
    unittest.main()
