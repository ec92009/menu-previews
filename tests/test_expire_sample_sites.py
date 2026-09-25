import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "expire_sample_sites.py"
SPEC = importlib.util.spec_from_file_location("expire_sample_sites", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class SampleExpiryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "r").mkdir()
        self.due_id = "r_aaaaaaaaaaaaaaaaaaaa"
        self.active_id = "r_bbbbbbbbbbbbbbbbbbbb"
        (self.root / "r" / self.due_id).mkdir()
        (self.root / "r" / self.active_id).mkdir()
        (self.root / "round3").mkdir()
        (self.root / "round3" / "index.html").write_text(
            f'<article><a href="https://example.test/r/{self.due_id}/">Expired</a></article>'
            f'<article><a href="https://example.test/r/{self.active_id}/">Still active</a></article>',
            encoding="utf-8",
        )
        self.manifest = self.root / "sample-site-lifecycle.json"
        self.manifest.write_text(json.dumps({
            "samples": [
                {
                    "restoID": self.due_id,
                    "expires_at": "2026-10-06T08:48:26Z",
                    "overview_path": "round3/index.html",
                    "status": "active",
                },
                {
                    "restoID": self.active_id,
                    "expires_at": "2026-10-08T08:36:02Z",
                    "overview_path": "round3/index.html",
                    "status": "active",
                },
            ]
        }), encoding="utf-8")
        self.now = datetime(2026, 10, 7, 0, 0, tzinfo=timezone.utc)

    def tearDown(self):
        self.temp.cleanup()

    def test_dry_run_leaves_routes_and_manifest_unchanged(self):
        result = MODULE.clean_due(self.root, self.manifest, self.now, apply=False)
        self.assertEqual(result, [])
        self.assertTrue((self.root / "r" / self.due_id).exists())
        self.assertEqual(json.loads(self.manifest.read_text())["samples"][0]["status"], "active")

    def test_apply_removes_only_due_route_and_scrubs_its_overview_card(self):
        receipts = MODULE.clean_due(self.root, self.manifest, self.now, apply=True)
        self.assertEqual(len(receipts), 1)
        self.assertFalse((self.root / "r" / self.due_id).exists())
        self.assertTrue((self.root / "r" / self.active_id).exists())
        index = (self.root / "round3" / "index.html").read_text()
        self.assertNotIn(self.due_id, index)
        self.assertIn(self.active_id, index)
        states = {row["restoID"]: row["status"] for row in json.loads(self.manifest.read_text())["samples"]}
        self.assertEqual(states[self.due_id], "expired")
        self.assertEqual(states[self.active_id], "active")

    def test_expired_overview_is_replaced_after_all_its_samples_expire(self):
        data = json.loads(self.manifest.read_text())
        data["samples"][1]["expires_at"] = "2026-10-06T08:48:26Z"
        self.manifest.write_text(json.dumps(data), encoding="utf-8")
        MODULE.clean_due(self.root, self.manifest, self.now, apply=True)
        index = (self.root / "round3" / "index.html").read_text()
        self.assertIn("Estas muestras han caducado", index)
        self.assertNotIn(self.due_id, index)
        self.assertNotIn(self.active_id, index)

    def test_rejects_path_traversal_ids(self):
        with self.assertRaises(ValueError):
            MODULE.safe_route(self.root, "../outside")


if __name__ == "__main__":
    unittest.main()
