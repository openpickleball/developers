# CLAUDE.md

This file gives Claude Code guidance for working in this repository.

## What this repository is

The developer site for OPEN, the Open Pickleball Evaluation Network, served at [dev.openpb.org](https://dev.openpb.org). It explains how OPEN works for a technical audience: the architecture, the tech stack, and how a match becomes a rating. It is a static site built with [Zensical](https://zensical.org), using its `classic` theme variant, and deployed to GitHub Pages. It holds no application code.

- `docs/`: the site's pages. Every page is listed in `nav` in `mkdocs.yml`.
- `overrides/main.html`: the theme override that shows the site-wide status notice.
- `mkdocs.yml`: site configuration, which Zensical reads. `validation` makes `--strict` fail on links to missing pages and missing anchors.
- `scripts/check_docs.py`: fails on a page missing from `nav`, a `nav` entry that is not a file in `docs/`, an absolute link, a link to a directory, or a relative link to a missing file. CI runs it before the build. Its tests are in `tests/`.
- `plans/`: plans recorded for issues before their work lands, named `YYYY-MM-DD-issue-<N>-<slug>.md`. They live outside `docs/` so the site does not publish them.
- `.github/workflows/pages.yml`: the tests, the check script, and the strict build on every pull request, and the deploy to Pages on a push to `main`.
- `.github/workflows/dco.yml`: the `sign-off` check on pull requests.
- `.github/workflows/scorecard.yml`: OpenSSF Scorecard.

## Commands

```bash
uv sync
uv run zensical serve                # preview at http://localhost:8000
uv run pytest                        # tests for the check script
uv run python scripts/check_docs.py  # nav coverage and link targets
uv run zensical build --strict       # the same build CI runs
```

Dependencies are pinned in `pyproject.toml` and locked in `uv.lock`. CI runs `uv sync --locked`, so update the lock with `uv lock` whenever `pyproject.toml` changes. GitHub Actions are pinned by commit SHA with the version in a comment; keep that form when Dependabot or a contributor bumps one.

The `build` job in `pages.yml` and the `sign-off` job in `dco.yml` are required status checks on `main`. Renaming either job must also update the "Protect main" ruleset.

## Hard rules

1. **No real player data, anywhere.** Use made-up names and OPEN Codes, such as `P-7K3M-QX9H`.
2. **Keep the status notice.** No OPEN rating is live. The engine is the reference implementation of the OPEN rating method, and its outputs are not OPEN ratings. Never say or imply that ratings are validated or live. Keep the announcement bar and the status section on Home, and match their wording to the engine's latest release.
3. **Do not name competing rating systems.** Say "standard external rating system".
4. **Check every claim against the repository it describes, on `main`.** Mark each step of how a match becomes a rating as implemented or planned.
5. **Link decisions, do not copy them.** Link the backend's ADRs and `CONTEXT.md`, the rating spec, and each repository's guides. A one-sentence summary is fine.
6. **Load nothing from another host.** No web fonts, CDN scripts, Mermaid, or remote images. The site must load while every OPEN service is down.
7. **Charter limits.** Nothing that conflicts with the [mission charter](https://github.com/openpickleball/.github/blob/main/CHARTER.md).

## Related repositories

Local checkouts may exist next to this one: `../OPEN-backend` (its `CONTEXT.md` holds the domain language and `docs/adr/` the decisions), `../OPEN-engine`, `../OPEN-frontend`, and `../OPEN-pickleball` (the `openpickleball/.github` repository with the charter, governance, contributing guide, security policy, and licensing). Use the backend's domain terms on the site.

## Contribution conventions

- Every commit needs a DCO sign-off (`git commit -s`). CI rejects pull requests with unsigned commits. That check runs only on pull requests, so commits pushed straight to `main` must be signed off by hand.
- One change per pull request, linked to an issue.
- Commit messages: imperative mood, subject under 72 characters, body explains why.
- License: the site's text is CC BY 4.0 (`LICENSE`). The build configuration, workflows, and any scripts are Apache-2.0 (`LICENSE-APACHE`). A new script carries an `SPDX-License-Identifier: Apache-2.0` line.

## Git exception

This section overrides a contributor's global no-commit rule for the `/work-issue` workflow only.

- The workflow may commit (`git commit -s`, with explicit paths) and push, but only on the `issue-<N>-*` branch it creates or resumes.
- After a rebase it may push that branch with `--force-with-lease`. It never force-pushes any other branch.
- It may open a pull request against `main`, edit its description, label it (creating the ready label if it does not exist), and reply to review comments on it.
- It never commits or pushes to `main`, never merges, and never enables auto-merge. A human reviews and merges every pull request.

## Writing style

Plain, short sentences. No emojis and no em dashes. Prefer "player", "match", and "organizer" over generic words like "user" or "entity".
