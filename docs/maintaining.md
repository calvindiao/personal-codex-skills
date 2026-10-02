# Maintenance guide

Identify the intended change, then edit the relevant files. Most changes do not need updates to every layer.

| Change | Location | Relevant checks |
| --- | --- | --- |
| Communication preferences | `instructions/AGENTS.md` | Preserve meaning; install and check in a temporary directory |
| Skill triggers or task guidance | The package's `SKILL.md` | Format, references, representative tasks, and near misses |
| Material needed only in a specific mode | Package `references/` | Discoverability from the entry point and valid references |
| Repeatable operations needing deterministic execution | Package `scripts/` | Run isolated inputs and inspect actual output |
| Sync and file operations | Repository `scripts/` and `tests/` | Preserve existing content; check conflicts, repeated runs, and recovery |
| Installation steps or directory conventions | README, `docs/`, and root `AGENTS.md` | Commands, links, and effects on existing installations |

## Add or change a skill

Place new packages at top-level `<skill-name>/`. The directory name must match the frontmatter's `name`. This repository recommends lowercase ASCII letters, digits, and hyphens for readable cross-platform paths. State what the skill does and when it applies. Explain near misses only when incorrect triggering is a realistic problem.

```yaml
---
name: explain-query-plans
description: Explain database query plans when diagnosing a slow query or comparing an index change.
---
```

The body provides goals, key judgments, and necessary constraints. Do not repeat general knowledge the model already has. Add scripts, examples, references, or assets when they have a clear purpose. References should be reachable directly from the entry point, and the package should remain usable when copied elsewhere.

Keep installation paths, accounts, private project data, and host-specific settings out of reusable packages. State the compatibility scope of client-specific fields. Review third-party skills and their licenses before copying content.

## Run deterministic checks

Use Python 3.10+ to create an isolated development environment. Skip creation if `.venv` already exists. macOS / Linux:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/validate.py
.venv/bin/python -m unittest discover -s tests -v
```

Windows PowerShell:

```powershell
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe scripts/validate.py
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The validator checks actual skill packages: YAML, names, required fields, and local Markdown references in each entry point's body. It does not check raw HTML links, anchors, remote pages, factual accuracy, or task quality. Directory, length, and style recommendations are not mechanical scoring rules.

Sync tests use temporary directories. They cover preservation of existing instructions, repeated runs, backups, overrides, symlinks, CRLF, and concurrent changes. Runtime sync still needs only the standard library. See `.github/workflows/checks.yml` for the CI matrix and versions. Report a specific commit and run; configuring CI does not mean it passed.

## Check actual skill behavior

When triggers or task guidance change, select a few representative tasks and include similar tasks that should not trigger the skill. Observe completion, matching evidence, and unnecessary steps. Wording changes alone do not require expensive evaluation reruns.

For `evidence-led-engineering`, examples include:

| Sample prompt | Expected behavior |
| --- | --- |
| "Investigate duplicate submissions, reproduce the issue, and fix it" | Find observable failure and its cause; repeat relevant checks after the fix |
| "Review the cause only; do not change files yet" | Provide an evidence-backed investigation and respect the read-only scope |
| "Local tests passed. Does that prove production recovered?" | Distinguish local tests from production behavior and seek relevant evidence |
| "Fix one typo in the README" | Complete the small edit directly without a full investigation workflow |
| "Explain what a Git branch is" | Give an ordinary explanation without requiring repository scans or tests |
| "The fix and release are already authorized; complete them" | Finish the authorized work without adding repeated confirmation requirements |

For comparisons, use the same input with the old and new versions, or with and without the skill. Record the date, model, skill commit, input, actual result, and judgment. Format checks or one agent's self-assessment cannot establish general improvement. Use isolated samples; real releases, communication, and paid calls follow the current task's authorization.

## Releases and compatibility

Choose the merge and release approach for the task. Before publishing, review relevant checks, the diff, and compatibility with existing installations. Record an identifiable Git commit. Document migration and rollback when stable paths or CLI behavior change.

Development dependencies are pinned in `requirements-dev.txt`, and CI actions are pinned to commits. Run relevant tests when updating them. Preserve coverage of the minimum Python version and all three operating systems.

After shared preferences change, each host must pull and rerun the installer. Linked skills follow clone updates; copied skills need their own updates. Never install the root `AGENTS.md` or all human documentation as global instructions.
