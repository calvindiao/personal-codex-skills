"""Exercise the installer through its CLI using isolated host directories."""

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parent.parent
BEGIN = "<!-- BEGIN personal-codex-skills:communication -->"
END = "<!-- END personal-codex-skills:communication -->"


class SyncInstructionsTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        self.fixture = root / "repository"
        (self.fixture / "scripts").mkdir(parents=True)
        (self.fixture / "instructions").mkdir()
        self.script = self.fixture / "scripts" / "sync-instructions.py"
        shutil.copy2(REPO / "scripts" / "sync-instructions.py", self.script)
        self.source = self.fixture / "instructions" / "AGENTS.md"
        self.source.write_text("# Communication\n\nKeep conditions and uncertainty.\n", encoding="utf-8")
        self.codex_home = root / "host" / ".codex"
        self.target = self.codex_home / "AGENTS.md"

    def run_sync(self, *arguments, expected=0, explicit_home=True):
        command = [sys.executable, str(self.script)]
        if explicit_home:
            command += ["--codex-home", str(self.codex_home)]
        result = subprocess.run(
            command + list(arguments), capture_output=True, text=True,
            env={**os.environ, "CODEX_HOME": str(self.codex_home)},
        )
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def write_target(self, content):
        self.codex_home.mkdir(parents=True, exist_ok=True)
        self.target.write_bytes(content)

    def test_check_does_not_create_files_and_install_is_idempotent(self):
        self.run_sync("--check", expected=1)
        self.assertFalse(self.codex_home.exists())
        self.run_sync(explicit_home=False)
        installed = self.target.read_bytes()
        self.run_sync("--check")
        self.run_sync()
        self.assertEqual(self.target.read_bytes(), installed)
        self.assertEqual(list(self.codex_home.glob("AGENTS.md.backup-*")), [])

    def test_existing_instructions_and_backup_remain_byte_exact(self):
        original = "# Local preferences\r\nKeep my existing rule.\r\n".encode()
        self.write_target(original)
        self.run_sync()
        self.assertTrue(self.target.read_bytes().startswith(original))
        backups = list(self.codex_home.glob("AGENTS.md.backup-*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_bytes(), original)

    def test_new_version_replaces_only_managed_block(self):
        self.write_target(b"# Local rules\nKeep this.\n")
        self.run_sync()
        with self.target.open("ab") as stream:
            stream.write(b"\n# Another local rule\nKeep this too.\n")
        self.source.write_text("# Communication\n\nUse the updated rule.\n", encoding="utf-8")
        self.run_sync("--check", expected=1)
        self.run_sync()
        self.run_sync("--check")
        content = self.target.read_text()
        self.assertIn("Keep this.", content)
        self.assertIn("Keep this too.", content)
        self.assertIn("Use the updated rule.", content)
        self.assertNotIn("Keep conditions and uncertainty.", content)
        self.assertEqual(content.count(BEGIN), 1)
        self.assertEqual(content.count(END), 1)

    def test_standalone_source_copy_is_migrated_without_duplication(self):
        self.write_target(self.source.read_bytes())
        self.run_sync()
        self.assertEqual(self.target.read_text().count("Keep conditions and uncertainty."), 1)
        self.run_sync("--check")

    def test_malformed_markers_and_active_override_do_not_change_files(self):
        for content in (BEGIN, END + "\n" + BEGIN, BEGIN + "\n" + BEGIN + "\n" + END):
            with self.subTest(content=content):
                original = content.encode()
                self.write_target(original)
                self.run_sync(expected=2)
                self.assertEqual(self.target.read_bytes(), original)
        original = b"# Local\nKeep this.\n"
        self.write_target(original)
        (self.codex_home / "AGENTS.override.md").write_text("# Active override\n")
        self.run_sync(expected=2)
        self.run_sync("--check", expected=2)
        self.assertEqual(self.target.read_bytes(), original)
        self.assertEqual(list(self.codex_home.glob("AGENTS.md.backup-*")), [])

    def test_canonical_symlink_tracks_updates_without_replacing_link(self):
        self.codex_home.mkdir(parents=True)
        try:
            self.target.symlink_to(self.source)
        except OSError as error:
            self.skipTest(str(error))
        self.run_sync("--check")
        self.source.write_text("# Updated linked instructions\n")
        self.run_sync()
        self.assertTrue(self.target.is_symlink())
        self.assertEqual(self.target.read_bytes(), self.source.read_bytes())


if __name__ == "__main__":
    unittest.main()
