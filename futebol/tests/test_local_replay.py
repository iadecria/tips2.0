"""Full local replay of valid/invalid grades, revalidation and partial CONFERE."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import confere_engine
import fas_engine


class LocalReplayTests(unittest.TestCase):
    def grade(self, snapshot_id, track="TRILHA_B_OPERACIONAL"):
        return {
            "date": "2026-11-24", "snapshotId": snapshot_id, "track": track,
            "methodologyVersion": "V7.5", "changeReason": "initial" if snapshot_id.endswith("V1") else "revalidation",
            "qualityFixtureCount": 10,
            "qualityFixtures": [{"fixtureKey": f"Q{index}", "date": "2026-11-24",
                                 "competition": "Premier League"} for index in range(10)],
            "supremoTicket": {"name": "Supremo", "track": track, "stake": 5,
                              "selections": [{"match": "Alpha x Beta", "period": "FT", "market": "1X",
                                              "side": "Alpha/Draw", "odd": 1.3}]},
            "structuredTickets": [{"name": "SAFE", "type": "SAFE", "track": track, "stake": 4,
                                    "stopPoints": [
                                        {"level": "Stop Point 1", "multiplier": 1.4, "legs": [
                                            {"match": "Gamma x Delta", "period": "FT", "market": "1X",
                                             "side": "Gamma/Draw", "odd": 1.2}]},
                                        {"level": "Stop Point 2", "multiplier": 1.5, "legs": [
                                            {"match": "Epsilon x Zeta", "period": "FT", "market": "DNB",
                                             "side": "Epsilon", "odd": 1.25}]},
                                    ]}],
            "sorosTicket": {"name": "Desafio Soros", "type": "SOROS", "track": track, "stake": 2,
                            "legs": [{"match": "Eta x Theta", "period": "FT", "market": "Moneyline",
                                      "side": "Eta", "odd": 1.35}]},
        }

    def test_end_to_end_local_replay_and_retry(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            active_path = root / "bilhetes_ativos.json"
            soros_path = root / "soros_state.json"
            soros_initial = {"initialStake": 10, "currentStake": 10, "currentDay": 1,
                             "vaultProfit": 10, "history": []}
            active_path.write_text(json.dumps(self.grade("REPLAY_V1")), encoding="utf-8")
            soros_path.write_text(json.dumps(soros_initial), encoding="utf-8")

            with mock.patch.object(fas_engine, "current_dir", str(root)), \
                    mock.patch.object(fas_engine, "parent_dir", str(root / "no-sync")), \
                    mock.patch("notifier.send_telegram", return_value=True):
                self.assertTrue(fas_engine.run_morning_pipeline())
                first_snapshot = json.loads((root / "snapshots" / "2026-11-24" / "REPLAY_V1.json").read_text())
                active_path.write_text(json.dumps(self.grade("REPLAY_V2")), encoding="utf-8")
                self.assertTrue(fas_engine.run_morning_pipeline())

            second_snapshot = json.loads((root / "snapshots" / "2026-11-24" / "REPLAY_V2.json").read_text())
            self.assertEqual(second_snapshot["metadata"]["previousSnapshotId"], "REPLAY_V1")
            self.assertEqual(first_snapshot["metadata"]["snapshotId"], "REPLAY_V1")
            self.assertEqual(json.loads((root / "snapshots" / "2026-11-24" / "manifest.json").read_text())["latestSnapshotId"], "REPLAY_V2")

            data = json.loads(active_path.read_text(encoding="utf-8"))
            data["settlementEvidence"] = {
                "snapshotId": "REPLAY_V2", "verified": True,
                "source": "local replay fixture", "retrievedAt": "2026-11-24T23:00:00-03:00",
                "tickets": [
                    {"ticketId": "supremoTicket", "track": "TRILHA_B_OPERACIONAL",
                     "ticket": {"legs": [{"status": "HIT", "evidence": {
                         "status": "HIT", "fixture": "Alpha x Beta", "date": "2026-11-24",
                         "period": "FT", "source": "local replay fixture",
                         "retrievedAt": "2026-11-24T23:00:00-03:00"}}]}},
                    {"ticketId": "structuredTickets[0]", "track": "TRILHA_B_OPERACIONAL",
                     "ticket": {"stopPoints": [
                         {"legs": [{"status": "HIT"}]}, {"legs": [{"status": "PENDING"}]},
                     ]}},
                ],
            }
            active_path.write_text(json.dumps(data), encoding="utf-8")

            with mock.patch.object(confere_engine, "current_dir", str(root)), \
                    mock.patch.object(confere_engine, "parent_dir", str(root / "no-sync")), \
                    mock.patch("notifier.send_telegram", return_value=False):
                self.assertTrue(confere_engine.run_confere_pipeline())
                once = json.loads(active_path.read_text(encoding="utf-8"))
                soros_once = json.loads(soros_path.read_text(encoding="utf-8"))
                self.assertTrue(confere_engine.run_confere_pipeline())
                twice = json.loads(active_path.read_text(encoding="utf-8"))
                soros_twice = json.loads(soros_path.read_text(encoding="utf-8"))

            statuses = {item["ticketId"]: item["result"]["status"] for item in twice["settlementResults"]}
            self.assertEqual(statuses["supremoTicket"], "HIT")
            self.assertEqual(statuses["structuredTickets[0]"], "PENDING")
            self.assertEqual(once["settlementResults"], twice["settlementResults"])
            self.assertEqual(soros_initial, soros_once)
            self.assertEqual(soros_once, soros_twice)

    def test_invalid_grade_does_not_snapshot_or_notify(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            grade = json.loads((Path(__file__).parent / "fixtures" / "compliance_2026-11-23_track_b.json").read_text(encoding="utf-8"))
            (root / "bilhetes_ativos.json").write_text(json.dumps(grade), encoding="utf-8")
            with mock.patch.object(fas_engine, "current_dir", str(root)), \
                    mock.patch.object(fas_engine, "parent_dir", str(root / "no-sync")), \
                    mock.patch("notifier.send_telegram") as send:
                self.assertFalse(fas_engine.run_morning_pipeline())
            send.assert_not_called()
            self.assertFalse((root / "snapshots").exists())


if __name__ == "__main__":
    unittest.main()
