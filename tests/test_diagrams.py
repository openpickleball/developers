# SPDX-License-Identifier: Apache-2.0
"""Tests for the SVG diagrams in diagrams/, which pages inline with snippets."""

import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
from diagram_rules import forbidden

REPO_ROOT = Path(__file__).resolve().parent.parent
DIAGRAMS = REPO_ROOT / "diagrams"
DOCS = REPO_ROOT / "docs"
SVG_NS = "{http://www.w3.org/2000/svg}"
EXPECTED = ["architecture.svg", "match-to-rating.svg"]


def diagram_files() -> list[Path]:
    return sorted(DIAGRAMS.glob("*.svg"))


@pytest.fixture(params=EXPECTED)
def diagram(request: pytest.FixtureRequest) -> Path:
    path = DIAGRAMS / request.param
    assert path.is_file(), f"{path} is missing"
    return path


def test_expected_diagrams_are_the_only_ones() -> None:
    assert [p.name for p in diagram_files()] == EXPECTED


def test_diagram_parses_as_svg(diagram: Path) -> None:
    root = ET.fromstring(diagram.read_text())
    assert root.tag == f"{SVG_NS}svg"


def test_diagram_has_title_and_desc_for_screen_readers(diagram: Path) -> None:
    root = ET.fromstring(diagram.read_text())
    assert root.get("role") == "img"
    title = root.find(f"{SVG_NS}title")
    desc = root.find(f"{SVG_NS}desc")
    assert title is not None and (title.text or "").strip()
    assert desc is not None and (desc.text or "").strip()
    # The title is the short accessible name, the desc the long description.
    assert root.get("aria-labelledby") == title.get("id")
    assert root.get("aria-describedby") == desc.get("id")


def test_diagram_ids_are_prefixed_and_unique() -> None:
    seen: set[str] = set()
    prefixes = {"architecture.svg": "arch-", "match-to-rating.svg": "m2r-"}
    for name, prefix in prefixes.items():
        root = ET.fromstring((DIAGRAMS / name).read_text())
        for element in root.iter():
            element_id = element.get("id")
            if element_id is None:
                continue
            assert element_id.startswith(prefix), f"{name}: id {element_id}"
            assert element_id not in seen, f"{name}: duplicate id {element_id}"
            seen.add(element_id)


def test_diagram_loads_nothing_from_another_host(diagram: Path) -> None:
    assert forbidden(diagram.read_text()) == [], diagram.name


def test_diagram_has_no_blank_lines(diagram: Path) -> None:
    lines = diagram.read_text().splitlines()
    assert all(line.strip() for line in lines), f"{diagram.name} has a blank line"


def test_diagram_is_referenced_by_a_page(diagram: Path) -> None:
    snippet = f'--8<-- "{diagram.name}"'
    pages = [p for p in DOCS.rglob("*.md") if snippet in p.read_text()]
    assert pages, f"no page under docs/ includes {diagram.name}"


def test_diagram_stylesheet_loads_nothing_from_another_host() -> None:
    stylesheet = DOCS / "stylesheets" / "diagrams.css"
    assert stylesheet.is_file(), f"{stylesheet} is missing"
    assert forbidden(stylesheet.read_text()) == [], "diagrams.css"


def diagram_figures() -> list[tuple[Path, str]]:
    """Return each page's open-diagram figures, from <figure to </figure>."""
    pattern = re.compile(r'<figure\b[^>]*class="open-diagram".*?</figure>', re.DOTALL)
    return [
        (page, match.group(0))
        for page in sorted(DOCS.rglob("*.md"))
        for match in pattern.finditer(page.read_text())
    ]


def test_pages_have_diagram_figures() -> None:
    assert len(diagram_figures()) == len(EXPECTED)


def test_diagram_figure_has_no_blank_lines() -> None:
    # A blank line ends a raw HTML block in Python-Markdown.
    for page, figure in diagram_figures():
        lines = figure.splitlines()
        assert all(line.strip() for line in lines), f"{page.name}: blank line"


def test_diagram_figure_can_be_scrolled_by_keyboard() -> None:
    for page, figure in diagram_figures():
        tag = figure.split(">", 1)[0]
        assert 'tabindex="0"' in tag, page.name
        label = re.search(r'aria-label="([^"]+)"', tag)
        assert label and label.group(1).strip(), page.name
