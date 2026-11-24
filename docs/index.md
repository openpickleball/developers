# OPEN for developers

OPEN, the Open Pickleball Evaluation Network, is a free, open-source, community-governed pickleball rating network. This site explains how it works for developers, researchers, and anyone who wants to contribute: how the pieces fit together, what they are built with, and how a match becomes a rating.

## Current status

!!! warning "No OPEN rating is live"

    OPEN publishes no ratings yet. The [rating engine](https://github.com/openpickleball/engine) is the reference implementation of the OPEN rating method. Its outputs are not OPEN ratings, and it must not be used to rate real players. It was evaluated on one club's closed pool, and a forthcoming report describes that evaluation. Ratings from pools that share no players are not comparable, and the engine's parameters are retuned on a published schedule. No official version of the [rating spec](https://github.com/openpickleball/rating-spec) exists yet.

What exists today:

- The **backend** stores accounts, players, clubs, organizers, events, and matches. It validates match submissions, detects duplicates, and runs the confirmation and dispute workflow. It does not call the engine yet, and it serves no ratings.
- The **engine** computes and replays ratings as a Python package. Version 1.0.0 is on PyPI: install it with `pip install openpickleball-engine`, and load the published parameter set `v1` with `Config.published("v1")`. `v1` is not shown to predict better than the `Config()` defaults, which remain placeholders. Its outputs are still not OPEN ratings.
- The **frontend** serves a static teaser at [openpb.org](https://openpb.org). The full web app is in development and not deployed.

Testing the engine on real match results in shadow mode, so that no one relies on its ratings yet, is a current priority on the roadmap. The [roadmap](https://github.com/openpickleball/.github/blob/main/ROADMAP.md) lists what must happen before ratings go live, including a seated governing board and published validation results.

## Players never pay

The [mission charter](https://github.com/openpickleball/.github/blob/main/CHARTER.md) rules out subscriptions, paid tiers, advertisements, and premium features, so no part of OPEN is for sale, including a rating reset or a stat. Under the [funding rules](https://github.com/openpickleball/.github/blob/main/GOVERNANCE.md#funds), every dollar in and out is published, and donors, grant makers, and sponsors get no say over ratings.

## Who this site is for

- **Developers** who want to contribute to the backend, engine, or frontend.
- **Partners** (apps, league platforms, clubs, and tournaments) who want to know how OPEN will take results and serve ratings. Integration docs for partners are planned separately.
- **Researchers and rating enthusiasts** who want to review the methods.

## Pages

- [Architecture](architecture.md): the repositories and services, and how they fit together.
- [Tech stack](stack.md): what each repository is built with, and why.
- [How a match becomes a rating](match-to-rating.md): each step from submission to rating, marked as implemented or planned.
- [Contributing](contributing.md): how to contribute to each repository.
- [Glossary](glossary.md): the domain terms, one line each.

This site links to each repository's decisions instead of copying them. Where this site and a repository disagree, the repository is right. Please [open an issue](https://github.com/openpickleball/developers/issues/new) so we can fix the site.
