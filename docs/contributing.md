# Contributing

Everyone is welcome. You don't need to write code: players, organizers, platform builders, and statisticians can all help. Start with the [organization contributing guide](https://github.com/openpickleball/.github/blob/main/CONTRIBUTING.md), which applies to every repository. A repository's own guide adds to it.

## Rules for every repository

- Open an issue before starting anything large, in the repository it is about.
- Keep each pull request to one change, linked to its issue.
- Sign off every commit under the [Developer Certificate of Origin](https://developercertificate.org/): `git commit -s`. A check rejects pull requests with unsigned commits.
- Never put real player data in code, tests, issues, pull requests, or screenshots. Use made-up names and codes.
- Report security problems privately, as the [security policy](https://github.com/openpickleball/.github/blob/main/SECURITY.md) describes.
- Everyone agrees to the [mission charter](https://github.com/openpickleball/.github/blob/main/CHARTER.md) and the [Code of Conduct](https://github.com/openpickleball/.github/blob/main/CODE_OF_CONDUCT.md).

## Backend

[openpickleball/backend](https://github.com/openpickleball/backend): read its [contributing guide](https://github.com/openpickleball/backend/blob/main/CONTRIBUTING.md) and [README](https://github.com/openpickleball/backend/blob/main/README.md). You need uv and Docker. The quick start runs Postgres and Valkey with `docker compose up -d --wait`, then `uv run pytest`. Check the [architecture decision records](https://github.com/openpickleball/backend/tree/main/docs/adr) and [`CONTEXT.md`](https://github.com/openpickleball/backend/blob/main/CONTEXT.md) before changing a decision or naming a model.

## Engine

[openpickleball/engine](https://github.com/openpickleball/engine): read its [README](https://github.com/openpickleball/engine/blob/main/README.md). It has no guide of its own, so the organization guide applies. Install it from a checkout with `pip install -e ".[dev]"`, then run `pytest`, `ruff check .`, and `mypy src`.

## Frontend

[openpickleball/frontend](https://github.com/openpickleball/frontend): read its [contributing guide](https://github.com/openpickleball/frontend/blob/main/CONTRIBUTING.md) and [README](https://github.com/openpickleball/frontend/blob/main/README.md). It uses Node 26 and pnpm. `site/` and `app/` are separate projects: run `pnpm install` and `pnpm dev` in the one you change.

## Rating spec

[openpickleball/rating-spec](https://github.com/openpickleball/rating-spec): anyone can propose or challenge a change by opening an issue, with evidence. A change that gets support becomes an RFC under the [RFC process](https://github.com/openpickleball/rating-spec/blob/main/rfcs/README.md). The governing board makes the final decision.

## This site

[openpickleball/developers](https://github.com/openpickleball/developers): read its [contributing guide](https://github.com/openpickleball/developers/blob/main/CONTRIBUTING.md). Preview it with `uv run mkdocs serve`.

## Organization files

[openpickleball/.github](https://github.com/openpickleball/.github) holds the charter, governance, roadmap, licensing policy, and the organization guide.
