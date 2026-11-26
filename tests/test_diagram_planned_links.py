# SPDX-License-Identifier: Apache-2.0
"""A connection that touches a planned (dashed) box must be dashed too.

Under each diagram's legend, solid means implemented, so a solid arrow into
or out of a planned box would claim a working path through it.
"""

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
DIAGRAMS = REPO_ROOT / "diagrams"
SVG_NS = "{http://www.w3.org/2000/svg}"
TOUCH = 4.0


@dataclass(frozen=True)
class Box:
    x: float
    y: float
    width: float
    height: float

    def touches(self, px: float, py: float) -> bool:
        """True if the point is within TOUCH units of the box's outline."""
        left, right = self.x, self.x + self.width
        top, bottom = self.y, self.y + self.height
        near_x = left - TOUCH <= px <= right + TOUCH
        near_y = top - TOUCH <= py <= bottom + TOUCH
        on_side = abs(px - left) <= TOUCH or abs(px - right) <= TOUCH
        on_edge = abs(py - top) <= TOUCH or abs(py - bottom) <= TOUCH
        return near_x and near_y and (on_side or on_edge)


@dataclass(frozen=True)
class Connection:
    label: str
    ends: tuple[tuple[float, float], tuple[float, float]]
    planned: bool


def classes(element: ET.Element) -> set[str]:
    return set((element.get("class") or "").split())


def path_ends(d: str) -> tuple[tuple[float, float], tuple[float, float]]:
    """Return the first and last points of an M/V/H/L path."""
    tokens = re.findall(r"[MVHL]|-?\d+(?:\.\d+)?", d)
    x = y = 0.0
    points: list[tuple[float, float]] = []
    command = ""
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token in "MVHL":
            command = token
            index += 1
            continue
        if command in "ML":
            x, y = float(token), float(tokens[index + 1])
            index += 2
        elif command == "V":
            y = float(token)
            index += 1
        elif command == "H":
            x = float(token)
            index += 1
        points.append((x, y))
    return points[0], points[-1]


def connections(root: ET.Element) -> list[Connection]:
    found: list[Connection] = []
    for element in root.iter():
        if "od-line" not in classes(element):
            continue
        if element.tag == f"{SVG_NS}line":
            ends = (
                (float(element.get("x1", 0)), float(element.get("y1", 0))),
                (float(element.get("x2", 0)), float(element.get("y2", 0))),
            )
        elif element.tag == f"{SVG_NS}path":
            ends = path_ends(element.get("d", ""))
        else:
            continue
        label = ET.tostring(element, encoding="unicode").strip()
        found.append(Connection(label, ends, "od-planned" in classes(element)))
    return found


def planned_boxes(root: ET.Element) -> list[Box]:
    return [
        Box(
            float(rect.get("x", 0)),
            float(rect.get("y", 0)),
            float(rect.get("width", 0)),
            float(rect.get("height", 0)),
        )
        for rect in root.iter(f"{SVG_NS}rect")
        if "od-planned" in classes(rect)
    ]


@pytest.mark.parametrize("name", ["architecture.svg", "match-to-rating.svg"])
def test_connection_touching_a_planned_box_is_planned(name: str) -> None:
    root = ET.fromstring((DIAGRAMS / name).read_text())
    boxes = planned_boxes(root)
    solid = [
        c.label
        for c in connections(root)
        if not c.planned and any(b.touches(*end) for b in boxes for end in c.ends)
    ]
    assert solid == [], f"{name}: solid connection touches a planned box"
