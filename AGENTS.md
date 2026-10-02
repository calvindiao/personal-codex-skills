# Working in this repository

This repository contains portable skill packages and shared Codex communication preferences.

## Map

- `README.md`: human entry point; `docs/install.md`: installation, updates, recovery.
- `instructions/AGENTS.md`: canonical shared preferences. This root file is only for maintaining the repository and is never installed globally.
- Top-level `<skill-name>/SKILL.md`: independently usable skill packages. Keep existing paths stable; installed symlinks may point here.
- `scripts/sync-instructions.py`: explicit, standard-library-only installer. Its marked block is repo-owned; content outside it is host-owned.
- `scripts/validate.py` and `tests/`: structural checks and isolated filesystem tests.
- Read `docs/design.md` when changing boundaries or layout; `docs/maintaining.md` when adding skills or changing validation.

## Changes and checks

Keep skill descriptions precise and entry points short. Add references or scripts when a concrete workflow needs them; a simple skill can remain one file. Put Codex-specific UI metadata in `agents/openai.yaml` and keep portable instructions self-contained.

Preserve existing installation paths, CLI flags, host-local instructions, and backup behavior unless the requested change includes a migration. Edit shared rules at their source; installed markers do not belong in that source.

Runtime sync needs Python 3.10+ and the standard library. Development checks use `requirements-dev.txt`:

```sh
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
```

Choose checks that address the change. Skill behavior changes need representative tasks, including a near miss, rather than only format checks. Local tests use disposable fixtures and can be run without separate approval. PRs, plans, delegation, and full-suite reruns are choices for the task, not universal prerequisites.
