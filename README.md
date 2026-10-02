# Personal Codex skills

[![Checks](https://github.com/calvindiao/personal-codex-skills/actions/workflows/checks.yml/badge.svg)](https://github.com/calvindiao/personal-codex-skills/actions/workflows/checks.yml)

Reusable agent skills and personal communication preferences, with one shared source for Codex across projects and hosts.

Skills provide task-specific judgment. Communication preferences stay short. Load what the task needs and leave room for the agent to choose its approach.

## What's included

| Content | Purpose | When to read |
| --- | --- | --- |
| [Evidence-led Engineering](evidence-led-engineering/SKILL.md) | Use observable behavior to assess investigations, changes, and release checks | Engineering tasks that need evidence; skip trivial edits |
| [Communication preferences](instructions/AGENTS.md) | Answer first, use consistent terms, and preserve conditions and uncertainty | Loaded as global Codex instructions after installation |
| [Repository guidance](AGENTS.md) | Help agents find the right files and checks | When working in this repository |

`SKILL.md` uses the open Agent Skills format. The installation guide and global instruction sync tool currently target Codex. Follow each client's documentation for Claude and other clients' installation paths and extension fields.

## Already installed: update and check

Open your existing clone. Confirm that Git finishes pulling successfully before running the sync script.

macOS / Linux:

```sh
git pull --ff-only
python3 scripts/sync-instructions.py
python3 scripts/sync-instructions.py --check
```

Windows PowerShell:

```powershell
git pull --ff-only
py -3 scripts/sync-instructions.py
py -3 scripts/sync-instructions.py --check
```

If the `py` launcher is unavailable, use your installed `python`. You need Git and Python 3.10+. The sync script needs no third-party Python packages.

A skill linked to this clone uses the updated source after a pull. A copied skill needs its own update. Run the sync script to update global communication preferences. Start a new Codex conversation after installation or an update to confirm loading.

**First installation or another host:** follow the [installation, migration, and recovery guide](docs/install.md). It covers existing skill directories, Windows, WSL, remote hosts, and custom `CODEX_HOME` values.

## What the sync tool does

- Adds or updates a marked communication preferences block in the global `AGENTS.md`.
- Preserves host-specific instructions outside that block and saves a timestamped backup before changing an existing file.
- Provides a read-only check against the current clone and prints the rules' SHA-256.
- Reports active overrides, unrelated symlinks, damaged markers, and detected file changes during sync.

The repository owns the shared block. Edit shared preferences in `instructions/AGENTS.md`; keep host-specific instructions outside the block. Run sync explicitly on each host. It is not a background service.

Matching files, loaded instructions, and improved task behavior are three separate checks. The script checks file consistency. Confirm loading in a new conversation and assess behavior through real tasks.

## Repository layout

```text
AGENTS.md                       Repository guidance; never installed globally
README.md                       Human entry point
instructions/AGENTS.md          Single source for shared communication preferences
evidence-led-engineering/        Independent skill package; stable installation path
  SKILL.md                      Scope and task guidance
  agents/openai.yaml            Optional Codex UI metadata
docs/                           Installation, design decisions, and maintenance
scripts/                        Explicit sync and structural validation tools
tests/                          Isolated filesystem tests
.github/workflows/checks.yml     CI checks on macOS, Linux, and Windows
```

Add skills as sibling `<skill-name>/SKILL.md` packages. Add `references/`, `scripts/`, or `assets/` only when needed. The existing skill is short and self-contained, without a separate routing layer.

## Changes and validation

Normal use requires installation or updates. When changing the structure, scripts, or skills, choose relevant checks from the [maintenance guide](docs/maintaining.md).

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/validate.py
.venv/bin/python -m unittest discover -s tests -v
```

These are macOS / Linux development commands. See the [maintenance guide](docs/maintaining.md#run-deterministic-checks) for Windows commands. Structural validation uses PyYAML and a CommonMark parser. Neither is a sync runtime dependency. Tests use temporary directories without accessing real accounts or changing real Codex configuration.

CI checks format, references, and script behavior. It does not replace task-based skill evaluation. [Design decisions and sources](docs/design.md) explain how this repository applies OpenAI, Anthropic, and Agent Skills guidance, including compatibility limits.
