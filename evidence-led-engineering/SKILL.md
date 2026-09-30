---
name: evidence-led-engineering
description: Use for substantial repository investigations, bug fixes, features, refactors, and release checks that need evidence of actual behavior. Route by task type and verify at the relevant runtime layer; skip trivial edits.
---

# Evidence-led engineering

Make each engineering conclusion traceable to an observation. Apply the smallest method that can establish the requested outcome. Keep the user's requested stage and the repository's instructions in scope.

## Establish the target

- Identify the observable outcome, the surface where it matters, and the cheapest credible check. For a defect or performance claim, capture the current behavior before changing it.
- Inspect the actual checkout, relevant callers, configuration, and repository instructions. Treat reviews and prior reports as hypotheses until they match the current code or runtime.
- Settle measurable forks with a focused inspection or experiment. Ask the user about preferences or requirements that evidence cannot determine.

## Choose a route

- **Investigation:** Trace the relevant data and control flow. Return what was observed, what was inferred, and what remains unverified. A read-only request ends with an answer.
- **Bug fix:** Reproduce the symptom on its real surface. Narrow competing causes with logs, state inspection, or a focused test. Change the confirmed mechanism, then repeat the original reproduction. If it cannot be reproduced, say what was tried and avoid presenting a speculative guard as a verified fix.
- **Feature or refactor:** Define the user-visible behavior and the data shape or invariant that carries it. Follow existing boundaries and make the smallest coherent change. For stateful logic, represent valid states explicitly; for a refactor, compare behavior before and after. Prototype only when observing alternatives will resolve a meaningful design uncertainty.
- **Release check:** Match the exact source revision to the built or running artifact. Check the target environment and user-facing behavior that the request names. Report local validation, CI, preview, deployment, and real-world acceptance as distinct states.

## Prove the result

- Verify on the same surface as the claim. Use a targeted test for code behavior, an interactive run for UI behavior, and live runtime evidence for deployment claims. A build or green CI result proves only its own gate.
- Make tests assert an outcome a caller can observe. Add a test or reusable check when it protects a real failure mode or makes a complex result repeatable; keep one-off, low-impact edits light.
- Inspect the final diff for unrelated changes, duplicated logic, stale paths, and assumptions the evidence did not support. If repeated fixes fail the same check, reconsider the underlying premise before adding another patch.
- When explicitly asked to use parallel agents, first define a check that each unit can pass, split along independent artifacts, and personally verify the integrated result. Do not make parallelism a default.

Report what changed or was learned, the exact evidence for the conclusion, and any material gap. Finishing one requested stage does not imply authorization to start another.
