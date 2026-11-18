# Glossary

One line per term. The source of truth is the backend's [`CONTEXT.md`](https://github.com/openpickleball/backend/blob/main/CONTEXT.md), which has the full definitions and the matching engine and backend names. Where they differ, `CONTEXT.md` is right.

## People and accounts

- **Player**: a person who plays matches and has ratings. Every Player belongs to the one Account that created it.
- **Account**: a registered OPEN login, keyed on email. It has at most one Player.
- **Display Name**: the name a Player shows to others.
- **Legal Name**: a Player's full legal name, private, used only for identity checks and organizer verification.
- **Age Group**: a band derived from a Player's birth year and month. OPEN never stores the day.
- **Privacy Setting**: a Player's choice of who sees one of their other profile details.
- **Gender Division**: men's, women's, or none, used for divisions and gender-specific Rating Formats.
- **Organizer**: a person or body that runs events and submits results. A verified Organizer's submissions count as confirmed.
- **Organizer Member**: an Account that acts for an Organizer, as admin or match manager.
- **Club**: a place or group where players play.
- **Club Role**: an Account's role at a Club, admin or match manager.
- **Event**: a tournament, league, or verified rec play that an Organizer runs.
- **Partner**: an app, league platform, club, or tournament that integrates with OPEN through the APIs, for free.
- **Partner Application**: the OAuth client a Partner registers. It starts unapproved.
- **Club Application Grant**: a Club's permission for one Partner Application to submit its matches.
- **External ID**: a Player's identifier in another system, used only for identity matching.
- **OPEN Code**: the public identifier for a Player, Club, Event, Organizer, or Match, such as `P-7K3M-QX9H` (made up). It never changes.

## Matches and results

- **Match**: one completed contest between two teams, with one or more game scores.
- **Game**: one scored unit inside a Match, such as 11-8. A Match has 1 to 5 Games.
- **Game Format**: how each game is scored: side-out or rally, and points to win (11, 15, or 21).
- **Match Type**: where the result came from: tournament, league, verified rec play, or self-reported.
- **Confirmation**: agreement that a reported score is correct. Only a confirmed Match can count.
- **Dispute**: a participant's statement that a score is wrong. The Match stops counting until a moderator resolves it.
- **Correction**: the new Match that replaces a wrong one. The wrong one is voided, never edited.
- **Submission**: a request to add a Match. It becomes part of the Ledger only after permission, validation, duplicate checks, and Confirmation.
- **Flagged Match**: a Match held from counting for moderator review, for example as a possible duplicate.
- **Ledger**: the append-only, ordered record of every counted Match, and the source of truth for ratings.

## Ratings

- **Rating**: a number on the 2.0 to 8.0 scale for one Player in one Rating Format.
- **Rating Format**: singles, doubles, mixed doubles, men's doubles, or women's doubles.
- **RD (rating deviation)**: how uncertain a Rating is. It grows with inactivity and shrinks with play.
- **Reliability**: a 0 to 100% score shown with every Rating, earned through OPEN matches.
- **Seed**: a Player's starting Rating before any OPEN matches.
- **External Rating Snapshot**: a verified rating from a standard external rating system, used only as a Seed.
- **Imported Reliability**: the external system's reliability, shown separately from OPEN-earned Reliability.
- **Replay**: rebuilding all Ratings from Seeds and the full Ledger as of a date. It gives the authoritative Ratings.
- **Replay Info**: the provenance stored with every Replay: as-of date, config version, config fingerprint, and match counts.
- **Live Update**: a provisional rating change applied when a Match arrives, between Replays.
- **Frozen**: a player whose rating is used in a Match but does not move, because the Match is dated on or before their imported baseline.
- **Clamped**: a player whose change was cut short by the rating floor or ceiling.
- **Shadow Mode**: running the engine on real results without publishing or relying on its Ratings.

## Records and governance

- **Audit Event**: one recorded sensitive action, append-only. Audit Events never feed ratings.
- **Rating Spec**: the published, versioned definition of how OPEN ratings are calculated. Only the governing board changes it.
- **Conformance**: meeting the board's published requirements for showing an OPEN rating.
