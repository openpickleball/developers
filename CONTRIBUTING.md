# Contributing to the developer site

This guide adds to the [organization contributing guide](https://github.com/openpickleball/.github/blob/main/CONTRIBUTING.md). Read both.

## Preview locally

You need [uv](https://docs.astral.sh/uv/getting-started/installation/). It installs Python 3.13 and the pinned [Zensical](https://zensical.org) packages for you.

```bash
uv sync
uv run zensical serve
```

The site is then at http://localhost:8000. Before you open a pull request, run the same checks CI runs, in the same order:

```bash
uv run pytest
uv run python scripts/check_docs.py
uv run zensical build --strict
```

The strict build fails on a link to a missing page or a missing anchor. The check script, `scripts/check_docs.py`, fails on a page missing from the navigation, a navigation entry that is not a file in `docs/`, an absolute link such as `/stack/`, a link to a directory such as `stack/`, or a relative link to a file that does not exist. CI runs it next to the build.

## Writing the site

- Pages live in `docs/`. Add a new page to `nav` in `mkdocs.yml`.
- Plain, short sentences. No emojis and no em dashes. Prefer "player", "match", and "organizer" over generic words like "user".
- Link to each repository's decisions (ADRs, `CONTEXT.md`, the rating spec) instead of copying them. A one-sentence summary is fine.
- Check every claim against the repository it describes, on `main`. Mark each step of how a match becomes a rating as implemented or planned.
- Keep the status notice: no OPEN rating is live, the engine is the reference implementation of the OPEN rating method, and its outputs are not OPEN ratings.
- Load nothing from another host: no web fonts, CDN scripts, Mermaid, or remote images. The site must load while every OPEN service is down.

## Hard rules

- No real player data, anywhere. Use made-up names and OPEN Codes, such as `P-7K3M-QX9H`.
- Never name another rating system. Say "standard external rating system".

## Sign off your commits

Every commit needs a [DCO](https://developercertificate.org/) sign-off: `git commit -s`. A check rejects pull requests with unsigned commits.

## Deploys

Every pull request runs the tests, the check script, and the strict build. A merge to `main` builds the site and deploys it to GitHub Pages at [dev.openpb.org](https://dev.openpb.org).
