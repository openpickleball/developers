# SPDX-License-Identifier: Apache-2.0
"""Partner integrations reach the backend by two arrows, one per status.

The OAuth2 token endpoints at /oauth/ exist, but no API operation at
/api/v1/ accepts a partner token yet. So the /oauth/ arrow is solid and the
/api/v1/ arrow is dashed, and no single arrow carries both labels.
"""

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
ARCHITECTURE = REPO_ROOT / "diagrams" / "architecture.svg"
SVG_NS = "{http://www.w3.org/2000/svg}"


def classes(element: ET.Element) -> set[str]:
    return set((element.get("class") or "").split())


@pytest.fixture
def root() -> ET.Element:
    return ET.fromstring(ARCHITECTURE.read_text())


def partner_box(root: ET.Element) -> ET.Element:
    """Return the rect behind the "Partner integrations" name."""
    name = next(
        t for t in root.iter(f"{SVG_NS}text") if t.text == "Partner integrations"
    )
    x, y = float(name.get("x", 0)), float(name.get("y", 0))
    for rect in root.iter(f"{SVG_NS}rect"):
        left, top = float(rect.get("x", 0)), float(rect.get("y", 0))
        right = left + float(rect.get("width", 0))
        bottom = top + float(rect.get("height", 0))
        if left <= x <= right and top <= y <= bottom:
            return rect
    raise AssertionError("no box behind Partner integrations")


def arrow_beside(root: ET.Element, label: ET.Element) -> ET.Element:
    """Return the vertical line just left of a label, level with it."""
    lx, ly = float(label.get("x", 0)), float(label.get("y", 0))
    best: tuple[float, ET.Element] | None = None
    for line in root.iter(f"{SVG_NS}line"):
        x1, x2 = float(line.get("x1", 0)), float(line.get("x2", 0))
        y1, y2 = float(line.get("y1", 0)), float(line.get("y2", 0))
        if x1 != x2 or not min(y1, y2) <= ly <= max(y1, y2) or x1 >= lx:
            continue
        gap = lx - x1
        if best is None or gap < best[0]:
            best = (gap, line)
    assert best is not None, f"no arrow beside {label.text!r}"
    return best[1]


def label(root: ET.Element, text: str) -> ET.Element:
    found = [
        t
        for t in root.iter(f"{SVG_NS}text")
        if "od-label" in classes(t) and t.text == text
    ]
    assert len(found) == 1, f"expected one arrow label {text!r}, found {len(found)}"
    return found[0]


def test_partner_arrows_are_split_by_status(root: ET.Element) -> None:
    labels = [t.text for t in root.iter(f"{SVG_NS}text")]
    assert "/oauth/ and /api/v1/" not in labels
    box = partner_box(root)
    box_bottom = float(box.get("y", 0)) + float(box.get("height", 0))
    left = float(box.get("x", 0))
    right = left + float(box.get("width", 0))
    for text, planned in [("/oauth/", False), ("/api/v1/", True)]:
        arrow = arrow_beside(root, label(root, text))
        assert left <= float(arrow.get("x1", 0)) <= right, text
        assert float(arrow.get("y1", 0)) == box_bottom, text
        assert ("od-planned" in classes(arrow)) is planned, text
