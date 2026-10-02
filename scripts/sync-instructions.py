#!/usr/bin/env python3
"""Install the repository's communication rules without replacing local rules."""

import argparse
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile


SOURCE = Path(__file__).resolve().parent.parent / "instructions" / "AGENTS.md"
BEGIN = "<!-- BEGIN personal-codex-skills:communication -->"
END = "<!-- END personal-codex-skills:communication -->"


def merged_content(original, rules):
    block = f"{BEGIN}\n{rules.rstrip()}\n{END}"
    starts, ends = original.count(BEGIN), original.count(END)
    if starts == ends == 0:
        # Migrate an existing standalone copy of these same rules once.
        if original.replace("\r\n", "\n").strip() == rules.strip():
            original = ""
        separator = "\n\n" if original else ""
        return original + separator + block + "\n"
    if starts != 1 or ends != 1:
        raise ValueError("Managed block markers are missing or duplicated; no changes made.")
    start = original.index(BEGIN)
    end = original.index(END)
    if end < start:
        raise ValueError("Managed block markers are reversed; no changes made.")
    return original[:start] + block + original[end + len(END):]


def sync(codex_home, check):
    rules = SOURCE.read_text(encoding="utf-8")
    if not rules.strip():
        raise ValueError("The source rules file is empty; no changes made.")
    digest = hashlib.sha256(rules.encode("utf-8")).hexdigest()
    target = codex_home / "AGENTS.md"
    override = codex_home / "AGENTS.override.md"
    if override.is_file() and override.read_bytes().strip():
        raise ValueError(
            f"{override} is active and would override AGENTS.md. "
            "Merge the communication rules into that file or remove the override first."
        )
    if target.is_symlink():
        if target.resolve() != SOURCE:
            raise ValueError(f"{target} links to another file; no changes made.")
        print(f"Current (linked): {target}\nRules SHA-256: {digest}")
        return 0

    existed = target.exists()
    original_bytes = target.read_bytes() if existed else b""
    updated = merged_content(original_bytes.decode("utf-8"), rules).encode("utf-8")
    if original_bytes == updated:
        print(f"Current: {target}\nRules SHA-256: {digest}")
        return 0
    if check:
        print(f"Out of date: {target}\nExpected rules SHA-256: {digest}")
        return 1

    codex_home.mkdir(parents=True, exist_ok=True)
    backup = None
    if existed:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup = target.with_name(f"AGENTS.md.backup-{stamp}")
        shutil.copy2(target, backup)
    mode = stat.S_IMODE(target.stat().st_mode) if existed else 0o600
    descriptor, temporary = tempfile.mkstemp(prefix=".AGENTS-", dir=codex_home)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(updated)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, target)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    print(f"Updated: {target}\nRules SHA-256: {digest}")
    if backup:
        print(f"Backup: {backup}")
    print("Start a new Codex session to load the updated instructions.")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check only; do not write files.")
    parser.add_argument(
        "--codex-home", type=Path,
        default=Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex"),
        help="Codex home directory (default: CODEX_HOME, or ~/.codex).",
    )
    args = parser.parse_args()
    try:
        return sync(args.codex_home.expanduser().absolute(), args.check)
    except (OSError, ValueError, UnicodeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
