"""Regression assertions for the source-attributed FAS historical baseline."""

import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
FIXTURE = HERE / "fixtures" / "historical_baseline.json"


class HistoricalBaselineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_2026_11_21_case_and_receipt_gap(self):
        case = self.baseline["cases"]["2026-11-21"]
        self.assertEqual(case["improvavel"], {
            "selections": 8,
            "hits": 6,
            "system": "6/8",
            "sourceSaysSystemPrizeActivated": True,
        })
        self.assertEqual(case["soros"]["stakeDeclaredBRL"], 10.0)
        self.assertIsNone(case["soros"]["returnConfirmedByReceiptBRL"])

    def test_2026_11_23_acceptance_baseline(self):
        case = self.baseline["cases"]["2026-11-23"]
        self.assertEqual(case["trackB"]["operationalTicketCount"], 5)
        self.assertAlmostEqual(case["trackB"]["operationalStakeDeclaredBRL"], 64.80)
        self.assertEqual(case["trackB"]["operationalReturnDeclaredBRL"], 0.0)
        self.assertEqual(case["trackA"]["soros"]["returnDeclaredBRL"], 17.94)
        self.assertIsNone(case["trackA"]["soros"]["returnConfirmedByReceiptBRL"])
        self.assertEqual(case["trackA"]["improvavel"], {
            "selections": 8, "hits": 2, "system": "6/8"
        })
        self.assertEqual(case["trackB"]["improvavel"], {
            "selections": 7, "hits": 0, "system": "5/7"
        })

    def test_23_nov_operational_tickets_sum_to_declared_stake(self):
        case = self.baseline["cases"]["2026-11-23"]
        ticket_stakes = [ticket["stakeDeclaredBRL"] for ticket in case["trackB"]["tickets"]]
        ticket_ids = [ticket["id"] for ticket in case["trackB"]["tickets"]]
        self.assertAlmostEqual(sum(ticket_stakes), 64.80)
        self.assertEqual(len(ticket_ids), 5)
        self.assertEqual(len(set(ticket_ids)), 5)

    def test_fixture_sources_exist_and_distinguish_project_claims_from_receipts(self):
        for relative in self.baseline["sources"].values():
            self.assertTrue((HERE / relative).resolve().is_file(), relative)
        for case in self.baseline["cases"].values():
            self.assertIn("receipt", case["provenance"])
            self.assertIn("not present", case["provenance"]["receipt"])

    def test_root_copies_are_not_counted_as_separate_rounds(self):
        # The CLI points to futebol/bilhetes_ativos.json and the backtest database
        # exists only under futebol/ in this checkout.
        self.assertTrue((ROOT / "fas_cli.py").is_file())
        self.assertTrue((ROOT / "futebol" / "bilhetes_ativos.json").is_file())
        self.assertFalse((ROOT / "bilhetes_ativos.json").exists())
        self.assertFalse((ROOT / "FAS3_FOOTBALL_BACKTEST_DATABASE.md").exists())


if __name__ == "__main__":
    unittest.main()
