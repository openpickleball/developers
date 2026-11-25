# Plan: Move off Material for MkDocs before its end of life on May 5, 2027 (issue #2)

Risk tier: Medium. It replaces the build tool and changes the deploy workflow across several files, and the result can only be checked by building the site and loading it in a browser. No content or design changes.

Domain skills: none applicable. The change is build configuration, a workflow, one small Python check script, and doc lines; no framework, UI, API, data, auth, payments, or email code is touched. Use context7 or zensical.org for Zensical's own docs.

## Background

Zensical 0.1.3 (PyPI, released 2026-11-20) is the maintained successor that Material for MkDocs's end-of-life notice names. Its [migration guide](https://zensical.org/docs/compatibility/mkdocs/migration/) says it reads an existing `mkdocs.yml`, so this plan keeps `mkdocs.yml` and does not move to `zensical.toml`. Zensical has two theme variants. `classic` keeps the Material for MkDocs look and `modern` is the default, so the site sets `theme.variant: classic` to avoid a design change.

A trial build of `main`'s files under Zensical 0.1.3 (see Proof) showed that it keeps these strict failures: a link to a missing page, a link to a missing anchor on another page, and a missing local anchor. It drops three that MkDocs's `--strict` enforces: a page under `docs/` missing from `nav`, a `nav` entry naming a file that does not exist, and an absolute link such as `/stack/`. The user chose to keep those three with a small check script that CI runs next to the build.

## Acceptance criteria

1. `pyproject.toml` depends on `zensical` pinned to an exact version (`==0.1.3`) and no longer on `mkdocs-material`. `uv.lock` is regenerated with `uv lock`, and `uv sync --locked` succeeds.
2. `uv run zensical build --strict` builds the same 6 pages as `main` (`index`, `architecture`, `stack`, `match-to-rating`, `contributing`, `glossary`, plus `404.html`), at the same URLs.
3. `mkdocs.yml` sets `theme.variant: classic`. The built pages load the `classic` stylesheets. The announcement bar from `overrides/main.html` shows the current status wording on every page. The light and dark palettes and their toggle work. `theme.font: false` holds: no font is fetched. The `navigation.sections`, `navigation.footer`, and `content.code.copy` features are present.
4. `mkdocs.yml`'s `validation` block uses Zensical's keys (`invalid_links: true`, `invalid_link_anchors: true`) instead of MkDocs's `omitted_files`, `absolute_links`, `unrecognized_links`, and `anchors`. A link to a missing page, a link to a missing anchor on another page, and a missing local anchor each make `uv run zensical build --strict` exit non-zero.
5. A new script, `scripts/check_docs.py` (first line `# SPDX-License-Identifier: Apache-2.0`), exits non-zero and names the problem when: a Markdown file under `docs/` is not in `nav`; a `nav` entry names a file not under `docs/`; or a page has an absolute link (an inline link `](/...)`, a reference definition `]: /...`, or an HTML `href="/..."` or `src="/..."`, where the target starts with one `/` and not `//`). Links inside fenced code blocks and inline code spans are ignored. It exits 0 on `main`'s pages.
6. Tests in `tests/test_check_docs.py` (pytest, plain asserts, `tmp_path` fixtures) cover each failure in criterion 5, the code-block exemption, the `//` exemption, and a passing case. pytest is pinned in a `dev` dependency group in `pyproject.toml`.
7. `.github/workflows/pages.yml`'s `build` job runs `uv sync --locked`, `uv run pytest`, `uv run python scripts/check_docs.py`, and `uv run zensical build --strict`, in that order. It no longer sets `NO_MKDOCS_2_WARNING`. The job keeps the name `build`, and the deploy steps and `site` path are unchanged.
8. Loading every built page in a real browser, with the palette toggled both ways, makes no request to any host other than the local server.
9. `README.md` "Preview locally", `CONTRIBUTING.md`, `CLAUDE.md` (description, layout list, Commands), `docs/stack.md`, `docs/architecture.md`, and `docs/contributing.md` name Zensical and the new commands where they now name MkDocs or Material, and say where the check script runs. `mkdocs.yml` keeps its name and is still described as the site configuration.
10. No page content or design change beyond those lines. The hard rules hold: the status notice stays, no real player data, no names of other rating systems, nothing loaded from another host.

## Files that change

- `pyproject.toml`: replace `mkdocs-material==9.8.1` with `zensical==0.1.3`. Add `pyyaml` pinned to the version `uv lock` resolves, because the script imports it directly. Add `[dependency-groups] dev = ["pytest==<current>"]`. uv installs the `dev` group by default, so `uv sync --locked` in CI includes it.
- `uv.lock`: regenerated with `uv lock`.
- `mkdocs.yml`: add `variant: classic` under `theme`. Replace the `validation` block with Zensical's two keys. Nothing else.
- `scripts/check_docs.py` (new, Apache-2.0): reads `mkdocs.yml` with `yaml.safe_load`, flattens `nav` (strings, `{title: path}` maps, and nested lists) into the set of `.md` paths, ignoring any entry that is an external URL. Compares that set with every `*.md` under `docs/` (recursive, POSIX relative paths). Scans each page for absolute links after removing fenced code blocks (``` and ~~~) and inline code spans. Prints one line per problem as `<file>:<line>: <message>` and exits 1 if there are any, else prints nothing and exits 0. Takes optional `--config` (default `mkdocs.yml`) so tests can point it at a temporary project; the docs directory is `docs_dir` from the config, default `docs`, resolved next to the config file. Type hints on every function, pathlib, f-strings, Python 3.13 syntax. It is a CLI, so it reports problems with `print` to stderr rather than logging.
- `tests/test_check_docs.py` (new, Apache-2.0 SPDX line): calls the script's `main(argv) -> int` (or runs it with `subprocess` and `sys.executable`) against projects built in `tmp_path`.
- `.github/workflows/pages.yml`: the steps in criterion 7; drop the `env` block with `NO_MKDOCS_2_WARNING`. Keep action SHAs and comments as they are.
- `README.md`, `CONTRIBUTING.md`, `CLAUDE.md`, `docs/stack.md`, `docs/architecture.md`, `docs/contributing.md`: the lines in criterion 9.
- `.gitignore`: only if a Zensical build leaves a new untracked directory. Zensical writes `.cache/`, which is already ignored.

## Order of work

1. Commit this plan alone (`docs: plan for issue 2`).
2. Red: write `tests/test_check_docs.py` and the pytest dev group (update `uv.lock`). Run `uv run pytest` and record it failing because the script does not exist. Commit the tests.
3. Green: write `scripts/check_docs.py` until the tests pass. Run it on the repo and confirm exit 0. Commit.
4. Swap the build tool: `pyproject.toml`, `uv lock`, `mkdocs.yml`. Run the strict build. Probe criteria 4 and 5 by breaking a copy of the site in a scratch directory, never the branch. Commit.
5. Workflow: `pages.yml`. Commit.
6. Docs lines (criterion 9). Commit.
7. Full gate, in CI's order: `uv sync --locked`, `uv run pytest`, `uv run python scripts/check_docs.py`, `uv run zensical build --strict`. Then the live drive (Proof).

## Risks

- The `modern` variant would change the look. Mitigation: `variant: classic`, and the live drive checks that the classic stylesheets load.
- The Zensical bundle has lazy loaders for unpkg (glightbox, ace, a ResizeObserver polyfill) and jsdelivr (pyodide). They seem to fire only for markup this site does not use, or for browsers without ResizeObserver. Material's bundle has the same polyfill URL. Mitigation: the live drive records every network request on every page. If any page fetches from another host, stop and report it rather than patching the theme.
- Zensical is 0.1.x and moves fast. Mitigation: pin it exactly. Dependabot can propose bumps, and the strict build and the check script gate them.
- The check script could flag false positives in code examples. Mitigation: it strips fences and inline code, and a test covers that.
- `NO_MKDOCS_2_WARNING` hid a notice. After the swap the build no longer runs MkDocs, so nothing needs hiding.
- Renaming the `build` job would break the required check. The job keeps its name.
- What this plan chose not to do: move to `zensical.toml`, adopt the `modern` variant, add ruff to CI, or add any other Zensical feature.

## Proof

- Criteria 1, 2, 7: the gate output from step 7, plus `ls site` compared with `main`'s page list.
- Criterion 3: grep the built `index.html` for `assets/stylesheets/classic/`, the announce text, both `data-md-color-scheme` values, and the three features. The live drive shows the banner and toggles the palette.
- Criterion 4: in a scratch copy, add each broken link in turn and record the non-zero exit of `uv run zensical build --strict`.
- Criteria 5, 6: `uv run pytest` output, and `uv run python scripts/check_docs.py` exiting 0 on the branch. Also run it against a scratch copy with an orphan page, a missing nav file, and an absolute link, and record the exit 1 and its messages.
- Criterion 8 (live drive): serve `site/` with `python -m http.server` on localhost, open each of the 6 pages and `404.html` in Chrome, toggle the palette, and record every network request. Every request must go to the local server. Screenshot Home in both palettes, showing the banner.
- Criteria 9, 10: `git diff origin/main --stat` lists only the files named above. `grep -rni "mkdocs serve\|mkdocs build\|material for mkdocs\|Material theme" README.md CONTRIBUTING.md CLAUDE.md docs` prints nothing.

Measured on `main` (8bc4ad7), in scratch copies, with the tree left unchanged:

- `zensical==0.1.3` with `main`'s unchanged `mkdocs.yml`: `zensical build --strict` printed "No issues found" and exited 0. The output had `index.html`, `404.html`, and the 5 other page directories. The announce text was present, both `data-md-color-scheme` values were present, the features list was `["navigation.sections","navigation.footer","content.code.copy"]`, and no `fonts.googleapis` appeared.
- Broken page link `[x](nope.md)`: "Warning: page does not exist", exit 1. Broken anchors `glossary.md#no-such-anchor` and `#no-such-local`: aborted in strict mode.
- Orphan page `docs/orphan.md`, absolute link `[x](/stack/)`, and a nav entry `missing.md`: each passed `zensical build --strict` with exit 0. Under `mkdocs build --strict` (Material 9.8.1) each one aborted with 1 warning.
- Without `variant`, the build linked the `modern` stylesheets. With `variant: classic`, `index.html` linked `assets/stylesheets/classic/main.0006804e.min.css` and `classic/palette.813d4b3f.min.css`.
- `grep -rnE '\]\(/[^/]|href="/[^/]|^\[[^]]+\]: */[^/]' docs` on `main`: no matches. Every `docs/*.md` file is in `nav`, and every `nav` file exists. So the check script must exit 0 on `main`'s pages.
- Remote hosts in built HTML tags (`<script>`, `<link>`, `<img>`, `<iframe>`): only the `rel="canonical"` links to `dev.openpb.org`, the same as under Material. Those are not requests.
