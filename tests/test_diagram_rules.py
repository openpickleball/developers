# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the forbidden-construct checker in diagram_rules.py.

HTML, SVG in HTML, and CSS keywords are case-insensitive, so upper-case
spellings must be caught as well as lower-case ones.
"""

import pytest
from diagram_rules import forbidden


@pytest.mark.parametrize(
    "sample",
    [
        '<IMAGE HREF="https://example.org/x.png"/>',
        '<Image width="10"/>',
        '<use XLINK:HREF="https://example.org/s.svg#a"/>',
        '<feImage SRC="https://example.org/x.png"/>',
        '<img alt="x"/>',
        '<IMG alt="x"/>',
        '<object type="image/svg+xml"></object>',
        '<embed type="image/svg+xml"/>',
        '<iframe title="x"></iframe>',
        "<SCRIPT>alert(1)</SCRIPT>",
        "<FOREIGNOBJECT/>",
        'srcset="https://example.org/x.png 1x"',
        'SRCSET="x.png 2x"',
        "background: URL(https://example.org/x.png);",
        'background: image-set("x.png" 1x);',
        "background: IMAGE-SET(url(x.png) 1x);",
        '@IMPORT "https://example.org/x.css";',
        "@Font-Face { font-family: x; }",
    ],
)
def test_forbidden_construct_is_caught(sample: str) -> None:
    assert forbidden(sample), sample


@pytest.mark.parametrize(
    "sample",
    [
        'marker-end="url(#arch-arrow)"',
        'marker-end="URL( #m2r-arrow)"',
        '<rect class="od-box" x="20" y="20" width="96" height="42" rx="8"/>',
        "<text>Status page (status.openpb.org, planned)</text>",
    ],
)
def test_allowed_construct_passes(sample: str) -> None:
    assert forbidden(sample) == [], sample
