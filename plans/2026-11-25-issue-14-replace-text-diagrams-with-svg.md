# Plan: Replace the text diagrams with SVG pictures (issue #14)

Risk tier: Medium. Docs and styling only, no workflow or script change, but how the diagrams look in light mode, dark mode, and on a narrow screen cannot be proven by a test, so it needs a live drive.

Domain skills:

- frontend-design: invoke, for the diagrams' visual design (spacing, hierarchy, legibility).
- artifact-diagramming: invoke for its inline-SVG legibility guidance in both themes only. Its Artifact-specific publishing rules do not apply.
- Every other listed skill (Django, Expo, React, API, auth, payments, email): not applicable, because the change is Markdown, SVG, CSS, and one config line.

## Acceptance criteria

1. `docs/architecture.md` ("How the pieces fit together") and `docs/match-to-rating.md` (the block after "The short version") show SVG diagrams instead of the ASCII `text` code blocks. `grep -n -- '+---' docs/*.md` prints nothing.
2. Each SVG lives in its own file in a top-level `diagrams/` directory (`diagrams/architecture.svg`, `diagrams/match-to-rating.svg`). It is inlined into the page at build time by `pymdownx.snippets` (`base_path: [diagrams]`, `check_paths: true`), so a missing file fails both `zensical build --strict` and `scripts/check_docs.py`.
3. The SVGs and their stylesheet load nothing from another host: no `href`, `xlink:href`, `src`, `@import`, `@font-face`, or `url(` other than `url(#...)`, and no `<image>`, `<script>`, or `<foreignObject>`.
4. Colors come from the theme's CSS variables (`--md-default-fg-color`, its `--light`/`--lighter`/`--lightest` variants, `--md-default-bg-color`, `--md-code-bg-color`, `--md-primary-fg-color`, `--md-accent-fg-color`) in a local stylesheet, `docs/stylesheets/diagrams.css`, added with `extra_css`. No color is hard-coded in the SVGs, so both palettes, including the manual toggle, restyle them. Text uses `font-family: inherit`.
5. Implemented and planned parts look different: a box or arrow whose current label says "planned" has a dashed outline or line, and everything else is solid. Each diagram has a small legend (solid: implemented, dashed: planned).
   - Architecture, dashed: the Frontend web app box, the arrow into it from players and organizers and its `/api/v1/ and /_allauth/` arrow to the backend (a connection that touches a planned box is planned; `tests/test_diagram_planned_links.py` checks this), the engine's "imported in-process" link to the backend, and the Status page box. Partner integrations stays solid, because the OAuth2 token endpoints exist, and keeps its "(API planned)" label. Its link to the backend is two arrows: a solid one labeled `/oauth/` (the token endpoints exist) and a dashed one labeled `/api/v1/` (no API operation accepts a partner token yet). `tests/test_diagram_partner_arrows.py` checks this.
   - Match to rating, dashed: live update, replay with provenance, the ratings box, and the arrows into and out of them.
6. Every label keeps the current wording from the ASCII diagrams (except that "/oauth/ and /api/v1/" is split into one label per arrow, see criterion 5), including the three notes under the architecture diagram (rating spec, openpb.org, status page) and the "(not OPEN ratings, served by an API that is planned)" line. No claim is added, removed, or strengthened.
7. Each `<svg>` has `role="img"`, `aria-labelledby` pointing to a `<title>` and a `<desc>`. The `<desc>` states in prose every box and connection the diagram shows, including what is planned, so a screen reader gets the same content. Element ids are unique across the site (prefix them `arch-` and `m2r-`).
8. On a narrow screen the diagram scrolls sideways inside its figure instead of shrinking text below legibility. The figure wrapper has `overflow-x: auto`, and the SVG has a `min-width` (about 640px).
9. `tests/test_diagrams.py` checks each file in `diagrams/`: it parses as XML, has the role, title, and desc from criterion 7, and contains none of the forbidden constructs from criterion 3. It also checks each file is referenced by a page under `docs/`. It also checks that ids carry the `arch-` or `m2r-` prefix and are unique, that the SVG files have no blank lines, and that `docs/stylesheets/diagrams.css` has none of the forbidden constructs from criterion 3. (Added while writing the test, so criteria 3 and 7 and the blank-line risk are covered by a test, not only by review.)
10. The gate passes: `uv sync --locked`, `uv run pytest`, `uv run python scripts/check_docs.py`, `uv run zensical build --strict`.

## Files that change

- `diagrams/architecture.svg`, `diagrams/match-to-rating.svg`: new.
- `docs/stylesheets/diagrams.css`: new.
- `mkdocs.yml`: `pymdownx.snippets` under `markdown_extensions` (after `pymdownx.superfences`), and `extra_css: [stylesheets/diagrams.css]`.
- `docs/architecture.md`, `docs/match-to-rating.md`: the code blocks become a `<figure class="open-diagram">` holding `--8<-- "<name>.svg"`. There are no blank lines inside the figure.
- `tests/test_diagrams.py`: new.
- Phase 8 may touch `CLAUDE.md` and `CONTRIBUTING.md` (repository layout, how to edit a diagram).

## Order of work

1. Commit this plan alone.
2. Write `tests/test_diagrams.py` and run it red (no `diagrams/` files yet). Commit the test.
3. Add the snippets and `extra_css` config, the stylesheet, and both SVGs. Replace both code blocks. Run the gate. Commit.
4. Live drive with `uv run zensical serve`: both pages in light mode, dark mode, and at about 375px wide. Capture screenshots as evidence.

## Risks

- Python-Markdown ends a raw HTML block at a blank line. A blank line inside the figure or inside an SVG breaks the markup, so the SVG files contain none.
- The SVG is inlined into the page, so its `<style>`, if any, would leak site-wide. Put all styling in `diagrams.css`, scoped under `.open-diagram`.
- Duplicate `id`s across the two diagrams break `aria-labelledby` and markers. Use the prefixes.
- `check_docs.py` only checks `href` and `src` for absolute links. The new test covers `xlink:href` and CSS `url()` for the SVG files.
- An arrow marker whose fill does not follow the theme. Use `fill: context-stroke` or style the marker path through `diagrams.css`.
- `zensical serve` does not watch `diagrams/`. After editing an SVG, change the page that includes it (or restart the server) to see the edit. Found during the live drive.
- Not chosen: separate `<img>` SVG files (they cannot follow the theme toggle), Mermaid (hard rule 6), and raster images (they cannot follow the theme and do not scale).

## Proof

- Criteria 2, 3, 7, 9: `tests/test_diagrams.py`, plus the build and check failing on a missing snippet.
- Criteria 1, 6: grep for the ASCII art, and a read of the rendered labels against the old blocks on `origin/main`.
- Criteria 4, 5, 8: live drive screenshots of both pages in light, dark, and narrow views.
- Criterion 10: the gate output.

Measured on `origin/main` (79cc6e0) in this worktree, then reverted:

- Inline `<svg>` inside `<figure>` in a page passes through Zensical 0.1.3 unchanged, and `extra_css` loads a stylesheet from `docs/stylesheets/`.
- `site/assets/stylesheets/classic/palette.*.css` defines `--md-default-fg-color` and its variants, and `--md-code-bg-color`, for both the default and slate schemes.
- With `pymdownx.snippets` (`base_path: [diagrams]`, `check_paths: true`), `--8<-- "t.svg"` inlines the file. Both `zensical build --strict` and `check_docs.py` exit 0. Pointing it at `missing.svg`, both exit 1 with `SnippetMissingError`.
