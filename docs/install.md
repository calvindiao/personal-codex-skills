# Installation, updates, and recovery

Run these commands on the host and under the user account that runs Codex. Install Git and Python 3.10+ first.

## Existing installations

Keep your existing clone and skill paths. Run the README's update commands from that clone. Do not reinstall the same skill just to match the new directory examples.

Earlier installations may have cloned the whole repository into `~/.agents/skills` or linked a single skill into `~/.codex/skills`. This repository keeps top-level skill paths compatible with those installations. The current recommended personal skill directory is `~/.agents/skills`. Skills with the same name in multiple discovery directories may appear more than once; confirm the source actually loaded. [Official Codex guidance](https://learn.chatgpt.com/docs/build-skills)

If the old installation copied a skill directory, pulling Git updates the clone but not that copy. Compare and preserve local changes before updating the copy or replacing it with a link. Do not overwrite unknown content.

## New host: clone into a working directory

Choose a stable location for the repository. This example uses `~/src`. Keeping the clone separate from the personal skill discovery directory makes it easier to install skills from other sources.

macOS / Linux:

```sh
mkdir -p "$HOME/src"
git clone https://github.com/calvindiao/personal-codex-skills.git "$HOME/src/personal-codex-skills"
cd "$HOME/src/personal-codex-skills"
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force "$HOME\src" | Out-Null
git clone https://github.com/calvindiao/personal-codex-skills.git "$HOME\src\personal-codex-skills"
Set-Location "$HOME\src\personal-codex-skills"
```

If a step fails, resolve that error before continuing.

## Install the skills you need

Run these commands from the clone's root. They link only `evidence-led-engineering`. If the target already exists, first check whether it points to this repository.

macOS / Linux:

```sh
mkdir -p "$HOME/.agents/skills"
skill_target="$HOME/.agents/skills/evidence-led-engineering"
if [ -e "$skill_target" ] || [ -L "$skill_target" ]; then
  printf 'Existing installation; inspect before changing: %s\n' "$skill_target"
else
  ln -s "$PWD/evidence-led-engineering" "$skill_target"
fi
```

Windows PowerShell uses a directory junction:

```powershell
New-Item -ItemType Directory -Force "$HOME\.agents\skills" | Out-Null
$skillSource = Join-Path (Get-Location) "evidence-led-engineering"
New-Item -ItemType Junction -Path "$HOME\.agents\skills\evidence-led-engineering" -Target $skillSource
```

Codex supports linked skill directories. Git updates the linked source directly, so keep the clone in place. If linking is unavailable, copy the whole skill package and explicitly update that copy later. [Discovery and symlink guidance](https://learn.chatgpt.com/docs/build-skills)

## Install shared communication preferences

macOS / Linux:

```sh
python3 scripts/sync-instructions.py
python3 scripts/sync-instructions.py --check
```

Windows PowerShell:

```powershell
py -3 scripts/sync-instructions.py
py -3 scripts/sync-instructions.py --check
```

Use `python` if the `py` launcher is unavailable. The script reads `CODEX_HOME`, falling back to the current user's `.codex` directory. Use `--codex-home /path/to/profile` to select a target explicitly. It copies communication preferences only, not login information, MCP configuration, or other host settings.

| Exit code | Meaning | Next step |
| --- | --- | --- |
| `0` | Installation completed, or shared content matches the current clone | Confirm loading in a new conversation |
| `1` | `--check` found a missing installation or different content | Confirm the Git version, then run installation |
| `2` | A file, permission, override, link, or marker needs attention | Follow the specific error and retry |

An active `AGENTS.override.md` takes precedence over `AGENTS.md`. The sync script reports this as an error. Depending on the host's needs, merge shared preferences into the override or disable an override you no longer need before installing. Manual merges into an override are outside the script's management scope. [Global instruction loading order](https://learn.chatgpt.com/docs/agent-configuration/agents-md)

## Confirm that it works

1. Run `git rev-parse HEAD` in each clone to confirm the intended Git version.
2. Run `--check` and compare the rules' SHA-256. It checks shared preferences; other host instructions may differ.
3. Start a new Codex conversation. Ask it to identify loaded instruction sources, confirm the communication preferences, and check that the required skill is available.

Project instructions can override conflicting global instructions. A terminal, desktop app, or remote service may use a different account or `CODEX_HOME`; check the actual execution environment. Windows and WSL have separate user directories.

## Update, roll back, or remove

**Update:** run `git pull --ff-only` in the clone. After a successful pull, rerun instruction sync and check. Hosts that need a fixed version can check out a tested commit before syncing, then choose a new version when upgrading.

**Restore preferences:** before changing an existing file, the installer prints an `AGENTS.md.backup-<timestamp>` path. Compare the backup with the current file. Preserve host instructions added since installation, then restore the content you need. The first installation creates no backup if no file existed.

**Remove shared preferences:** delete the entire block marked `personal-codex-skills:communication` from the global file. Preserve content outside it. To remove a skill, delete its installation link or copy. Keep the repository source if it is still needed.

Avoid editing the same global file concurrently with an editor or another sync program. The script detects concurrent changes on a best-effort basis and replaces files atomically. It does not coordinate transactions among multiple writers.
