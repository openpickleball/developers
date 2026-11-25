# Plan: Update the match-to-rating page for engine 1.0.0 (issue #15)

Risk tier: Low. Prose edits to one Markdown page. No build configuration, theme, workflow, or script changes. The strict build and `scripts/check_docs.py` cover links and anchors; the risk is an inaccurate claim, handled by the sources below.

Domain skills: none applicable. The change is plain Markdown; no framework, UI, API, data, auth, payments, or email code is touched.

## Sources, checked on 2026-11-25

- Engine release `v1.0.0` (latest). Engine README on `main`, section "Known limitations".
- Engine `PARAMETERS.md` on `main`: `v1` declares `scale_by_scoring` 1.0 (against 2.9 in `Config()`), fits the side-out win calibration (0.476, against 1.0), and scales `k_min` and `k_max` by 1.0 / 1.112. The default-change rule failed its gain bar, so `Config()` keeps its defaults and `v1` ships as a named set loaded with `Config.published("v1")`.
- Engine README: under `v1`, the sandbagging and collusion effects were 1.9 to 2.6 times as large as under `Config()`.
- `openpickleball/evaluation` README (public): "Initial evaluation, not pre-registered. ... no result here is confirmatory. No OPEN rating is live." Its `preregistration/` holds a locked plan for a test on play after 2026-11-24, not yet scored. The README names other rating systems; the site must not.
- Issue states: engine#164, engine#163, engine#82, engine#86, engine#172, backend#206, backend#213 are open. engine#49 ("Publish a versioned release for the evaluation to pin") is closed, so the Evaluation section's link to it as the shadow-mode step is stale.
- backend#206 and backend#213: OPEN detects unusual submissions and suspicious patterns and flags them, but never applies an automatic penalty. Organizers see the flags for their Events (backend#213); moderators see each Organizer's flag counts (backend#206).

## Acceptance criteria

1. The Evaluation section links `https://github.com/openpickleball/evaluation`, says it holds the methodology and results of an initial evaluation on one club's play, says it was not pre-registered so no result is confirmatory, and says a pre-registered test on later play is still pending (planned). It no longer says the evaluation "is not published yet", and no longer cites engine#49.
2. `docs/index.md` and `overrides/main.html` are unchanged (they keep "forthcoming report" until engine#172 changes the engine's wording).
3. No page under `docs/` and no line of `overrides/` names another rating system: `grep -rniE '\belo\b|glicko|trueskill|dupr|\butr\b' docs overrides` prints nothing.
4. The "Guarding against gamed ratings" section gains a "Known limitations" part that summarizes, in one or two sentences each, the four limitations from the engine README (regular partners share one rating; losing on purpose is not detected; made-up league matches between colluding accounts count without limit, with only Organizer verification in the way; a closed group can be labeled established), says reliability flags none of them, and links the README's Known limitations anchor. The section intro no longer implies the guards are complete.
5. Step 8 says that the published parameter set `v1` declares a scale of 1.0 (against 2.9) and changes K, that it showed no measurable gain over the defaults so `Config()` is unchanged, and that the evaluation's simulations found `v1` makes gaming pay more. It links `https://github.com/openpickleball/engine/blob/main/PARAMETERS.md`.
6. Planned links, each marked **Planned**:
   - engine#164 in "Reliability and established ratings", keeping the implemented `established` rule text (reliability at least 60 and 3 counted verified matches) as written.
   - engine#163 linked from the sentence that says the engine does not cap one match's change.
   - backend#206 and backend#213, with a sentence that OPEN flags suspicious patterns for organizers and moderators and never applies an automatic penalty.
7. The self-reported repeat rule (implemented) and engine#82 (planned) stay in separate, separately marked places.
8. Hard rules hold: no real player data, nothing says ratings are validated or live, nothing loaded from another host, no emojis or em dashes in the changed text.
9. `uv run pytest`, `uv run python scripts/check_docs.py`, and `uv run zensical build --strict` pass.

## Files that change

- `docs/match-to-rating.md` only.

## Order of work

All edits are in `docs/match-to-rating.md`. Use these wordings or close equivalents; keep the page's plain, short sentences.

1. **Step 8, after the Weight bullet's paragraph (before "Every result reports ...")**, add a paragraph:
   "The engine also ships a published parameter set, `v1`, which a caller loads on purpose with `Config.published("v1")`. It is the first set fitted on match data. It declares a scale of 1.0 in place of the default 2.9, fits the side-out win calibration, and lowers K to match. On held-out matches it showed no measurable gain over the defaults, so `Config()` is unchanged. The evaluation's simulations also found that `v1` moves ratings faster, so losing on purpose and colluding accounts move ratings further under it. See [PARAMETERS.md](https://github.com/openpickleball/engine/blob/main/PARAMETERS.md)."
2. **Reliability and established ratings**: after the established paragraph, add: "**Planned**: cap the reliability number itself below 60 until a player has the minimum verified matches, so a player with only self-reported matches never shows 60 or more ([engine#164](https://github.com/openpickleball/engine/issues/164))." Do not change the established rule text.
3. **Evaluation**: change the marker line to: "**Implemented** in the engine: the tools. **Published**: an initial evaluation. **Planned**: a pre-registered test on later play, and testing the engine on real match results in shadow mode." Replace the sentences from "The engine was evaluated on one club's closed pool" to the end of the paragraph with: "The [evaluation repository](https://github.com/openpickleball/evaluation) holds the methodology and results of an initial evaluation on one club's play. It was not pre-registered, so no result in it is confirmatory. A test on matches played after the evaluation, registered in advance, is still pending. The evaluation compares the engine with standard external rating systems. Testing the engine on real results in shadow mode, and publishing validation results, are steps on the [roadmap](https://github.com/openpickleball/.github/blob/main/ROADMAP.md) before any rating goes live." (Drop the engine#49 link: that issue is closed and was about a release tag.)
4. **Guarding against gamed ratings**: change the intro to say each guard is marked like the steps above, none costs a player anything or needs a paid verification, and the guards are not complete: see Known limitations below.
5. In the "Losing on purpose" part, change "The engine does not cap how far one match can move a rating, beyond the 2.0 to 8.0 range." to keep that fact and add: "**Planned**: a cap on the rating a team can lose to one lopsided match, off by default until it is backtested ([engine#163](https://github.com/openpickleball/engine/issues/163))."
6. In "Multiple and colluding accounts", keep the self-reported repeat rule where it is (the Self-reported matches guard, implemented) and engine#82 as its own Planned bullet. Add a Planned bullet: "Planned: flag unusual submissions from trusted submitters, such as an Organizer's first matches or a large batch ([backend#206](https://github.com/openpickleball/backend/issues/206)), and show anomaly flags to organizers ([backend#213](https://github.com/openpickleball/backend/issues/213))." Then a sentence after the list: "OPEN flags suspicious patterns for organizers and moderators, and never applies an automatic penalty: a flag does not change a rating or stop a match counting."
7. Add a final subsection `### Known limitations` at the end of the Guarding section (a `###` under the `##`, so it gets an anchor), intro: "The guards above do not stop every way to game a rating. The engine README's [Known limitations](https://github.com/openpickleball/engine/blob/main/README.md#known-limitations) lists what engine 1.0.0 does not catch, found by simulating leagues of invented players. Reliability flags none of them." Then four bullets, one or two sentences each:
   - Regular partners end up with the same rating: two players who always play together get the same updates, so the engine cannot tell who carries whom.
   - Losing on purpose is not detected: a thrown match lowers the rating, and nothing in the rating's uncertainty or reliability shows it.
   - Made-up league matches between colluding accounts count without limit. Only Organizer verification stands in the way. (Self-reported matches are limited by the repeat rule.)
   - A closed group can be labeled established: the connectivity cap meant for this is off by default (link to the Closed groups section, `#closed-groups`).
   Link the intro in step 4 to `#known-limitations`.
8. Run the gate. Then build and grep `site/match-to-rating/index.html` for "evaluation repository", "PARAMETERS.md", "engine/issues/164", "engine/issues/163", "backend/issues/206", "backend/issues/213", and `id="known-limitations"`.

## Departures during implementation

- Step 6: the sentence after the list is scoped to anomaly flags and marked planned: "These anomaly flags are planned too. OPEN will show them to organizers and moderators, and never applies an automatic penalty for them: an anomaly flag does not change a rating or stop a match counting." It adds that a near duplicate flag is different and holds a match, linking `#4-duplicate-detection`. The suggested wording said "a flag does not ... stop a match counting", which contradicts step 4 of the page, where a near duplicate flag holds both matches. backend#206 and backend#213 are open, so the flags are not built yet.
- Step 7: the intro says the README "lists what the engine does not catch" instead of "what engine 1.0.0 does not catch". The README says its findings come from a pre-1.0 build (0.3.0.dev0).

## Risks

- Overclaiming: saying the evaluation validates the engine. The text must say "not pre-registered" and "no result is confirmatory".
- Naming a competitor while summarizing the evaluation. Criterion 3's grep catches the common names.
- Anchor collision: `#known-limitations` must be unique on the page. No other heading has that text today.
- Banner mismatch: the page will say the evaluation is published while Home and the banner say "forthcoming report". The issue asks for exactly this until engine#172; do not touch them.

## Proof

- Criteria 1, 4, 5, 6, 7: read the diff, and the grep of the built page in step 8.
- Criterion 2: `git diff --stat origin/main` lists only the page and this plan.
- Criterion 3: the grep in criterion 3. Measured on `origin/main` (79cc6e0): `grep -rniE 'elo\b|glicko|trueskill|dupr|utr\b' docs/ overrides/` printed nothing, exit 1.
- Criterion 9: gate output.
- Live drive: the build plus the grep of the rendered HTML in step 8.
