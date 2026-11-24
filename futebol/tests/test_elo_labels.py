"""Presentation-only Elo labels for FAS tickets; internal IDs stay unchanged."""

import sys
import unittest
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "futebol"))
sys.path.insert(0, str(ROOT / "basquete"))

import notifier

_basket_engine_spec = importlib.util.spec_from_file_location("fas_basketball_engine_for_label_test", ROOT / "basquete" / "fas_engine.py")
_basket_engine = importlib.util.module_from_spec(_basket_engine_spec)
_basket_engine_spec.loader.exec_module(_basket_engine)
format_nba_message = _basket_engine.format_nba_message


class EloLabelTests(unittest.TestCase):
    def test_internal_types_map_to_requested_elo_names(self):
        expected = {
            "SAFE": "MESTRE",
            "TRIPLA_SUPREMA_NBA": "DIAMANTE",
            "SAFE_PLUS": "OURO",
            "ATTACK_VALUE": "PRATA",
            "IMPROVAVEL": "BRONZE",
        }
        for ticket_type, label in expected.items():
            with self.subTest(ticket_type=ticket_type):
                self.assertTrue(notifier.display_ticket_label(ticket_type, "Bilhete").startswith(label))
        self.assertEqual(notifier.display_ticket_label("SOROS", "Desafio Soros"), "Desafio Soros")

    def test_football_grade_message_uses_display_labels_without_mutating_json(self):
        grade = {
            "date": "2026-11-24",
            "supremoTicket": {"multiplierGlobal": 1.5, "stake": 1, "selections": []},
            "structuredTickets": [
                {"name": "SAFE Plus", "type": "SAFE_PLUS", "multiplier": 1.6, "stake": 1},
                {"name": "Super Attack", "type": "ATTACK", "multiplier": 2.0, "stake": 1},
                {"name": "Improvável", "type": "IMPROVAVEL", "multiplier": 10.0, "stake": 1},
            ],
        }
        original_types = [ticket["type"] for ticket in grade["structuredTickets"]]
        message = notifier.format_grade_message(grade)
        self.assertIn("DIAMANTE — BILHETE SUPREMO", message)
        self.assertIn("OURO — SAFE Plus", message)
        self.assertIn("PRATA — Super Attack", message)
        self.assertIn("BRONZE — Improvável", message)
        self.assertEqual([ticket["type"] for ticket in grade["structuredTickets"]], original_types)

    def test_basketball_message_uses_same_mapping_for_corresponding_models(self):
        message = format_nba_message({
            "date": "2026-11-24",
            "supremoTicket": {"multiplierGlobal": 1.5, "selections": []},
            "safeTicket": {"multiplier": 1.6, "stopPoints": []},
            "experimentalTickets": [{"type": "ATTACK_VALUE", "name": "Ataque", "multiplier": 2.0, "legs": []}],
            "roundSweepTicket": {"name": "Bingo", "multiplier": 10.0, "selections": []},
        })
        self.assertIn("DIAMANTE — SUPREMO BASQUETE", message)
        self.assertIn("MESTRE — MÚLTIPLA 1", message)
        self.assertIn("PRATA — Ataque", message)
        self.assertIn("BRONZE — Bingo", message)


if __name__ == "__main__":
    unittest.main()
