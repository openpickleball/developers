# Tech stack

Each repository picks its own tools. This page lists them and gives the reason, with a link to the decision behind it.

## Backend

[openpickleball/backend](https://github.com/openpickleball/backend). The stack decisions are in [backend issue #1](https://github.com/openpickleball/backend/issues/1) and the [architecture decision records](https://github.com/openpickleball/backend/tree/main/docs/adr).

| Part | Choice | Why |
| --- | --- | --- |
| Language and framework | Python 3.13, Django 5.2 LTS | The engine is Python, so the backend can import it and run the same code for the API, replays, and backtests. Django's admin is the first back office for moderators. 5.2 LTS has security support until April 2028. [ADR 0001](https://github.com/openpickleball/backend/blob/main/docs/adr/0001-django.md) |
| API | django-ninja at `/api/v1/` | Typed operations and an OpenAPI document, with one error format and stable operation ids for generated clients. [ADR 0005](https://github.com/openpickleball/backend/blob/main/docs/adr/0005-api-versioning-and-error-format.md) |
| Database | Postgres, through psycopg 3 | Holds the ledger and every record. Constraints enforce match rules and duplicate uniqueness, the app refuses edits and deletes of ledger rows ([ADR 0013](https://github.com/openpickleball/backend/blob/main/docs/adr/0013-match-confirmation-and-changes.md)), and a database trigger keeps the audit log append-only ([ADR 0007](https://github.com/openpickleball/backend/blob/main/docs/adr/0007-append-only-audit-log.md)). |
| Cache and broker | Valkey | DigitalOcean's managed cache is Valkey, which speaks the Redis protocol, so Django's cache and Celery work unchanged. [Issue #1, decision Q11](https://github.com/openpickleball/backend/issues/1) |
| Background tasks | Celery with django-celery-beat | Four queues (`default`, `ratings`, `email`, `webhooks`), late acknowledgement, and periodic tasks from the database scheduler. [ADR 0006](https://github.com/openpickleball/backend/blob/main/docs/adr/0006-celery-queues-and-broker.md) |
| Accounts | django-allauth 65, headless | Sign-up, login, email verification, and password reset as an API for the web app, with email-only login. [ADR 0014](https://github.com/openpickleball/backend/blob/main/docs/adr/0014-headless-account-authentication.md) |
| Partner access | django-oauth-toolkit | Partners reach the API as OAuth2 clients, with an optional owning organizer, an approval, and hashed client secrets. [ADR 0010](https://github.com/openpickleball/backend/blob/main/docs/adr/0010-partner-application-model.md) |
| Email | django-anymail with Resend | Sent from an outbox on the `email` queue, so a slow provider never slows a request. [ADR 0016](https://github.com/openpickleball/backend/blob/main/docs/adr/0016-email-outbox.md) |
| Serving | gunicorn, WhiteNoise, django-cors-headers | gunicorn runs the app, WhiteNoise serves static files, and CORS covers the API and account paths only. |
| Tooling | uv, pytest, factory_boy, ruff, mypy (strict), pre-commit | One lockfile, tests against real Postgres, and strict types. |
| Hosting | DigitalOcean App Platform | Planned. |

## Engine

[openpickleball/engine](https://github.com/openpickleball/engine).

| Part | Choice | Why |
| --- | --- | --- |
| Language | Python 3.11 or later | The backend imports it in-process ([ADR 0001](https://github.com/openpickleball/backend/blob/main/docs/adr/0001-django.md)). |
| Dependencies | None at runtime | Plain Python, built with hatchling. |
| Tooling | pytest, ruff, mypy | Tests, lint, and types. |
| Releases | On PyPI as `openpickleball-engine`, version 1.0.0 | Each tagged release publishes to TestPyPI, then to PyPI after approval. Install with `pip install openpickleball-engine`. The backend will pin a release tag ([backend issue #1, decision Q4](https://github.com/openpickleball/backend/issues/1)). See [releasing](https://github.com/openpickleball/engine/blob/main/docs/releasing.md). |

## Frontend

[openpickleball/frontend](https://github.com/openpickleball/frontend). The app's stack is decided in [the frontend stack decision](https://github.com/openpickleball/frontend/blob/main/plans/frontend-stack/decision.md).

| Part | Choice | Why |
| --- | --- | --- |
| App framework | SvelteKit (Svelte 5), TypeScript | Most of OPEN is pages people open from a link and forms they fill in on a phone. A web-first framework does that best, and an installable PWA covers mobile for now. |
| Styling | Tailwind CSS 4 | Shared with the static site. |
| API client | openapi-typescript and openapi-fetch | Types are generated from the backend's OpenAPI documents. |
| Tests | Vitest, Playwright | Unit and component tests, and end-to-end tests in a browser. |
| Package manager | pnpm, Node 26 | One lockfile per project (`site/` and `app/`). |
| Hosting | GitHub Pages for `site/` | The web app's hosting is not decided yet. |

## Rating spec

[openpickleball/rating-spec](https://github.com/openpickleball/rating-spec). Markdown, versioned with Semantic Versioning. A major version is a change that can move existing ratings. Changes go through the [RFC process](https://github.com/openpickleball/rating-spec/blob/main/rfcs/README.md).

## This site

[openpickleball/developers](https://github.com/openpickleball/developers). Zensical with its classic theme, pinned with uv, built and deployed to GitHub Pages by a workflow. It loads no fonts, scripts, or images from another host.
