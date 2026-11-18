# Contributing to the developer site

This guide adds to the [organization contributing guide](https://github.com/openpickleball/.github/blob/main/CONTRIBUTING.md). Read both.

## Preview locally

You need [uv](https://docs.astral.sh/uv/getting-started/installation/). It installs Python 3.13 and the pinned MkDocs packages for you.

```bash
uv sync
uv run mkdocs serve
```

The site is then at http://127.0.0.1:8000. Before you open a pull request, run the same strict build CI runs:

```bash
uv run mkdocs build --strict
```

A strict build fails on a broken internal link or a page missing from the navigation.

## Writing the site

- Pages live in `docs/`. Add a new page to `nav` in `mkdocs.yml`.
- Plain, short sentences. No emojis and no em dashes. Prefer "player", "match", and "organizer" over generic words like "user".
- Link to each repository's decisions (ADRs, `CONTEXT.md`, the rating spec) instead of copying them. A one-sentence summary is fine.
- Check every claim against the repository it describes, on `main`. Mark each step of how a match becomes a rating as implemented or planned.
- Keep the demonstration notice: OPEN publishes no ratings yet, and engine output is labeled as demonstration ratings.
- Load nothing from another host: no web fonts, CDN scripts, Mermaid, or remote images. The site must load while every OPEN service is down.

## Hard rules

- No real player data, anywhere. Use made-up names and OPEN Codes, such as `P-7K3M-QX9H`.
- Never name another rating system. Say "standard external rating system".

## Sign off your commits

Every commit needs a [DCO](https://developercertificate.org/) sign-off: `git commit -s`. A check rejects pull requests with unsigned commits.

## Deploys

Every pull request runs the strict build. A merge to `main` builds the site and deploys it to GitHub Pages at [dev.openpb.org](https://dev.openpb.org).
