"""Local acceptance tests for immutable football snapshots."""

import datetime as dt
import json
import tempfile
import unittest
import sys
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from snapshot_store import SnapshotError, save_snapshot


class SnapshotStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.captured = dt.datetime.fromisoformat("2026-11-23T16:00:00-03:00")

    def tearDown(self):
        self.temp.cleanup()

    def grade(self, snapshot_id, track, *, include_started=False):
        selections = [
            {
                "match": "Future FC x Away FC",
                "kickoff": "2026-11-23T18:00:00-03:00",
                "period": "FT",
                "market": "Moneyline",
                "side": "Home",
                "line": None,
                "odd": 1.5,
                "quoteAt": "2026-11-23T15:50:00-03:00",
                "quoteSource": "manual test fixture",
            }
        ]
        if include_started:
            selections.insert(0, {
                "match": "Started FC x Away FC",
                "kickoff": "2026-11-23T15:30:00-03:00",
                "market": "Moneyline",
                "odd": 2.0,
            })
        return {
            "date": "2026-11-23",
            "snapshotId": snapshot_id,
            "status": "ACTIVE",
            "methodologyVersion": "FAS V7.5",
            "track": track,
            "changeReason": "initial" if track == "A" else "revalidation",
            "supremoTicket": {"name": "Supremo", "stake": 10.0, "selections": selections},
            "structuredTickets": [],
            "sorosTicket": {},
        }

    def test_revalidation_preserves_track_a_and_links_track_b(self):
        a, created_a = save_snapshot(self.grade("EVENT_V1", "A"), self.root, captured_at=self.captured)
        b, created_b = save_snapshot(self.grade("EVENT_V2", "B"), self.root, captured_at=self.captured)
        self.assertTrue(created_a)
        self.assertTrue(created_b)
        self.assertEqual(a["metadata"]["track"], "A")
        self.assertEqual(b["metadata"]["track"], "B")
        self.assertEqual(b["metadata"]["previousSnapshotId"], "EVENT_V1")
        manifest = json.loads((self.root / "2026-11-23" / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["latestSnapshotId"], "EVENT_V2")
        self.assertEqual([entry["snapshotId"] for entry in manifest["snapshots"]], ["EVENT_V1", "EVENT_V2"])

    def test_replay_is_idempotent_and_conflicting_id_is_rejected(self):
        grade = self.grade("EVENT_V1", "A")
        _, created = save_snapshot(grade, self.root, captured_at=self.captured)
        replay, created_again = save_snapshot(grade, self.root, captured_at=self.captured)
        self.assertTrue(created)
        self.assertFalse(created_again)
        self.assertEqual(replay["metadata"]["snapshotId"], "EVENT_V1")
        changed = self.grade("EVENT_V1", "A")
        changed["changeReason"] = "silently changed"
        with self.assertRaises(SnapshotError):
            save_snapshot(changed, self.root, captured_at=self.captured)

    def test_started_selection_is_excluded_and_quote_fields_are_retained(self):
        snapshot, _ = save_snapshot(
            self.grade("EVENT_V1", "A", include_started=True), self.root, captured_at=self.captured
        )
        self.assertEqual(snapshot["excludedStartedSelections"], 1)
        selections = snapshot["tickets"][0]["components"]
        self.assertEqual(len(selections), 1)
        self.assertEqual(selections[0]["fixture"], "Future FC x Away FC")
        self.assertEqual(selections[0]["quoteAt"], "2026-11-23T15:50:00-03:00")
        self.assertEqual(selections[0]["quoteSource"], "manual test fixture")

    def test_failed_manifest_write_keeps_previous_latest_snapshot(self):
        save_snapshot(self.grade("EVENT_V1", "A"), self.root, captured_at=self.captured)
        import snapshot_store

        original = snapshot_store._atomic_json_write

        def fail_manifest(path, value):
            if path.name == "manifest.json":
                raise OSError("simulated manifest write failure")
            original(path, value)

        with mock.patch("snapshot_store._atomic_json_write", side_effect=fail_manifest):
            with self.assertRaises(OSError):
                save_snapshot(self.grade("EVENT_V2", "B"), self.root, captured_at=self.captured)
        manifest = json.loads((self.root / "2026-11-23" / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["latestSnapshotId"], "EVENT_V1")
        self.assertTrue((self.root / "2026-11-23" / "EVENT_V1.json").is_file())

    def test_settled_grade_is_refused_for_pre_match_snapshot(self):
        grade = self.grade("EVENT_SETTLED", "A")
        grade["status"] = "SETTLED"
        with self.assertRaises(SnapshotError):
            save_snapshot(grade, self.root, captured_at=self.captured)

    def test_morning_pipeline_snapshots_before_local_notifier(self):
        import fas_engine
        import notifier

        grade = self.grade("EVENT_V1", "A")
        (self.root / "bilhetes_ativos.json").write_text(json.dumps(grade), encoding="utf-8")
        snapshot_file = self.root / "snapshots" / "2026-11-23" / "EVENT_V1.json"
        observed = []

        def format_locally(_data):
            observed.append(snapshot_file.is_file())
            self.assertEqual(_data["conformity"]["status"], "REVIEW")
            return "local test message"

        with mock.patch.object(fas_engine, "current_dir", str(self.root)), \
                mock.patch.object(fas_engine, "parent_dir", str(self.root / "no-sync")), \
                mock.patch.object(notifier, "format_grade_message", side_effect=format_locally), \
                mock.patch.object(notifier, "send_telegram", return_value=True):
            self.assertTrue(fas_engine.run_morning_pipeline())
        self.assertEqual(observed, [True])


if __name__ == "__main__":
    unittest.main()
