# Plan: Update the engine status wording when engine 1.0.0 ships (issue #6)

Risk tier: Low. Wording changes to Markdown pages, the theme notice, and contributor docs. No build configuration or workflow changes; the strict build covers links.

Domain skills: none applicable. The change is plain Markdown and one HTML template line; no framework, UI, API, data, auth, payments, or email code is touched.

Engine 1.0.0 is published (PyPI `openpickleball-engine==1.0.0`, tag `v1.0.0` at `be2a0ff`). Its wording, settled in openpickleball/engine#161 and shipped in its README and `src/open_engine/_version.py`: the engine is the reference implementation of the OPEN rating method, its outputs are not OPEN ratings, do not use it to rate real players, and no OPEN rating is live. It was evaluated on one club's closed pool, and a forthcoming report describes the evaluation. Parameter set `v1` is loaded explicitly with `Config.published("v1")`; the `Config()` defaults remain placeholders.

## Acceptance criteria

1. No page under `docs/`, no line of `overrides/main.html`, and no line of `README.md` calls the engine or its output a "demonstration" (checked with `grep -rni demonstrat docs overrides README.md`, which must print nothing).
2. The site and README call the engine the "reference implementation" of the OPEN rating method, say its outputs are not OPEN ratings, and say no OPEN rating is live. Nothing says or implies that ratings are validated or live.
3. Home's status box no longer says the engine's methods "have not been validated on real match data". It says the engine was evaluated on one club's closed pool and that a forthcoming report describes the evaluation, matching the engine's README.
4. Home's "What exists today" no longer says the engine has only a dev release on TestPyPI. It says 1.0.0 is on PyPI, installed with `pip install openpickleball-engine`, and that parameter set `v1` loads with `Config.published("v1")`.
5. The contributor guidance (`CLAUDE.md` hard rule 2 and its `overrides/main.html` line, `CONTRIBUTING.md`) names the status notice and the new wording instead of "demonstration ratings".
6. Hard rules hold: no real player data, no names of other rating systems, nothing loaded from another host.
7. `uv run mkdocs build --strict` passes.

## Files that change

- `README.md`: project status line.
- `overrides/main.html`: announcement bar text.
- `docs/index.md`: status box and the engine bullet under "What exists today".
- `docs/architecture.md`: last sentence of the Engine section.
- `docs/stack.md`: the engine's Releases row, which still says TestPyPI only.
- `docs/match-to-rating.md`: the diagram label under "ratings", the Ratings API paragraph, and the Evaluation section's status line.
- `CLAUDE.md`, `CONTRIBUTING.md`: the notice rule.

## Order of work

1. Commit this plan alone.
2. Edit the files above, run the strict build and the grep checks, commit.

## Risks

- Overclaiming: saying the engine is validated. Mitigation: copy the engine's own phrases ("reference implementation", "evaluated on one club's closed pool", "not OPEN ratings", "no OPEN rating is live").
- "Provisional" already means a live update between replays on this site. Do not reuse the word for the engine's pool caveat; state the caveat directly instead.
- The ASCII diagram in `match-to-rating.md` must stay aligned.
- PR #5 (engine-rating-details) touched `docs/index.md`, `docs/match-to-rating.md`, and `docs/glossary.md`. It merged into `main` (`13775b0`) before this branch's work, so this branch is based on it and only the status lines change in those pages.

## Proof

- Criterion 1: `grep -rni demonstrat docs overrides README.md` prints nothing after the change. On `main` (`13775b0`) it prints 6 lines across README.md, overrides/main.html, docs/index.md, docs/architecture.md, and docs/match-to-rating.md.
- Criteria 2 to 6: read the diff; `grep -rniE "validated|TestPyPI" docs` shows no claim that ratings are validated.
- Criterion 7: `uv run mkdocs build --strict` output.
- Live drive: build the site and grep the rendered HTML in `site/` for the new announcement text on every page.
