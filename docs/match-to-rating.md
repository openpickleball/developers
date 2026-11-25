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
                               (not OPEN ratings, served by an API that is planned)
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

## 8. How the engine moves a rating

**Implemented** in the engine.

The engine is an open-source Python package, `openpickleball-engine`, under AGPL-3.0-or-later. Its [rating model](https://github.com/openpickleball/engine/blob/main/docs/model.md) states every equation it uses and the function that computes each one. In short:

- **Expected result.** A team's rating is the mean of its players' ratings. The gap between the two teams gives each team an expected share of the points.
- **Performance.** By default, a team's performance is its share of all points across the match's games. The rating moves by the difference between that share and the expected share. So a team can win and still lose rating, when it wins by less than expected, and a team that loses by about as much as expected barely moves. See [match performance](https://github.com/openpickleball/engine/blob/main/docs/behavior.md#match-performance).
- **Uncertainty.** Each rating carries a rating deviation (RD). Each player moves by their own K, which grows with their RD, so a new or returning player moves faster than a settled one. RD shrinks with each counted match and grows with inactivity. Inactivity never moves the rating itself.
- **Weight.** The match type sets how much a match counts. Under the current defaults: tournament 1.00, league 0.90, recreational verified 0.75, and self-reported 0.40. Longer games and more games add a little weight, up to a cap. These defaults are declared choices or uncalibrated placeholders, as the [parameter table](https://github.com/openpickleball/engine/blob/main/docs/model.md#parameters) marks each one.

The engine also ships a published parameter set, `v1`, which a caller loads on purpose with `Config.published("v1")`. It is the first set fitted on match data. It declares a scale of 1.0 in place of the default 2.9, fits the side-out win calibration, and scales K by the fitted side-out scale (1.0 / 1.112). On held-out matches it showed no measurable gain over the defaults, so `Config()` is unchanged. The evaluation's simulations also found that `v1` moves ratings faster, so losing on purpose and colluding accounts move ratings further under it. See [PARAMETERS.md](https://github.com/openpickleball/engine/blob/main/PARAMETERS.md).

Every result reports the expected share, the actual share, the difference, the weight, and each player's change, so any rating change can be explained from the match that caused it. A replay of the same ledger, seeds, config, and date always gives the same ratings, so any change can also be reproduced (see [Replay with provenance](#10-replay-with-provenance)). The engine can also predict a match before it is played, as an expected point share and a win probability. No app shows those predictions to players yet.

## 9. Live updates

**Implemented** in the engine. **Planned** in the backend ([backend#46](https://github.com/openpickleball/backend/issues/46)).

When a match arrives between replays, the engine can update ratings at once. These live updates are provisional. Each rating carries a count of live updates since the last replay, so a reader can tell a provisional rating from an authoritative one.

## 10. Replay with provenance

**Implemented** in the engine. **Planned** in the backend ([ratings pipeline epic, backend#109](https://github.com/openpickleball/backend/issues/109)).

Authoritative ratings come from a deterministic replay: the engine rebuilds every rating from the seeds and the full ledger as of a date. The same ledger, seeds, config, and date always give the same result. Each replay returns its provenance: the as-of date, the config version, the config fingerprint, and match counts. The backend must store that provenance with every replay, so any published rating can be reproduced. Each published version of the [rating spec](https://github.com/openpickleball/rating-spec) will name the config version and fingerprint that implement it.

## 11. Serving ratings

**Planned** in the backend.

A ratings API will let any app read ratings and rating history for free ([backend#53](https://github.com/openpickleball/backend/issues/53)). Stats are planned separately ([backend#55](https://github.com/openpickleball/backend/issues/55), [#56](https://github.com/openpickleball/backend/issues/56), [#57](https://github.com/openpickleball/backend/issues/57)). The engine is the reference implementation of the OPEN rating method, and its outputs are not OPEN ratings. No OPEN rating is live. Ratings go live only after the steps in the [roadmap](https://github.com/openpickleball/.github/blob/main/ROADMAP.md), including published validation results and a seated governing board.

## Starting ratings

**Implemented** in the engine. **Planned** in the backend.

A player starts from a seed. A seed can come from a verified rating in a standard external rating system, with its source, date, and evidence. An imported rating is only a starting point: it never overwrites a rating earned from OPEN matches, and its reliability is shown apart from OPEN-earned reliability.

## Reliability and established ratings

**Implemented** in the engine. **Planned** in the backend, which will serve both with each rating ([backend#53](https://github.com/openpickleball/backend/issues/53)).

Reliability is a score from 0 to 100, earned only from OPEN matches. It combines the player's RD with the variety of their partners and opponents over the last year. An imported reliability never counts toward it.

A rating is **established** when its reliability is at least 60 and the player has at least 3 counted verified matches: tournament, league, or recreational verified, which all come from Events an Organizer runs. Self-reported matches can raise reliability, but they never count toward that minimum. The engine reports whether a rating is established with every player summary, so a rating that is not established can be labeled as such. Both thresholds are labels: they change no rating. See [Established](https://github.com/openpickleball/engine/blob/main/docs/behavior.md#established).

**Planned**: cap the reliability number itself below 60 until a player has the minimum verified matches, so a player with only self-reported matches never shows 60 or more ([engine#164](https://github.com/openpickleball/engine/issues/164)).

## Evaluation

**Implemented** in the engine: the tools. An initial evaluation is published. **Planned**: a pre-registered test on later play, and testing the engine on real match results in shadow mode.

The engine predicts each match from ratings that have not seen it yet, then scores those predictions for error and calibration. It also fits the expectation scale and the win probability calibration, and says when the data do not pin a value down. See [evaluation and calibration](https://github.com/openpickleball/engine/blob/main/docs/model.md#evaluation-and-calibration). The [evaluation repository](https://github.com/openpickleball/evaluation) holds the methodology and results of an initial evaluation on one club's play. It was not pre-registered, so no result in it is confirmatory. A test on matches played after the evaluation, registered in advance, is still pending. The evaluation compares the engine with standard external rating systems. Testing the engine on real results in shadow mode, and publishing validation results, are steps on the [roadmap](https://github.com/openpickleball/.github/blob/main/ROADMAP.md) before any rating goes live.

## Closed groups

**Implemented** in the engine as a label. Its reliability cap is **off by default** ([engine#86](https://github.com/openpickleball/engine/issues/86)).

Ratings are relative. A group that plays only itself has no matches that tie its scale to anyone else's, so its ratings can drift away from the wider network. RD and variety cannot see this: a closed group can reach low RD, full variety, and established ratings on its own. Matches between players from different groups are what place those groups on one scale.

So the engine reports network connectivity with every player summary: whether the player's group of regular partners and opponents connects to the wider network, through enough outside players on enough dates. When `connectivity_reliability_cap` is set, a player who is not connected has reliability held under the cap, so their rating is not established. The cap is off by default because group sizes can game the rule and it could cap players in a real but smaller community. [engine#86](https://github.com/openpickleball/engine/issues/86) tracks making it robust before it is turned on. See [Network connectivity](https://github.com/openpickleball/engine/blob/main/docs/behavior.md#network-connectivity).

## Guarding against gamed ratings

Each guard below is marked like the steps above. None of them costs a player anything or needs a paid verification. The guards are not complete: see [Known limitations](#known-limitations) below.

**Self-reported matches.** **Implemented** in the engine and the backend. A self-reported match counts only when a player on each team confirms it (see [Confirmation and dispute](#5-confirmation-and-dispute)). It weighs 0.40 against a tournament match's 1.00. Under the defaults, each earlier self-reported match between the same two teams in the last 90 days halves its weight, and a fifth one in that window is rejected.

**Losing on purpose to enter a lower division.** **Planned** in the backend.

- An Event will be able to set division eligibility by a player's highest authoritative rating over a recent window, such as 6 or 12 months, instead of their current rating. Lowering a rating before an event then stops paying off ([backend#174](https://github.com/openpickleball/backend/issues/174)).
- A player whose results run far above expectation in self-reported or recreational play and far below it in tournament or league play will be flagged for organizers, in their flag feed. The expectations come from the engine's out-of-sample predictions, and the flag rules will be published. A flag never changes a rating by itself ([backend#175](https://github.com/openpickleball/backend/issues/175)).
- A player whose results run far from their seed will be flagged for review too ([backend#51](https://github.com/openpickleball/backend/issues/51)).

The engine does not cap how far one match can move a rating, beyond the 2.0 to 8.0 range. **Planned**: a cap on the rating a team can lose to one lopsided match, off by default until it is backtested ([engine#163](https://github.com/openpickleball/engine/issues/163)).

**Multiple and colluding accounts.** Partly **implemented**, partly **planned**.

- Implemented: an established rating needs verified matches from Events an Organizer runs, so accounts that only confirm each other's self-reported matches can never become established.
- Implemented: every replay reports the net rating its matches added to or removed from each rating format, so rating created by repeated matches between the same accounts shows up.
- Planned: limit the rating that repeated matches between the same accounts can create ([engine#82](https://github.com/openpickleball/engine/issues/82)).
- Planned: detect rings of accounts that confirm each other's matches, for example a set of players whose matches are almost all against each other, from data OPEN already holds ([backend#209](https://github.com/openpickleball/backend/issues/209)).
- Planned: flag unusual submissions from trusted submitters, such as an Organizer's first matches or a large batch ([backend#206](https://github.com/openpickleball/backend/issues/206)), and show anomaly flags to organizers ([backend#213](https://github.com/openpickleball/backend/issues/213)).

These anomaly flags are planned too. OPEN will show them to organizers, and moderators will see each Organizer's flag counts. OPEN never applies an automatic penalty for them: an anomaly flag does not change a rating or stop a match counting. (A near duplicate flag is different: it holds a match, as [Duplicate detection](#4-duplicate-detection) says.)

### Known limitations

The guards above do not stop every way to game a rating. The engine README's [Known limitations](https://github.com/openpickleball/engine/blob/main/README.md#known-limitations) lists what the engine does not catch, found by simulating leagues of invented players. Reliability flags none of them.

- **Regular partners end up with the same rating.** Two players who always play together get the same updates, so the engine cannot tell who carries whom.
- **Losing on purpose is not detected.** A thrown match lowers the rating, and nothing in the rating's uncertainty or reliability shows it.
- **Made-up league matches between colluding accounts count without limit.** Only Organizer verification stands in the way. For self-reported matches, the repeat rule shrinks the gain but does not remove it.
- **A closed group can be labeled established.** The connectivity cap meant for this is off in `Config()` and in `v1` (see [Closed groups](#closed-groups)).
