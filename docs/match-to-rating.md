# How a match becomes a rating

A match passes through several steps before it can move a rating. Each step below is marked:

- **Implemented**: the code is on `main` in the named repository.
- **Planned**: tracked in an issue, not built yet.

The short version: the backend takes, checks, and confirms matches today, and keeps them in an append-only ledger. The engine can replay a ledger into ratings today. Connecting the two, and serving ratings, is planned. No OPEN rating is published.

```text
 submit -> permission -> validate -> duplicates -> confirm or dispute
                                                         |
                                                         v
                                            append-only ledger (counted matches)
                                                         |
                          +------------------------------+-------------------------+
                          v                                                        v
           live update (provisional, planned)                   replay with provenance (planned in backend)
                          |                                                        |
                          +------------------------> ratings <---------------------+
                                           (demonstration only, served by an API that is planned)
```

## 1. Submission

**Implemented** in the backend, for a player's own match. **Planned** for organizers, clubs, and partners through the API.

Every path that adds a match calls one service, `record_match()`, so every path gets the same checks. Today the API has one submission operation, `POST /api/v1/matches/`, for a player who played in the match. Players are named by OPEN Code. An example body, with made-up codes:

```json
{
  "format": "doubles",
  "played_on": "2026-11-14",
  "team_a": ["P-7K3M-QX9H", "P-4TNW-2R8N"],
  "team_b": ["P-9HDQ-6MA2", "P-2ZC8-VJ5M"],
  "games": [{"team_a": 11, "team_b": 7}, {"team_a": 9, "team_b": 11}, {"team_a": 11, "team_b": 8}]
}
```

Partner endpoints ([backend#32](https://github.com/openpickleball/backend/issues/32)) and CSV upload for organizers ([backend#71](https://github.com/openpickleball/backend/issues/71)) are planned.

## 2. Permission check

**Implemented** in the backend.

The submitter is checked before anything else, so a refused submitter learns nothing about other matches. A match with an Event needs authority for that Event: a member of its verified Organizer, or an approved Partner Application that Organizer owns. A match with a Club needs a Club Role there, or an approved application the Club granted. A match with neither is a self-submission, and only a player in the match may send it. A refusal is a 403. See [ADR 0012](https://github.com/openpickleball/backend/blob/main/docs/adr/0012-match-submission-permissions.md).

## 3. Validation

**Implemented** in the backend.

One function, `validate_match()`, holds the score rules: the winner of each game reaches the target and wins by 2 (past the target, by exactly 2), team size fits the format, no player appears twice, best of 1, 3, or 5, games to 11, 15, or 21 with side-out or rally scoring, 1 to 5 games that decide the match, and no date in the future. It reports every problem at once, as a 422 with one item per problem. A validation message never repeats the submitted value.

## 4. Duplicate detection

**Implemented** in the backend.

Each match gets a fingerprint of its teams, date, and scores. An exact duplicate of a match that is not voided is refused with a 409, and so is a partner's repeated external id. A near duplicate (same teams and date, other scores) is saved but flagged, and the flag holds both matches from counting until a moderator reviews it. See [ADR 0011](https://github.com/openpickleball/backend/blob/main/docs/adr/0011-duplicate-match-detection.md). The moderator review screens are planned ([backend#40](https://github.com/openpickleball/backend/issues/40)).

## 5. Confirmation and dispute

**Implemented** in the backend, including the player operations `POST /api/v1/matches/{code}/confirm` and `/dispute`. Moderator screens are **planned**.

A match has four statuses: pending, confirmed, disputed, and voided. A match from someone with Event or Club authority is confirmed when it is created. A self-submission stays pending until at least one player on each team confirms it (the submitter's own submission does not count as their team's confirmation), or until someone with Event or Club authority submits the same match (same teams, date, and scores). A player may dispute a match once. A disputed match stops counting until a moderator (an active Account with the `matches.moderate_match` permission) resolves it as confirmed or voided. An optional daily task voids pending matches older than a set number of days. See [ADR 0013](https://github.com/openpickleball/backend/blob/main/docs/adr/0013-match-confirmation-and-changes.md) and [ADR 0015](https://github.com/openpickleball/backend/blob/main/docs/adr/0015-first-party-match-endpoints.md).

## 6. The append-only ledger and corrections

**Implemented** in the backend.

The ledger is the ordered record of every counted match, and it is the source of truth for ratings. A match is never deleted, and only its status ever changes. A wrong match is voided, and a correction is a new match that points to it, so the ledger keeps both. A match counts when it is confirmed and no open duplicate flag holds it. Every status change writes an Audit Event to an append-only audit log ([ADR 0007](https://github.com/openpickleball/backend/blob/main/docs/adr/0007-append-only-audit-log.md)). Some changes send a signal inside their transaction, for the rating and webhook work to use. Confirming a match sends `match_confirmed`, even when a duplicate flag still holds it, so a receiver checks whether the match counts. Voiding, correcting, or disputing a counting match, or holding it with a new flag, sends `match_changed`, and so does a held match counting again because the match holding it was voided. A correction of a counting match sends `match_changed` instead of `match_confirmed`. Nothing listens to those signals yet.

## 7. Engine adapter

**Planned** in the backend.

The backend will pin the engine to a release tag ([backend#43](https://github.com/openpickleball/backend/issues/43)) and map counted matches to the engine's input ([backend#44](https://github.com/openpickleball/backend/issues/44)). The match type comes from the Event's kind, or is self-reported when there is no Event. The backend never computes ratings itself: the math lives in the engine.

## 8. Live updates

**Implemented** in the engine. **Planned** in the backend ([backend#46](https://github.com/openpickleball/backend/issues/46)).

When a match arrives between replays, the engine can update ratings at once. These live updates are provisional. Each rating carries a count of live updates since the last replay, so a reader can tell a provisional rating from an authoritative one.

## 9. Replay with provenance

**Implemented** in the engine. **Planned** in the backend ([ratings pipeline epic, backend#109](https://github.com/openpickleball/backend/issues/109)).

Authoritative ratings come from a deterministic replay: the engine rebuilds every rating from the seeds and the full ledger as of a date. The same ledger, seeds, config, and date always give the same result. Each replay returns its provenance: the as-of date, the config version, the config fingerprint, and match counts. The backend must store that provenance with every replay, so any published rating can be reproduced. Each published version of the [rating spec](https://github.com/openpickleball/rating-spec) will name the config version and fingerprint that implement it.

## 10. Serving ratings

**Planned** in the backend.

A ratings API will let any app read ratings and rating history for free ([backend#53](https://github.com/openpickleball/backend/issues/53)). Stats are planned separately ([backend#55](https://github.com/openpickleball/backend/issues/55), [#56](https://github.com/openpickleball/backend/issues/56), [#57](https://github.com/openpickleball/backend/issues/57)). While the engine is a demonstration, its output is labeled as demonstration ratings. Ratings go live only after the steps in the [roadmap](https://github.com/openpickleball/.github/blob/main/ROADMAP.md), including published validation results and a seated governing board.

## Starting ratings

**Implemented** in the engine. **Planned** in the backend.

A player starts from a seed. A seed can come from a verified rating in a standard external rating system, with its source, date, and evidence. An imported rating is only a starting point: it never overwrites a rating earned from OPEN matches, and its reliability is shown apart from OPEN-earned reliability.
