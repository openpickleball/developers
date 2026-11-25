# SPDX-License-Identifier: Apache-2.0
"""Tests for scripts/check_docs.py, run as a CLI against temporary projects."""

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "check_docs.py"


@dataclass
class Result:
    code: int
    stderr: str


def run_check(config: Path) -> Result:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--config", str(config)],
        capture_output=True,
        text=True,
        check=False,
    )
    return Result(code=proc.returncode, stderr=proc.stderr)


def make_project(
    root: Path,
    nav: str,
    pages: dict[str, str],
    docs_dir: str | None = None,
) -> Path:
    config = root / "mkdocs.yml"
    lines = ["site_name: Test site"]
    if docs_dir is not None:
        lines.append(f"docs_dir: {docs_dir}")
    lines.append(nav)
    config.write_text("\n".join(lines) + "\n")
    docs = root / (docs_dir or "docs")
    for name, text in pages.items():
        page = docs / name
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text(text)
    return config


@pytest.fixture
def basic_nav() -> str:
    return "nav:\n  - Home: index.md\n  - Stack: stack.md\n"


def test_clean_project_passes(tmp_path: Path, basic_nav: str) -> None:
    config = make_project(
        tmp_path,
        basic_nav,
        {"index.md": "# Home\n\nSee [stack](stack.md).\n", "stack.md": "# Stack\n"},
    )
    result = run_check(config)
    assert result.code == 0
    assert result.stderr == ""


def test_page_missing_from_nav_fails(tmp_path: Path, basic_nav: str) -> None:
    config = make_project(
        tmp_path,
        basic_nav,
        {"index.md": "# Home\n", "stack.md": "# Stack\n", "orphan.md": "# Orphan\n"},
    )
    result = run_check(config)
    assert result.code == 1
    assert "orphan.md" in result.stderr
    assert "nav" in result.stderr


def test_nested_page_missing_from_nav_fails(tmp_path: Path, basic_nav: str) -> None:
    config = make_project(
        tmp_path,
        basic_nav,
        {"index.md": "# Home\n", "stack.md": "# Stack\n", "sub/deep.md": "# Deep\n"},
    )
    result = run_check(config)
    assert result.code == 1
    assert "sub/deep.md" in result.stderr


def test_nav_entry_for_missing_file_fails(tmp_path: Path) -> None:
    nav = "nav:\n  - Home: index.md\n  - Missing: missing.md\n"
    config = make_project(tmp_path, nav, {"index.md": "# Home\n"})
    result = run_check(config)
    assert result.code == 1
    assert "missing.md" in result.stderr


def test_nested_nav_and_bare_entries_are_read(tmp_path: Path) -> None:
    nav = (
        "nav:\n"
        "  - index.md\n"
        "  - Section:\n"
        "      - Stack: stack.md\n"
        "      - Deeper:\n"
        "          - sub/deep.md\n"
        "  - Source: https://example.org/source\n"
    )
    config = make_project(
        tmp_path,
        nav,
        {"index.md": "# Home\n", "stack.md": "# Stack\n", "sub/deep.md": "# Deep\n"},
    )
    result = run_check(config)
    assert result.code == 0, result.stderr
    assert result.stderr == ""


@pytest.mark.parametrize(
    "line",
    [
        "See [stack](/stack/).",
        "[stack]: /stack/",
        '<a href="/stack/">stack</a>',
        '<img src="/logo.png" alt="logo">',
    ],
)
def test_absolute_link_fails(tmp_path: Path, basic_nav: str, line: str) -> None:
    config = make_project(
        tmp_path,
        basic_nav,
        {"index.md": f"# Home\n\n{line}\n", "stack.md": "# Stack\n"},
    )
    result = run_check(config)
    assert result.code == 1
    assert "index.md:3:" in result.stderr
    assert "absolute" in result.stderr


@pytest.mark.parametrize(
    "line",
    [
        "See [cdn](//example.org/x).",
        "[cdn]: //example.org/x",
        '<a href="//example.org/x">cdn</a>',
        "See [site](https://example.org/x).",
    ],
)
def test_protocol_relative_and_full_urls_pass(
    tmp_path: Path, basic_nav: str, line: str
) -> None:
    config = make_project(
        tmp_path,
        basic_nav,
        {"index.md": f"# Home\n\n{line}\n", "stack.md": "# Stack\n"},
    )
    result = run_check(config)
    assert result.code == 0, result.stderr


def test_links_in_code_are_ignored(tmp_path: Path, basic_nav: str) -> None:
    page = (
        "# Home\n"
        "\n"
        'Inline `[x](/stack/)` and ``<a href="/y">`` are code.\n'
        "\n"
        "```markdown\n"
        "[x](/stack/)\n"
        "[ref]: /stack/\n"
        "```\n"
        "\n"
        "~~~html\n"
        '<a href="/stack/">x</a>\n'
        "~~~\n"
    )
    config = make_project(
        tmp_path, basic_nav, {"index.md": page, "stack.md": "# Stack\n"}
    )
    result = run_check(config)
    assert result.code == 0, result.stderr


def test_absolute_link_after_code_block_reports_its_line(
    tmp_path: Path, basic_nav: str
) -> None:
    page = "# Home\n\n```\n[x](/a/)\n```\n\nSee [stack](/stack/).\n"
    config = make_project(
        tmp_path, basic_nav, {"index.md": page, "stack.md": "# Stack\n"}
    )
    result = run_check(config)
    assert result.code == 1
    assert "index.md:7:" in result.stderr
    assert "index.md:4:" not in result.stderr


def test_docs_dir_from_config_is_used(tmp_path: Path, basic_nav: str) -> None:
    config = make_project(
        tmp_path,
        basic_nav,
        {"index.md": "# Home\n", "stack.md": "# Stack\n"},
        docs_dir="content",
    )
    result = run_check(config)
    assert result.code == 0, result.stderr


def test_repository_pages_pass() -> None:
    result = run_check(REPO_ROOT / "mkdocs.yml")
    assert result.code == 0, result.stderr


def two_pages(text: str) -> dict[str, str]:
    return {"index.md": text, "stack.md": "# Stack\n"}


@pytest.mark.parametrize(
    "page",
    [
        "Use a ` here.\n\n[x](/stack/)\n\nAnd ` again.\n",
        "a \\` b [x](/stack/) c \\` d\n",
        "```code``` is inline.\n\n[x](/stack/)\n",
    ],
    ids=["span-across-blank-line", "escaped-backticks", "inline-triple-backticks"],
)
def test_backticks_that_are_not_code_do_not_hide_links(
    tmp_path: Path, basic_nav: str, page: str
) -> None:
    config = make_project(tmp_path, basic_nav, two_pages(page))
    result = run_check(config)
    assert result.code == 1
    assert "absolute" in result.stderr


@pytest.mark.parametrize("entry", ["../mkdocs.yml", "/etc/hostname"])
def test_nav_entry_outside_docs_fails(tmp_path: Path, entry: str) -> None:
    nav = f"nav:\n  - Home: index.md\n  - R: {entry}\n"
    config = make_project(tmp_path, nav, {"index.md": "# Home\n"})
    result = run_check(config)
    assert result.code == 1
    assert entry in result.stderr


def test_nav_entry_with_non_http_scheme_is_external(tmp_path: Path) -> None:
    nav = "nav:\n  - Home: index.md\n  - Mail: mailto:a@example.org\n"
    config = make_project(tmp_path, nav, {"index.md": "# Home\n"})
    result = run_check(config)
    assert result.code == 0, result.stderr


def test_nav_paths_are_normalized(tmp_path: Path) -> None:
    nav = "nav:\n  - Home: ./index.md\n"
    config = make_project(tmp_path, nav, {"index.md": "# Home\n"})
    result = run_check(config)
    assert result.code == 0, result.stderr


@pytest.mark.parametrize(
    "line",
    [
        "See [stack](stack/).",
        "[stack]: stack/",
        '<a href="stack/">stack</a>',
    ],
)
def test_directory_link_fails(tmp_path: Path, basic_nav: str, line: str) -> None:
    config = make_project(tmp_path, basic_nav, two_pages(f"# Home\n\n{line}\n"))
    result = run_check(config)
    assert result.code == 1
    assert "index.md:3:" in result.stderr
    assert "stack/ does not name a file" in result.stderr


@pytest.mark.parametrize(
    ("line", "target"),
    [
        ("![x](missing.png)", "missing.png"),
        ("See [x](files/missing.pdf).", "files/missing.pdf"),
        ("[x]: files/missing.pdf", "files/missing.pdf"),
        ('<img src="missing.png" alt="x">', "missing.png"),
        ("See [x](../mkdocs.yml).", "../mkdocs.yml"),
    ],
)
def test_link_to_missing_file_fails(
    tmp_path: Path, basic_nav: str, line: str, target: str
) -> None:
    config = make_project(tmp_path, basic_nav, two_pages(f"# Home\n\n{line}\n"))
    result = run_check(config)
    assert result.code == 1
    assert "index.md:3:" in result.stderr
    assert f"link target {target} does not exist" in result.stderr


def test_relative_links_to_existing_files_pass(tmp_path: Path) -> None:
    nav = "nav:\n  - Home: index.md\n  - Stack: stack.md\n  - Deep: sub/deep.md\n"
    pages = {
        "index.md": (
            "# Home\n\n"
            "[a](stack.md#part) [b](stack.md?x=1) [c](#local) ![d](img/logo.png)\n"
            '<img src="img/logo.png" alt="d"> [e](mailto:a@example.org)\n'
            "[ref]: sub/deep.md\n"
        ),
        "stack.md": "# Stack\n",
        "sub/deep.md": "# Deep\n\n[home](../index.md) ![d](../img/logo.png)\n",
        "img/logo.png": "png\n",
    }
    config = make_project(tmp_path, nav, pages)
    result = run_check(config)
    assert result.code == 0, result.stderr


@pytest.mark.parametrize(
    "page",
    [
        "# Home\n\n!!! example\n\n    ```md\n    [a](other.md)\n\n    [b](stack/)\n    ```\n",
        "# Home\n\n- Item\n\n    ~~~~\n    [a](/stack/)\n    ~~~~\n",
    ],
    ids=["admonition", "list-item"],
)
def test_indented_fences_are_ignored(tmp_path: Path, basic_nav: str, page: str) -> None:
    config = make_project(tmp_path, basic_nav, two_pages(page))
    result = run_check(config)
    assert result.code == 0, result.stderr


def test_link_after_indented_fence_is_checked(tmp_path: Path, basic_nav: str) -> None:
    page = "# Home\n\n!!! note\n\n    ```\n    [a](/x/)\n    ```\n\n[b](/stack/)\n"
    config = make_project(tmp_path, basic_nav, two_pages(page))
    result = run_check(config)
    assert result.code == 1
    assert "index.md:9:" in result.stderr
    assert "index.md:6:" not in result.stderr


@pytest.mark.parametrize(
    "line",
    ["[Note]: this line is prose.", "[^1]: A footnote body."],
    ids=["prose", "footnote"],
)
def test_prose_after_label_is_not_a_reference_definition(
    tmp_path: Path, basic_nav: str, line: str
) -> None:
    config = make_project(tmp_path, basic_nav, two_pages(f"# Home\n\n{line}\n"))
    result = run_check(config)
    assert result.code == 0, result.stderr


@pytest.mark.parametrize(
    "line",
    [
        '[x]: files/missing.pdf "Title"',
        "[x]: files/missing.pdf 'Title'",
        "[x]: files/missing.pdf (Title)",
    ],
)
def test_reference_definition_with_title_is_checked(
    tmp_path: Path, basic_nav: str, line: str
) -> None:
    config = make_project(tmp_path, basic_nav, two_pages(f"# Home\n\n{line}\n"))
    result = run_check(config)
    assert result.code == 1
    assert "link target files/missing.pdf does not exist" in result.stderr


@pytest.mark.parametrize(
    ("page", "expected"),
    [
        (
            (
                "- item\n\n    ```\n    code\n\n"
                "See [the stack](/stack/) and [missing](files/missing.pdf).\n"
            ),
            [
                "index.md:6: absolute link",
                "index.md:6: link target files/missing.pdf does not exist",
            ],
        ),
        (
            "Some text\n    ```\nmore [a](/abs2/)\n\nand [b](/abs3/)\n",
            ["index.md:3: absolute link", "index.md:5: absolute link"],
        ),
        ("# H\n\n```\nnot closed\n\n[a](/abs1/)\n", ["index.md:6: absolute link"]),
    ],
    ids=["unclosed-list-fence", "continuation-backticks", "unclosed-top-fence"],
)
def test_backticks_that_do_not_make_a_fence_do_not_hide_links(
    tmp_path: Path, basic_nav: str, page: str, expected: list[str]
) -> None:
    config = make_project(tmp_path, basic_nav, two_pages(page))
    result = run_check(config)
    assert result.code == 1
    for line in expected:
        assert line in result.stderr


@pytest.mark.parametrize(
    "title",
    ["'it's'", "(see (x))", '"a "b" c"'],
    ids=["inner-quote", "nested-parens", "inner-double-quotes"],
)
def test_reference_with_odd_title_is_checked(
    tmp_path: Path, basic_nav: str, title: str
) -> None:
    page = f"Hi [x][r].\n\n[r]: /abs/ {title}\n"
    config = make_project(tmp_path, basic_nav, two_pages(page))
    result = run_check(config)
    assert result.code == 1
    assert "absolute link" in result.stderr


@pytest.mark.parametrize(
    ("page", "line"),
    [
        ("!!! note\n\n    See [x][r].\n\n    [r]: /abs9/\n", 5),
        ("- See [x][r].\n\n    [r]: /abs10/\n", 3),
    ],
    ids=["admonition", "list-item"],
)
def test_indented_reference_definition_is_checked(
    tmp_path: Path, page: str, line: int
) -> None:
    nav = (
        "nav:\n  - Home: index.md\n  - Stack: stack.md\n"
        "markdown_extensions:\n  - admonition\n  - pymdownx.superfences\n"
    )
    config = make_project(tmp_path, nav, two_pages(page))
    result = run_check(config)
    assert result.code == 1
    assert f"index.md:{line}: absolute link" in result.stderr


@pytest.mark.parametrize(
    ("page", "expected"),
    [
        (
            "Type <code> by mistake then [abs](/stack/).\n\nLater [b](/other/).\n",
            ["index.md:1: absolute link", "index.md:3: absolute link"],
        ),
        ("<pre><code>x</pre> then [s](/zzz/)\n", ["index.md:1: absolute link"]),
    ],
    ids=["stray-code", "unbalanced-pre"],
)
def test_stray_raw_code_tags_do_not_hide_later_links(
    tmp_path: Path, basic_nav: str, page: str, expected: list[str]
) -> None:
    config = make_project(tmp_path, basic_nav, two_pages(page))
    result = run_check(config)
    assert result.code == 1
    for line in expected:
        assert line in result.stderr


def test_repository_pages_pass_from_another_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    result = run_check(REPO_ROOT / "mkdocs.yml")
    assert result.code == 0, result.stderr
    assert result.stderr == ""
