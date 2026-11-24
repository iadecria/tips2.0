"""Acceptance tests for snapshot-derived, deduplicated performance metrics."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from performance_panel import build_performance_panel


class PerformancePanelTests(unittest.TestCase):
    def test_no_snapshot_history_reports_no_sample_without_using_legacy_totals(self):
        panel = build_performance_panel([], [])
        self.assertEqual(panel["sampleStatus"], "sem amostra")
        self.assertEqual(panel["strategies"], [])
        self.assertTrue(panel["metrics"]["simulationAndExecutionSeparated"])

    def test_deduplicates_selections_but_counts_occurrences_and_separates_execution(self):
        snapshot = {"metadata": {"snapshotId": "S1", "date": "2026-11-24", "methodologyVersion": "V7.5"},
                    "tickets": [{"sourceKey": "safe", "type": "SAFE", "stakeTotal": 10,
                                 "sourceTicket": {"legs": [
                                     {"match": "A x B", "period": "FT", "market": "1X", "side": "Home/Draw", "odd": 1.5},
                                     {"match": "A x B", "period": "FT", "market": "1X", "side": "Home/Draw", "odd": 1.5},
                                 ]},
                                 "components": [{}, {}]},
                                {"sourceKey": "safe-alt", "type": "SAFE", "stakeTotal": 10,
                                 "sourceTicket": {"legs": [
                                     {"match": "A x B", "period": "FT", "market": "1X", "side": "Home/Draw", "odd": 1.5},
                                 ]}, "components": [{}]},
                                {"sourceKey": "soros", "type": "SOROS", "stakeTotal": 5,
                                 "sourceTicket": {"legs": [
                                     {"match": "C x D", "period": "FT", "market": "ML", "side": "Home", "odd": 1.4},
                                 ]}, "components": [{}]}]}
        settlements = [
            {"snapshotId": "S1", "ticketId": "safe", "stakeDeclared": 10,
             "result": {"status": "MISS", "calculationBasis": "ESTIMATED_DECIMAL_ODDS_HALF_UP"},
             "selectionEvidence": [{"status": "HIT"}, {"status": "HIT"}]},
            {"snapshotId": "S1", "ticketId": "safe-alt", "stakeDeclared": 10,
             "result": {"status": "HIT", "calculationBasis": "ESTIMATED_DECIMAL_ODDS_HALF_UP"},
             "selectionEvidence": [{"status": "HIT"}]},
            {"snapshotId": "S1", "ticketId": "soros", "stakeDeclared": 5,
             "result": {"status": "HIT", "calculationBasis": "VERIFIED_RECEIPT", "actualGrossReturn": 7},
             "selectionEvidence": [{"status": "HIT"}]},
        ]
        panel = build_performance_panel([snapshot], settlements)
        self.assertEqual(len(panel["strategies"]), 2)
        safe = next(row for row in panel["strategies"] if row["strategy"] == "SAFE")
        self.assertEqual(safe["HIT"], 1)
        safe_selections = next(row for row in panel["selections"] if row["strategy"] == "SAFE")
        self.assertEqual(safe_selections["uniqueSelections"], 1)
        self.assertEqual(safe_selections["billetOccurrences"], 2)
        self.assertEqual(safe_selections["concentration"][0]["ticketOccurrences"], 2)
        self.assertEqual(safe["knownNetReturn"], None)
        soros = next(row for row in panel["strategies"] if row["strategy"] == "SOROS")
        self.assertEqual(soros["mode"], "executed")
        self.assertEqual(soros["knownNetReturn"], 2.0)

    def test_void_and_pending_do_not_enter_hit_rate_denominator(self):
        snapshot = {"metadata": {"snapshotId": "S", "date": "2026-11-24", "methodologyVersion": "V"},
                    "tickets": [{"sourceKey": "t", "type": "SAFE", "sourceTicket": {"legs": [
                        {"match": f"A{i} x B", "market": "ML", "side": "Home", "period": "FT"}
                        for i in range(3)]}}]}
        records = [{"snapshotId": "S", "ticketId": "t", "result": {"status": "PENDING"},
                    "selectionEvidence": [{"status": "HIT"}, {"status": "VOID"}, {"status": "PENDING"}]}]
        row = build_performance_panel([snapshot], records)["strategies"][0]
        self.assertEqual(row["sampleSize"], 1)
        self.assertEqual(row["selectionHitRate"], 1.0)
        self.assertEqual(row["VOID"], 1)
        self.assertEqual(row["PENDING"], 1)


if __name__ == "__main__":
    unittest.main()
