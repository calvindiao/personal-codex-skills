# Personal Codex skills

This Git repository is the source of truth for my personal Codex skills and shared communication instructions. Each skill is a top-level directory containing `SKILL.md`. Shared instructions live in `instructions/AGENTS.md`. Keep account credentials, machine-specific configuration, and private project data out of this repository.

## First setup on another computer

Codex discovers personal skills under `$HOME/.agents/skills`. If that directory does not already exist, clone the repository directly there.

macOS or Linux:

```sh
mkdir -p "$HOME/.agents"
git clone https://github.com/calvindiao/personal-codex-skills.git "$HOME/.agents/skills"
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force "$HOME\.agents" | Out-Null
git clone https://github.com/calvindiao/personal-codex-skills.git "$HOME\.agents\skills"
```

Authenticate with GitHub when accessing a private clone or pushing changes. Restart Codex if the skill does not appear automatically.

If `$HOME/.agents/skills` already contains other skills, clone this repository elsewhere and link its individual skill directories into `$HOME/.agents/skills`. On macOS/Linux use `ln -s`; on Windows use a PowerShell directory junction (`New-Item -ItemType Junction`). Do not replace an existing skill with the same name without reviewing it.

## Keep computers in sync

Before editing a skill or shared instructions, run `git pull --ff-only` in the clone. After editing, review the diff, commit, and push. On each other computer, run `git pull --ff-only` in its clone. Git records changes and transports them; account sign-in is not proof that these local files are synchronized.

## Install shared communication instructions

Run these commands from this repository's clone on each computer that actually runs Codex. The installer needs Python 3 and only uses its standard library. Skills are discovered as needed; global `AGENTS.md` instructions apply across projects.

macOS or Linux:

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

If Windows has Python on `PATH` but not the `py` launcher, use `python` instead of `py -3`.

The installer uses `CODEX_HOME` when set, otherwise the current user's `.codex` directory. It adds or updates one marked communication block in `AGENTS.md`, preserves other instructions, and saves a timestamped backup before changing an existing file. An existing standalone copy of the same shared rules is migrated without duplication. It reports an active `AGENTS.override.md` or an unrelated symlink instead of silently changing them.

Repeat the install command after pulling changes to `instructions/AGENTS.md`. Pulling the repository alone does not update an installed copy. For an SSH or Remote chat, install on the execution host under the account running Codex. Windows and WSL have separate user directories.

`--check` never writes files. Exit code 0 means the shared block matches this clone's source; 1 means installation or an update is needed; 2 means a file error or conflict needs attention. The printed rules SHA-256 can be compared across hosts. A matching hash only proves agreement with the local clone, so pull the intended Git revision first.

Start a new Codex session after installation. Ask it to list the instruction sources it loaded and summarize the communication rules. Project instructions can override conflicting global guidance. See the [official AGENTS.md documentation](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

## Check the installer

```sh
python3 -m unittest discover -s tests -v
```
