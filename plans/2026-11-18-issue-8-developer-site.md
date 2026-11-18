# Plan: Developer site at dev.openpb.org (openpickleball/.github#8)

Risk tier: Medium. Not a forced-High area (no auth, money, migrations, or messaging); raised for behavior a unit test cannot exercise (a deployed static site, a Pages workflow) and for more than a few new files. The user asked for no approval pause, so this plan is committed without one.

Domain skills: none apply. django, django-ninja-api, django-allauth, django-celery: not applicable because this repository has no Python application code, only Markdown and MkDocs configuration. frontend-design: not applicable because the site uses the stock Material for MkDocs theme. humanizer: optional for prose; the finders check tone.

Decisions already made by the user: create `openpickleball/developers` (done, bootstrap commit `0fc1e73` on `main`: licenses, README, DCO workflow), MkDocs on GitHub Pages (Pages enabled with Actions builds, custom domain `dev.openpb.org` set), and do both the site and the `LICENSING.md` row in `.github`.

Plans live in `plans/`, not `docs/plans/`, because `docs/` is the MkDocs source directory and would publish them.

## Acceptance criteria

1. `uv run mkdocs build --strict` succeeds from a clean checkout, using versions pinned in `pyproject.toml` and `uv.lock`.
2. The site has these pages, each reachable from the navigation:
   - Home (`docs/index.md`): what OPEN is, who the site is for, current status, and a map of the other pages.
   - Architecture (`docs/architecture.md`): the frontend, backend, engine, rating spec, and the planned status page, and how they fit together, with a diagram that loads no third-party script (an inline SVG or a text diagram in a code block).
   - Tech stack (`docs/stack.md`): each repository's stack and why, with the reason drawn from its ADRs or decisions.
   - How a match becomes a rating (`docs/match-to-rating.md`): submission, validation, duplicate detection, confirmation and dispute, the append-only ledger and corrections, replay with provenance, and provisional live updates. Each step says whether it is implemented today or planned.
   - Contributing (`docs/contributing.md`): how to contribute to each repository, with links to each repository's guide and the org guide.
   - Glossary (`docs/glossary.md`): the domain terms, one line each, linking to `CONTEXT.md` in the backend as the source of truth.
3. Decisions are linked, not copied: the backend's ADR directory, the rating spec repository, and each repository's README or CONTRIBUTING are linked by URL on `main`. No ADR text or spec text is pasted beyond a one-sentence summary.
4. Every page shows that OPEN publishes no ratings yet and that engine output is labeled as demonstration ratings (a site-wide announcement bar through a theme override, plus the status section on Home).
5. The built site makes no request to any OPEN backend or API, and no request to a third-party host at load time (Material's Google Fonts off with `theme.font: false`, and no Mermaid, which Material loads from a CDN). So the site loads while the backend is down.
6. Hard rules: no real player data (examples use made-up OPEN Codes and names), and no names of other rating systems ("standard external rating system" only).
7. `.github/workflows/pages.yml` builds the site with `--strict` on every pull request (job named `build`) and deploys to GitHub Pages on push to `main` (job `deploy`, environment `github-pages`). Actions are pinned to full commit SHAs with a version comment. Permissions are least privilege per job.
8. The repository gets a `CONTRIBUTING.md` (adds to the org guide: how to preview locally, the hard rules, DCO) and a `.github/CODEOWNERS` matching the backend's pattern for the maintainers team, if that team exists in the org, else the org owner handle used in `.github`'s CODEOWNERS.
9. In `openpickleball/.github`, `LICENSING.md` names the `developers` repository: its text under CC BY 4.0 in the documentation row, and its code (configuration, workflows, scripts) under Apache-2.0. No other `.github` file changes unless this change makes it wrong.
10. Every factual claim on the site matches the source repositories on `main`. Where the fact sheet and a repository's `CLAUDE.md` disagree, the repository wins (for example, a moderator is an active Account with the `matches.moderate_match` permission, per the backend `CLAUDE.md`).

## Files that change

In `openpickleball/developers` (worktree `/home/bradstricherz/PycharmProjects/OPEN-developers`, branch `issue-8-developer-site-at-dev-openpb-org`):

- `pyproject.toml`, `uv.lock`: a non-package uv project with `mkdocs-material` pinned (exact versions), Python 3.13.
- `.python-version`: 3.13.
- `mkdocs.yml`: site name, `site_url: https://dev.openpb.org/`, a repository link through `extra.social` (not `repo_url`: with `repo_url`, Material's script fetches star and fork counts from `api.github.com` on every page load, which breaks criterion 5), Material theme with `font: false`, light and dark palette, navigation, `pymdownx.superfences`, `admonition`, strict validation of links (`validation:` block set to warn on omitted, absolute, and unrecognized links), `custom_dir: overrides`, copyright line naming CC BY 4.0.
- `overrides/main.html`: the announcement block with the demonstration notice.
- `docs/index.md`, `docs/architecture.md`, `docs/stack.md`, `docs/match-to-rating.md`, `docs/contributing.md`, `docs/glossary.md`.
- `.github/workflows/pages.yml`.
- `.gitignore`: `site/`, `.venv/`, `.cache/`.
- `CONTRIBUTING.md`, `.github/CODEOWNERS`.
- `README.md`: add a "Preview locally" section (`uv run mkdocs serve`).
- `plans/2026-11-18-issue-8-developer-site.md` (this file).

In `openpickleball/.github` (checkout `/home/bradstricherz/PycharmProjects/OPEN-pickleball`, a new branch `issue-8-license-developers-site` from `origin/main`):

- `LICENSING.md` only.

## Order of work

1. Project setup: `uv init --bare` style `pyproject.toml`, `uv add mkdocs-material` (dev group not needed), `.python-version`, `.gitignore`, `mkdocs.yml` with a stub Home. Confirm `uv run mkdocs build --strict` passes. Commit.
2. Confirm the stub build loads nothing from another host (gate step 3). Material loads Mermaid from a CDN when a page has a diagram, so the site uses no Mermaid. Draw the architecture as an inline SVG with `currentColor` strokes so it works in light and dark, or as a text diagram in a code block.
3. Write the pages in the order Home, Architecture, Tech stack, How a match becomes a rating, Glossary, Contributing. Use the fact sheet at `<scratch>/facts.md` as a starting point and verify each claim against the local checkouts (`../OPEN-backend`, `../OPEN-engine`, `../OPEN-frontend` on its `main` via `git show origin/main:<path>` because the checkout is on another branch, `../OPEN-pickleball`) and `gh api repos/openpickleball/rating-spec/contents/...`. Commit per page or a few pages at a time.
4. Announcement override, CONTRIBUTING, CODEOWNERS, README section. Commit.
5. Workflow `pages.yml`. Pin `actions/checkout`, `astral-sh/setup-uv`, `actions/configure-pages`, `actions/upload-pages-artifact`, `actions/deploy-pages` to SHAs of their latest release tags (look up with `gh api repos/<owner>/<action>/git/ref/tags/<tag>`; dereference annotated tags). Build job: `uv sync --locked`, `uv run mkdocs build --strict`, upload the artifact only on push to `main`. Deploy job: `needs: build`, only on push to `main`, `pages: write`, `id-token: write`. Add `concurrency: pages`. Commit.
6. `.github` repo: branch, edit `LICENSING.md`, commit with sign-off. Do not push.

## Gate

Run in `/home/bradstricherz/PycharmProjects/OPEN-developers`, in order:

1. `uv sync --locked`
2. `uv run mkdocs build --strict`
3. `grep -rhoE '(src|href)="https?://[^"]+"' site | sort -u` and confirm each URL is a link a reader clicks (`<a href>`), never a `<script src>`, `<link href>`, or `<img src>` to another host.
4. `git diff --check origin/main...HEAD`

## Risks

- Factual drift: the site states things the code does not do (the most likely defect). Mitigation: every implemented-or-planned label is checked against the repository, and the pages link to the source.
- Overclaiming status: presenting replay or ratings as live. Mitigation: criterion 4 and the per-step status labels.
- Third-party requests at load (fonts, Mermaid). Mitigation: criterion 5 and gate step 3.
- Pages deploy permissions or an unpinned action. Mitigation: criterion 7; the first deploy runs only after merge.
- `dev.openpb.org` will not resolve until a CNAME to `openpickleball.github.io` exists at the DNS provider. That is the user's step and is reported, not done here.
- Choosing not to do: copying ADRs, partner docs, a status page, search tuning, versioned docs.

## Proof

- Criterion 1, 2, 3: gate step 2 (strict build fails on a broken internal link or a page missing from nav).
- Criterion 5: gate step 3, and the live drive.
- Criteria 4, 6, 10: finder review and the verifier's read of each page against the sources.
- Criterion 7: workflow file review; the PR's `build` check.
- Live drive (Medium, drive the changed path): `uv run mkdocs serve -a 127.0.0.1:8765` in the background, `curl -s` each page's URL and check 200 and the announcement text, then stop the server by PID. Also open `site/index.html` from the built output with no server and no network to confirm it renders (Material's `use_directory_urls` means the served build is the real test; the offline check is that no asset URL leaves the site).

Measured on `origin/main` before the plan: nothing to measure (the repository holds only licenses, a README, and the DCO workflow).
