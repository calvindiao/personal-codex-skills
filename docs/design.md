# Design decisions and sources

The design supports stable reuse, easy discovery, and reading content when needed. These are repository design choices, not a fixed workflow for every task.

## Content boundaries

| Layer | Source | Use |
| --- | --- | --- |
| Personal communication preferences | `instructions/AGENTS.md` | Install a small set of cross-task preferences on each host |
| Task capabilities | Top-level `<skill-name>/SKILL.md` | Discover by name and description; read the body when relevant |
| Repository maintenance | Root `AGENTS.md` | Navigate repository changes; never install globally |
| Human guidance | README and `docs/` | Consult for installation, troubleshooting, or design changes |
| Deterministic tools | `scripts/` | Explicitly run file sync and structural checks |

Skill directories are the source of truth. Validation scans the actual `SKILL.md` files. There is no separate registry duplicating names, descriptions, and paths. Codex UI metadata stays in each package's `agents/openai.yaml`, separate from portable task guidance.

## Stable paths and update boundaries

Top-level skill directories remain stable because existing symlinks or junctions may point to them. Moving a directory requires migration steps and installation checks, beyond checking links inside the repository.

Git transfers versions. The installer updates global preferences. The repository owns the shared block; the host owns content outside it. `--check` confirms consistency with the local clone. It does not establish whether that clone is current with the remote or whether an agent loaded the instructions.

The sync script uses the Python standard library and preserves existing commands and markers. YAML and CommonMark parsers are development dependencies only. They avoid errors from handwritten parsers. CI uses temporary directories to cover filesystem behavior across operating systems without touching a real Codex home directory.

## Keep instruction overhead low

Descriptions state capabilities and trigger boundaries. Bodies contain task goals, key judgments, and actual constraints. Split long material into directly reachable references when there is a concrete need. A short skill can remain one file; empty directories and routing files are unnecessary.

Give agents room to choose methods for exploratory work. Use scripts for repeatable operations that can damage data. Plans, PRs, multiple agents, and broader testing depend on the task. Address a specific failure with a targeted correction before turning it into a permanent rule for every task.

## Sources and how they apply

| Source | Principle used here |
| --- | --- |
| [OpenAI: Build skills](https://learn.chatgpt.com/docs/build-skills) | Distinguish discovery, loading, and execution; use clear descriptions and load resources as needed |
| [OpenAI: Rethinking skills and prompts](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra) | Keep entry points short; avoid mandatory document sweeps and fixed workflows for every task |
| [OpenAI: Testing skills with evals](https://developers.openai.com/blog/eval-skills) | Assess task outcomes and near misses; passing format checks does not establish effectiveness |
| [Anthropic: Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) | Match freedom to task fragility, disclose content progressively, and iterate from observed behavior |
| [Claude Code: Skills](https://code.claude.com/docs/en/skills) | Separate portable content from client extensions and follow each client's installation guidance |
| [Agent Skills specification](https://agentskills.io/specification) | Apply metadata constraints such as `name` and `description`; keep packages independently usable |
| [Community discussion: Allow skills to serve humans too](https://github.com/agentskills/agentskills/discussions/390) | Provide a separate human entry point; treat the discussion as a proposal, not a runtime standard |

Separate specification requirements from writing recommendations. Name lengths and required fields are format constraints. Keeping a skill under 500 lines is authoring guidance, not an automatic failure condition here.

## Compatibility and validation scope

Portable skill content follows the Agent Skills format. Claude Code extensions such as `context` and dynamic command injection are not guaranteed to work in other clients. This repository's global instruction installer targets Codex. Following official examples does not establish runtime compatibility with every client.

Validation has three layers: format and references, installer behavior, and real task outcomes. CI covers the first two. When skill behavior changes, choose representative tasks for the third. Revisit rules when clients or models change, or when actual failures reveal a problem. Remove constraints that no longer help.
