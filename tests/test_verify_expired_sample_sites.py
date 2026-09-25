import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "verify_expired_sample_sites.py"
SPEC = importlib.util.spec_from_file_location("verify_expired_sample_sites", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class PublicExpiryVerificationTests(unittest.TestCase):
    def test_http_404_confirms_route_is_gone(self):
        def open_url(_request, timeout):
            raise HTTPError("https://example.test/r/sample/", 404, "not found", {}, None)

        result = MODULE.verify_route_gone(
            "https://example.test/r/sample/",
            open_url=open_url,
            attempts=1,
            sleep=lambda _seconds: None,
        )
        self.assertEqual(result, {"http_status": 404, "attempts": 1})

    def test_live_route_never_counts_as_removed(self):
        def open_url(_request, timeout):
            return type("Response", (), {
                "status": 200,
                "__enter__": lambda self: self,
                "__exit__": lambda self, *_args: None,
            })()

        with self.assertRaisesRegex(RuntimeError, "still responds"):
            MODULE.verify_route_gone(
                "https://example.test/r/sample/",
                open_url=open_url,
                attempts=2,
                interval_seconds=0,
                sleep=lambda _seconds: None,
            )

    def test_only_expired_unverified_routes_get_receipts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            due_id = "r_aaaaaaaaaaaaaaaaaaaa"
            active_id = "r_bbbbbbbbbbbbbbbbbbbb"
            manifest = root / "sample-site-lifecycle.json"
            manifest.write_text(json.dumps({"samples": [
                {"restoID": due_id, "status": "expired"},
                {"restoID": active_id, "status": "active"},
                {"restoID": "r_cccccccccccccccccccc", "status": "expired", "public_url_verified_at": "2026-10-06T09:00:00Z"},
            ]}), encoding="utf-8")

            code, receipt = MODULE.verify_expired(
                manifest,
                datetime(2026, 10, 6, 9, 0, tzinfo=timezone.utc),
                checker=lambda _url: {"http_status": 410, "attempts": 1},
                root=root,
            )

            self.assertEqual(code, 0)
            self.assertEqual([row["restoID"] for row in receipt["verified_removed"]], [due_id])
            saved = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(saved["samples"][0]["public_url_http_status"], 410)
            self.assertNotIn("public_url_verified_at", saved["samples"][1])
            self.assertTrue(list((root / "cleanup-receipts").glob("verification-*.json")))

    def test_pending_route_is_not_marked_verified(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            route_id = "r_aaaaaaaaaaaaaaaaaaaa"
            manifest = root / "sample-site-lifecycle.json"
            manifest.write_text(json.dumps({"samples": [{"restoID": route_id, "status": "expired"}]}), encoding="utf-8")

            code, receipt = MODULE.verify_expired(
                manifest,
                datetime(2026, 10, 6, 9, 0, tzinfo=timezone.utc),
                checker=lambda _url: (_ for _ in ()).throw(RuntimeError("still live")),
                root=root,
            )

            self.assertEqual(code, 1)
            self.assertEqual(receipt["unresolved"][0]["restoID"], route_id)
            saved = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertNotIn("public_url_verified_at", saved["samples"][0])


if __name__ == "__main__":
    unittest.main()
