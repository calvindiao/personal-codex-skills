# Personal Codex skills

This Git repository is the source of truth for my personal Codex skills. Each skill is a top-level directory containing `SKILL.md`. Keep account credentials, machine-specific configuration, and private project data out of this public repository.

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

Restart Codex if the skill does not appear automatically. GitHub authentication is needed only when pushing changes.

If `$HOME/.agents/skills` already contains other skills, clone this repository elsewhere and link its individual skill directories into `$HOME/.agents/skills`. On macOS/Linux use `ln -s`; on Windows use a PowerShell directory junction (`New-Item -ItemType Junction`). Do not replace an existing skill with the same name without reviewing it.

## Keep computers in sync

Before editing a skill, run `git pull --ff-only` in the clone. After editing, review the diff, commit, and push. On each other computer, run `git pull --ff-only` in its clone. Git records changes and transports them; Codex does not sync these local files through account sign-in.
