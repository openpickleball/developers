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
