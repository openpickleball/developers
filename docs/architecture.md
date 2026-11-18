# Architecture

OPEN is split into a few repositories, each with one job. The backend stores the match ledger and will serve ratings. The engine holds the rating math. The rating spec defines that math in words. The frontend is the public app.

## How the pieces fit together

```text
   Players and organizers           Partners (apps, league platforms,
   in a browser                     clubs, tournaments)
          |                                   |
          v                                   v
 +------------------+              +----------------------+
 | Frontend web app |              | Partner integrations |
 | (frontend repo,  |              | OAuth2 tokens        |
 |  planned)        |              | (API planned)        |
 +------------------+              +----------------------+
          |  /api/v1/ and /_allauth/          |  /oauth/ and /api/v1/
          v                                   v
 +-----------------------------------------------------------+
 | Backend (Django)                                          |
 |  API at /api/v1/   accounts at /_allauth/   admin         |
 |  match ledger, confirmation workflow, audit log           |
 |  Celery workers and beat: default, ratings, email,        |
 |  webhooks queues                                          |
 |                                                           |
 |  +---------------------------+                            |
 |  | Engine (Python package),  |  imported in-process,      |
 |  | replay and live updates   |  planned                   |
 |  +---------------------------+                            |
 +-----------------------------------------------------------+
       |                  |                   |
       v                  v                   v
   Postgres         Valkey (cache        Email provider
   (ledger and      and Celery           (Resend)
   all records)     broker)

 Rating spec (rating-spec repository): the official definition
 of the math. The engine implements a spec version, identified by
 its config version and config fingerprint.

 openpb.org: a static teaser from the frontend repository on
 GitHub Pages. It is live and calls no backend.

 Status page (status.openpb.org, planned): checks the backend
 from outside, so it stays up when the backend is down.
```

## Frontend

Repository: [openpickleball/frontend](https://github.com/openpickleball/frontend).

- `site/` is a static teaser served at [openpb.org](https://openpb.org) by GitHub Pages. It is live.
- `app/` is the full web app, a SvelteKit single-page app built as an installable PWA. It is in development and not deployed. It talks to the backend's API at `/api/v1/` and to the account endpoints at `/_allauth/`, and generates its API types from their OpenAPI documents.

## Backend

Repository: [openpickleball/backend](https://github.com/openpickleball/backend).

A Django project that holds every record and will serve ratings.

- **One API** at `/api/v1/`, with an OpenAPI document and one error format ([ADR 0005](https://github.com/openpickleball/backend/blob/main/docs/adr/0005-api-versioning-and-error-format.md)). Records are named by OPEN Codes, never row ids ([ADR 0008](https://github.com/openpickleball/backend/blob/main/docs/adr/0008-public-identifiers.md)).
- **Accounts** use headless sign-up, login, email verification, and password reset at `/_allauth/` ([ADR 0014](https://github.com/openpickleball/backend/blob/main/docs/adr/0014-headless-account-authentication.md)). Players must be 13 or older ([ADR 0017](https://github.com/openpickleball/backend/blob/main/docs/adr/0017-signup-age-screen.md)).
- **Partners** get OAuth2 clients. The token and revoke endpoints exist at `/oauth/`. No API operation accepts a partner token yet ([ADR 0010](https://github.com/openpickleball/backend/blob/main/docs/adr/0010-partner-application-model.md)).
- **The match ledger** is append-only. See [How a match becomes a rating](match-to-rating.md).
- **The audit log** records every sensitive action, and the database refuses to change or delete its rows ([ADR 0007](https://github.com/openpickleball/backend/blob/main/docs/adr/0007-append-only-audit-log.md)).
- **Background work** runs in Celery on four queues: `default`, `ratings`, `email`, and `webhooks` ([ADR 0006](https://github.com/openpickleball/backend/blob/main/docs/adr/0006-celery-queues-and-broker.md)). Email goes through an outbox and the `email` queue ([ADR 0016](https://github.com/openpickleball/backend/blob/main/docs/adr/0016-email-outbox.md)).
- **Hosting** on DigitalOcean App Platform is planned.

What the API serves today: health checks, the signed-in account, a player's own match submission, confirm and dispute, and a player's match history. Rating endpoints, partner endpoints, and organizer upload tools are planned.

## Engine

Repository: [openpickleball/engine](https://github.com/openpickleball/engine).

The reference rating engine, a Python package (`openpickleball-engine`, imported as `open_engine`) with no runtime dependencies. It records matches live and rebuilds ratings with a deterministic replay of the ledger. The backend will import it in-process, so the API, scheduled replays, and backtests all run the same code ([ADR 0001](https://github.com/openpickleball/backend/blob/main/docs/adr/0001-django.md)). The backend does not depend on it yet. When it does, the engine is pinned to a release tag, and its output stays labeled as demonstration ratings.

## Rating spec

Repository: [openpickleball/rating-spec](https://github.com/openpickleball/rating-spec).

The official definition of how an OPEN rating is calculated: the inputs, the math, the parameters, and how reliability is reported. Changes go through a public proposal (an RFC), and only the governing board changes the official version. Each published version records the config version and config fingerprint that implement it, so a published rating can be reproduced from the ledger. No version is published yet.

## Status page

Planned at `status.openpb.org` ([backend#139](https://github.com/openpickleball/backend/issues/139)). It will check the backend from outside and report whether ratings are fresh ([backend#140](https://github.com/openpickleball/backend/issues/140)).

## This site

[openpickleball/developers](https://github.com/openpickleball/developers) is a static MkDocs site on GitHub Pages. It calls no OPEN service and loads nothing from another host, so it stays up when the backend is down.
