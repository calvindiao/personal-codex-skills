"""Exercise the installer using isolated hosts and deterministic concurrent edits."""

import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


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

    def run_sync_with_concurrent_change(self, change):
        spec = importlib.util.spec_from_file_location("sync_instructions", self.script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        chmod = os.chmod

        def change_before_replace(path, mode, *args, **kwargs):
            chmod(path, mode, *args, **kwargs)
            if Path(path).name.startswith(".AGENTS-"):
                change()

        with patch.object(module.os, "chmod", side_effect=change_before_replace):
            with self.assertRaisesRegex(ValueError, "changed during sync"):
                module.sync(self.codex_home, check=False)
        self.assertEqual(list(self.codex_home.glob(".AGENTS-*")), [])

    def test_check_does_not_create_files_and_install_is_idempotent(self):
        self.run_sync("--check", expected=1)
        self.assertFalse(self.codex_home.exists())
        self.run_sync(explicit_home=False)
        installed = self.target.read_bytes()
        self.run_sync("--check")
        self.run_sync()
        self.assertEqual(self.target.read_bytes(), installed)
        self.assertEqual(list(self.codex_home.glob("AGENTS.md.backup-*")), [])

    def test_repository_rules_install_from_the_canonical_source(self):
        rules = (REPO / "instructions" / "AGENTS.md").read_text(encoding="utf-8")
        self.source.write_text(rules, encoding="utf-8")
        self.run_sync()
        self.run_sync("--check")
        installed = self.target.read_text(encoding="utf-8")
        self.assertIn(rules.rstrip(), installed)
        self.assertEqual(installed.count(BEGIN), 1)
        self.assertEqual(installed.count(END), 1)

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

    def test_source_installation_markers_are_rejected_before_writing(self):
        for content in (BEGIN, END, BEGIN + "\n# Shared\n" + END):
            with self.subTest(content=content):
                self.source.write_text(content, encoding="utf-8")
                self.run_sync(expected=2)
                self.run_sync("--check", expected=2)
                self.assertFalse(self.codex_home.exists())

    def test_inline_marker_mentions_do_not_replace_local_prose(self):
        for content in (
            f"Use `{BEGIN}` to start.\nKeep this rule.\nUse `{END}` to finish.\n",
            f" {BEGIN}\nKeep this rule.\n{END}\n",
            f"{BEGIN}\nKeep this rule.\n{END} trailing prose\n",
        ):
            with self.subTest(content=content):
                original = content.encode()
                self.write_target(original)
                self.run_sync(expected=2)
                self.assertEqual(self.target.read_bytes(), original)
                self.assertEqual(list(self.codex_home.glob("AGENTS.md.backup-*")), [])

    def test_crlf_update_preserves_local_bytes_and_has_stable_source_digest(self):
        prefix = b"# Local before\r\nKeep this.\r\n\r\n"
        suffix = b"\r\n\r\n# Local after\r\nKeep this too.\r\n"
        original = prefix + f"{BEGIN}\r\nOld shared rules.\r\n{END}".encode() + suffix
        self.write_target(original)
        rules = self.source.read_text(encoding="utf-8").encode("utf-8")
        self.source.write_bytes(rules.replace(b"\n", b"\r\n"))
        crlf_result = self.run_sync()
        installed = self.target.read_bytes()
        expected = prefix + f"{BEGIN}\n".encode() + rules.rstrip() + b"\n" + END.encode() + suffix
        self.assertEqual(installed, expected)
        self.assertEqual(next(self.codex_home.glob("AGENTS.md.backup-*")).read_bytes(), original)
        self.source.write_bytes(rules)
        lf_result = self.run_sync("--check")
        def digest_line(result):
            return next(line for line in result.stdout.splitlines() if line.startswith("Rules SHA-256:"))

        self.assertEqual(digest_line(crlf_result), digest_line(lf_result))
        self.assertEqual(self.target.read_bytes(), installed)

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

    def test_unrelated_symlink_and_its_destination_are_preserved(self):
        self.codex_home.mkdir(parents=True)
        other = self.fixture / "host-local.md"
        original = b"# Host-specific instructions\nKeep this.\n"
        other.write_bytes(original)
        try:
            self.target.symlink_to(other)
        except OSError as error:
            self.skipTest(str(error))
        self.run_sync(expected=2)
        self.run_sync("--check", expected=2)
        self.assertTrue(self.target.is_symlink())
        self.assertEqual(other.read_bytes(), original)
        self.assertEqual(list(self.codex_home.glob("AGENTS.md.backup-*")), [])

    def test_concurrent_local_edit_is_preserved(self):
        original = b"# Local\nOriginal rule.\n"
        edited = original + b"A new host-local rule.\n"
        self.write_target(original)
        self.run_sync_with_concurrent_change(lambda: self.target.write_bytes(edited))
        self.assertEqual(self.target.read_bytes(), edited)
        self.assertEqual(next(self.codex_home.glob("AGENTS.md.backup-*")).read_bytes(), original)

    def test_concurrent_creation_is_preserved(self):
        edited = b"# Newly created local instructions\n"
        self.run_sync_with_concurrent_change(lambda: self.target.write_bytes(edited))
        self.assertEqual(self.target.read_bytes(), edited)
        self.assertEqual(list(self.codex_home.glob("AGENTS.md.backup-*")), [])

    def test_concurrent_directory_replacement_is_preserved(self):
        self.write_target(b"# Local\nOriginal rule.\n")

        def replace_with_directory():
            self.target.unlink()
            self.target.mkdir()

        self.run_sync_with_concurrent_change(replace_with_directory)
        self.assertTrue(self.target.is_dir())

    def test_concurrent_symlink_replacement_is_preserved(self):
        original = b"# Local\nOriginal rule.\n"
        self.write_target(original)
        other = self.fixture / "host-local.md"
        other.write_bytes(b"Keep the symlink destination.\n")
        probe = self.fixture / "symlink-probe"
        try:
            probe.symlink_to(other)
        except OSError as error:
            self.skipTest(str(error))
        probe.unlink()

        def replace_with_symlink():
            self.target.unlink()
            self.target.symlink_to(other)

        self.run_sync_with_concurrent_change(replace_with_symlink)
        self.assertTrue(self.target.is_symlink())
        self.assertEqual(other.read_bytes(), b"Keep the symlink destination.\n")


if __name__ == "__main__":
    unittest.main()
