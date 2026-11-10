"""Exercise receipt publication against real Git indexes, without network writes."""
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/stage_cleanup_receipt.sh"


class CleanupStagingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "-q")
        self.git("config", "user.name", "Cleanup test")
        self.git("config", "user.email", "cleanup@example.test")
        self.write("sample-site-lifecycle.json", "{}\n")
        self.write("round-2/index.html", "expired overview\n")
        self.write("round3/index.html", "expired overview\n")
        self.write("cleanup-receipts/old.json", '{"removed_sites": []}\n')
        self.write("README.md", "unrelated tracked file\n")
        self.commit_all()

    def git(self, *args):
        """Run Git only inside this disposable fixture repository."""
        return subprocess.run(
            ["git", *args], cwd=self.root, check=True,
            text=True, capture_output=True,
        ).stdout

    def write(self, relative, content):
        """Create or update a fixture output."""
        target = self.root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def commit_all(self):
        self.git("add", "-A")
        self.git("commit", "-qm", "fixture")

    def stage(self):
        subprocess.run(["bash", str(SCRIPT)], cwd=self.root, check=True)

    def changes(self):
        return set(self.git("diff", "--cached", "--name-status").splitlines())

    def test_absent_untracked_route_root_still_saves_verification_receipt(self):
        self.write("sample-site-lifecycle.json", '{"verified": true}\n')
        self.write("cleanup-receipts/verification-new.json", '{"http_status": 404}\n')
        self.stage()
        self.assertEqual(self.changes(), {
            "M\tsample-site-lifecycle.json",
            "A\tcleanup-receipts/verification-new.json",
        })
        self.git("commit", "-qm", "verification receipt")
        self.assertEqual(json.loads(self.git(
            "show", "HEAD:cleanup-receipts/verification-new.json"
        )), {"http_status": 404})
        self.assertIn("removed_sites", self.git("show", "HEAD:cleanup-receipts/old.json"))

    def test_deleted_tracked_route_root_preserves_deletion_evidence(self):
        self.write("r/r_aaaaaaaaaaaaaaaaaaaa/index.html", "menu\n")
        self.commit_all()
        shutil.rmtree(self.root / "r")
        self.write("cleanup-receipts/deletion.json", '{"route_removed": true}\n')
        self.stage()
        self.assertEqual(self.changes(), {
            "D\tr/r_aaaaaaaaaaaaaaaaaaaa/index.html",
            "A\tcleanup-receipts/deletion.json",
        })

    def test_normal_outputs_are_staged_without_unrelated_changes(self):
        self.write("r/r_aaaaaaaaaaaaaaaaaaaa/index.html", "old menu\n")
        self.commit_all()
        for relative in ("r/r_aaaaaaaaaaaaaaaaaaaa/index.html",
                         "round-2/index.html", "round3/index.html"):
            self.write(relative, "updated\n")
        self.write("README.md", "unrelated change\n")
        self.write("unrelated.txt", "unrelated new file\n")
        self.write("cleanup-receipts/new.json", "{}\n")
        self.stage()
        self.assertEqual(self.changes(), {
            "M\tr/r_aaaaaaaaaaaaaaaaaaaa/index.html", "M\tround-2/index.html",
            "M\tround3/index.html", "A\tcleanup-receipts/new.json",
        })

    def test_clean_rerun_with_absent_optional_outputs_is_a_noop(self):
        self.git("rm", "-r", "round-2", "round3", "cleanup-receipts")
        self.git("commit", "-qm", "optional outputs absent")
        self.stage()
        self.assertEqual(self.changes(), set())


if __name__ == "__main__":
    unittest.main()
