"""Regression tests for central FAS ticket settlement math."""

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from confere_engine import reconcile_financials
import confere_engine
from notifier import format_confere_message
from settlement_engine import apply_soros_settlement, recalculate_odds, settle_ticket


class SettlementEngineTests(unittest.TestCase):
    @staticmethod
    def leg(status, *, fixture=None, period=None, date=None):
        return {"status": status, "evidence": {
            "status": status, "fixture": fixture, "period": period, "date": date,
            "source": "local verified fixture", "retrievedAt": "2026-11-21T22:00:00-03:00",
            "score": "1-0",
        }}

    def test_single_and_accumulator_with_void(self):
        single = settle_ticket({"stake": 10, "legs": [{"odd": 1.2, "status": "HIT"}]})
        self.assertEqual(single["status"], "HIT")
        self.assertEqual(single["grossReturn"], 12.0)
        self.assertEqual(single["netResult"], 2.0)
        self.assertIsNone(single["actualGrossReturn"])
        self.assertIn("ESTIMATE", single["returnEvidence"])

        lost = settle_ticket({"stake": 10, "legs": [
            {"odd": 1.2, "status": "VOID", "market": "DNB"},
            {"odd": 1.5, "status": "MISS"},
        ]})
        self.assertEqual((lost["status"], lost["grossReturn"], lost["netResult"]), ("MISS", 0.0, -10.0))

        void_and_win = settle_ticket({"stake": 10, "legs": [
            {"odd": 1.2, "status": "VOID", "market": "DNB"},
            {"odd": 1.5, "status": "HIT"},
        ]})
        self.assertEqual((void_and_win["grossReturn"], void_and_win["netResult"]), (15.0, 5.0))

    def test_stop_products_and_safe_b_odd_mismatch(self):
        stop_ticket = {"stake": 10, "stopPoints": [
            {"level": "Stop Point 1", "multiplier": 1.76, "legs": [
                {"odd": 1.25, "status": "HIT"}, {"odd": 1.15, "status": "HIT"}, {"odd": 1.14, "status": "HIT"}
            ]},
            {"level": "Stop Point 2", "multiplier": 2.72, "legs": [
                {"odd": 1.25, "status": "HIT"}, {"odd": 1.14, "status": "HIT"}, {"odd": 1.22, "status": "HIT"}
            ]},
        ]}
        result = settle_ticket(stop_ticket)
        self.assertEqual(result["status"], "PENDING")
        self.assertEqual(result["grossReturn"], None)
        self.assertEqual([variant["oddsAudit"]["calculatedOdd"] for variant in result["stopVariants"]], [1.64, 1.74])
        self.assertEqual([variant["oddsAudit"]["publishedOdd"] for variant in result["stopVariants"]], [1.76, 2.72])

        safe_b = recalculate_odds([
            {"odd": 1.22}, {"odd": 1.22}, {"odd": 1.35}
        ], published_odd=1.82)
        self.assertEqual(safe_b["calculatedOdd"], 2.01)
        self.assertTrue(safe_b["mismatch"])

    def test_system_6_of_8_and_5_of_7(self):
        winning_odds = [1.18, 1.25, 1.15, 1.38, 1.40, 1.30]
        fixtures = ["newcastle-arsenal", "sevilla-betis", "napoli-torino", "palmeiras-flamengo",
                    "real-madrid-celta", "real-madrid-celta", "bahia-coritiba", "schalke-stuttgart"]
        six_of_eight = settle_ticket({
            "stake": 1.0,
            "system": "6/8",
            "legs": ([{"odd": odd, "status": "HIT", "fixtureKey": fixture}
                      for odd, fixture in zip(winning_odds, fixtures[:6])]
                     + [{"odd": 1.2, "status": "MISS", "fixtureKey": fixtures[6]},
                        {"odd": 1.3, "status": "MISS", "fixtureKey": fixtures[7]}]),
        })
        conditional = six_of_eight["conditionalEstimate"]
        self.assertEqual(conditional["combinationCount"], 28)
        self.assertEqual(conditional["status"], "HIT")
        self.assertEqual(conditional["grossReturnPerUnit"], 0.1522)
        self.assertEqual(conditional["grossReturn"], 0.15)
        self.assertIsNone(six_of_eight["actualGrossReturn"])

        five_of_seven = settle_ticket({
            "stake": 1.0, "system": "5/7",
            "legs": [{"odd": 1.5 + index / 10, "status": "MISS"} for index in range(7)],
        })
        self.assertEqual(five_of_seven["combinationCount"], 21)
        self.assertEqual(five_of_seven["grossReturn"], 0.0)
        self.assertEqual(five_of_seven["netResult"], -1.0)

    def test_special_market_without_receipt_stays_pending(self):
        result = settle_ticket({"stake": 5, "boost": True, "legs": [{"odd": 2.0, "status": "HIT"}]})
        self.assertEqual(result["status"], "PENDING")
        self.assertEqual(result["calculationBasis"], "RECEIPT_REQUIRED")

        same_game = settle_ticket({"stake": 5, "legs": [
            {"fixtureKey": "real-madrid-celta", "market": "W1", "odd": 1.4, "status": "HIT"},
            {"fixtureKey": "real-madrid-celta", "market": "Team Over 1.5", "odd": 1.3, "status": "HIT"},
        ]})
        self.assertEqual(same_game["status"], "PENDING")
        self.assertEqual(same_game["calculationBasis"], "RECEIPT_REQUIRED")

    def test_receipt_separates_actual_return_from_estimate(self):
        result = settle_ticket({
            "stake": 10, "legs": [{"odd": 1.5, "status": "HIT"}],
        }, receipt={"verified": True, "grossReturn": 14.75, "stake": 10, "source": "local receipt", "reference": "R-1"})
        self.assertEqual(result["grossReturn"], 14.75)
        self.assertEqual(result["netResult"], 4.75)
        self.assertEqual(result["actualGrossReturn"], 14.75)
        self.assertEqual(result["actualNetResult"], 4.75)
        self.assertEqual(result["calculationBasis"], "VERIFIED_RECEIPT")

    def test_soros_receipt_applies_once_and_theoretical_track_never_moves_state(self):
        state = {"initialStake": 10, "currentStake": 10, "currentDay": 1, "targetDays": 30,
                 "vaultProfit": 10, "vaultRules": {"day5Lock": 10, "day7Lock": 20}, "history": []}
        receipt_result = {"status": "HIT", "actualGrossReturn": 13.8, "calculationBasis": "VERIFIED_RECEIPT"}
        advanced, applied, _ = apply_soros_settlement(state, settlement_id="snap:soros-B", track="TRILHA_B_OPERACIONAL",
                                                       settlement=receipt_result, date="2026-11-21")
        repeated, applied_again, _ = apply_soros_settlement(advanced, settlement_id="snap:soros-B", track="TRILHA_B_OPERACIONAL",
                                                             settlement=receipt_result, date="2026-11-21")
        self.assertTrue(applied)
        self.assertFalse(applied_again)
        self.assertEqual(advanced["currentDay"], 2)
        self.assertEqual(advanced["currentStake"], 13.8)
        self.assertEqual(repeated, advanced)

        theoretical, applied, _ = apply_soros_settlement(state, settlement_id="snap:soros-A", track="TRILHA_A_MATINAL",
                                                           settlement=receipt_result, date="2026-11-21")
        self.assertFalse(applied)
        self.assertEqual(theoretical, state)

    def test_soros_vault_locks_are_idempotent_on_day_five_and_day_seven(self):
        receipt_result = {"status": "HIT", "actualGrossReturn": 30.0, "calculationBasis": "VERIFIED_RECEIPT"}
        base = {"initialStake": 10, "currentStake": 20, "targetDays": 30,
                "vaultProfit": 10, "vaultRules": {"day5Lock": 10, "day7Lock": 20}, "history": []}
        day5 = dict(base, currentDay=5, vaultProfit=0)
        locked5, applied5, _ = apply_soros_settlement(day5, settlement_id="D5", track="B", settlement=receipt_result)
        self.assertTrue(applied5)
        self.assertEqual(locked5["vaultProfit"], 10.0)

        day7 = dict(base, currentDay=7)
        locked7, applied7, _ = apply_soros_settlement(day7, settlement_id="D7", track="B", settlement=receipt_result)
        duplicate7, applied7_again, _ = apply_soros_settlement(locked7, settlement_id="D7", track="B", settlement=receipt_result)
        self.assertTrue(applied7)
        self.assertFalse(applied7_again)
        self.assertEqual(locked7["vaultProfit"], 30.0)
        self.assertEqual(duplicate7, locked7)

    def test_estimated_receipt_free_result_does_not_change_operational_soros(self):
        state = {"initialStake": 10, "currentStake": 10, "currentDay": 1, "vaultProfit": 10, "history": []}
        estimated = {"status": "HIT", "grossReturn": 12.0, "actualGrossReturn": None,
                     "calculationBasis": "ESTIMATED_DECIMAL_ODDS_HALF_UP"}
        updated, applied, _ = apply_soros_settlement(state, settlement_id="ESTIMATE", track="B", settlement=estimated)
        self.assertFalse(applied)
        self.assertEqual(updated, state)

    def test_confere_retry_keeps_same_balances_and_does_not_count_a_twice(self):
        data = {
            "date": "2026-11-21", "snapshotId": "FAS_TEST_V1",
            "settlementEvidence": {
                "snapshotId": "FAS_TEST_V1", "verified": True, "source": "local fixture", "retrievedAt": "2026-11-21T22:00:00-03:00",
                "tickets": [{
                    "ticketId": "soros-track-b", "track": "TRILHA_B_OPERACIONAL",
                    "ticket": {"name": "Soros Operational", "type": "SOROS", "stake": 10,
                               "legs": [self.leg("HIT")]},
                    "receipt": {"verified": True, "grossReturn": 13.8, "stake": 10, "source": "local fixture", "reference": "R-1"},
                }],
            },
        }
        state = {"initialStake": 10, "currentStake": 10, "currentDay": 1, "targetDays": 30,
                 "vaultProfit": 10, "vaultRules": {"day5Lock": 10, "day7Lock": 20}, "history": []}
        snapshot = {"metadata": {"snapshotId": "FAS_TEST_V1"}, "tickets": [{
            "sourceKey": "soros-track-b", "stakeTotal": 10,
            "sourceTicket": {"name": "Soros Operational", "type": "SOROS", "stake": 10,
                             "legs": [{"odd": 1.38}]},
        }]}
        first_data, first_state, first_report = reconcile_financials(data, state, snapshot=snapshot)
        second_data, second_state, second_report = reconcile_financials(first_data, first_state, snapshot=snapshot)
        self.assertEqual(first_report["status"], "SETTLED")
        self.assertTrue(first_report["sorosUpdated"])
        self.assertFalse(second_report["changed"])
        self.assertFalse(second_report["sorosUpdated"])
        self.assertEqual(second_data["settlementResults"], first_data["settlementResults"])
        self.assertEqual(second_state, first_state)

    def test_normal_confere_retry_after_notifier_failure_is_idempotent(self):
        data = {
            "date": "2026-11-21", "snapshotId": "PIPELINE_V1",
            "settlementEvidence": {
                "snapshotId": "PIPELINE_V1", "verified": True, "source": "local fixture",
                "retrievedAt": "2026-11-21T22:00:00-03:00",
                "tickets": [{
                    "ticketId": "soros-track-b", "track": "TRILHA_B_OPERACIONAL",
                    "ticket": {"name": "Soros Operational", "type": "SOROS", "stake": 10,
                               "legs": [self.leg("HIT")]},
                    "receipt": {"verified": True, "grossReturn": 13.8, "stake": 10,
                                "source": "local fixture", "reference": "R-1"},
                }],
            },
        }
        state = {"initialStake": 10, "currentStake": 10, "currentDay": 1, "targetDays": 30,
                 "vaultProfit": 10, "vaultRules": {"day5Lock": 10, "day7Lock": 20}, "history": []}
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            active_path = root / "bilhetes_ativos.json"
            soros_path = root / "soros_state.json"
            snapshot_dir = root / "snapshots" / "2026-11-21"
            snapshot_dir.mkdir(parents=True)
            (snapshot_dir / "PIPELINE_V1.json").write_text(json.dumps({
                "metadata": {"snapshotId": "PIPELINE_V1"},
                "tickets": [{"sourceKey": "soros-track-b", "stakeTotal": 10,
                             "sourceTicket": {"name": "Soros Operational", "type": "SOROS", "stake": 10,
                                              "legs": [{"odd": 1.38}]}}],
            }), encoding="utf-8")
            active_path.write_text(json.dumps(data), encoding="utf-8")
            soros_path.write_text(json.dumps(state), encoding="utf-8")
            with mock.patch.object(confere_engine, "current_dir", str(root)), \
                    mock.patch.object(confere_engine, "parent_dir", str(root / "no-sync")), \
                    mock.patch("notifier.send_telegram", return_value=False):
                self.assertTrue(confere_engine.run_confere_pipeline())
                once = json.loads(soros_path.read_text(encoding="utf-8"))
                self.assertTrue(confere_engine.run_confere_pipeline())
                twice = json.loads(soros_path.read_text(encoding="utf-8"))
            self.assertEqual(once, twice)
            stored_grade = json.loads(active_path.read_text(encoding="utf-8"))
            self.assertEqual(len(stored_grade["settlementResults"]), 1)
            self.assertEqual(once["currentDay"], 2)
            self.assertEqual(once["currentStake"], 13.8)

    def test_confere_without_evidence_is_pending_and_message_has_no_fixed_scores(self):
        original = {"date": "2026-11-23", "snapshotId": "SETTLED_WITHOUT_EVIDENCE"}
        untouched, state, report = reconcile_financials(original, {"currentStake": 10, "currentDay": 2, "history": []})
        self.assertFalse(report["changed"])
        self.assertEqual(untouched, original)
        message = format_confere_message("2026-11-23", {
            "roundResult": "PENDENTE", "invested": 0, "returned": 0, "netProfit": 0, "financialSettlements": []
        }, [])
        self.assertIn("Sem evidência estruturada", message)
        self.assertNotIn("Bayern de Munique 4", message)

    def test_confere_requires_fixture_date_period_and_reports_receipt_divergence(self):
        data = {"date": "2026-11-21", "snapshotId": "EVIDENCE_V1", "settlementEvidence": {
            "snapshotId": "EVIDENCE_V1", "verified": True, "source": "match report",
            "retrievedAt": "2026-11-21T22:00:00-03:00", "tickets": [{
                "ticketId": "supremoTicket", "track": "A",
                "ticket": {"name": "Supremo", "stake": 10, "legs": [self.leg(
                    "HIT", fixture="Home x Away", period="FIRST_HALF", date="2026-11-21")]},
                "receipt": {"verified": True, "grossReturn": 15, "stake": 10, "status": "MISS",
                            "source": "local receipt", "reference": "R-2"},
            }],
        }}
        snapshot = {"metadata": {"snapshotId": "EVIDENCE_V1"}, "tickets": [{
            "sourceKey": "supremoTicket", "stakeTotal": 10,
            "sourceTicket": {"name": "Supremo", "stake": 10, "legs": [{
                "match": "Home x Away", "period": "FIRST_HALF", "odd": 1.5,
            }]},
        }]}
        _, _, report = reconcile_financials(data, {"history": []}, snapshot=snapshot)
        result = report["results"][0]
        self.assertEqual(result["result"]["status"], "PENDING")
        self.assertEqual(result["result"]["calculationBasis"], "EVIDENCE_DIVERGENCE")
        self.assertEqual(result["divergence"]["type"], "REPORT_RECEIPT_DIVERGENCE")
        message = format_confere_message("2026-11-21", {"financialSettlements": [result]}, [])
        self.assertIn("DIVERGÊNCIA", message)


if __name__ == "__main__":
    unittest.main()
