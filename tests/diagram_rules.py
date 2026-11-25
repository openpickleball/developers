# SPDX-License-Identifier: Apache-2.0
"""Constructs that could load something from another host.

The diagram SVGs and their stylesheet must contain none of these. A
fragment reference such as url(#arch-arrow) stays inside the page and is
allowed.
"""

import re

FORBIDDEN_PATTERNS = [
    re.compile(r"\bhref\s*="),
    re.compile(r"\bsrc\s*="),
    re.compile(r"@import"),
    re.compile(r"@font-face"),
    re.compile(r"url\(\s*(?!#)"),
    re.compile(r"<\s*(?:\w+:)?image\b"),
    re.compile(r"<\s*(?:\w+:)?script\b"),
    re.compile(r"<\s*(?:\w+:)?foreignObject\b"),
]


def forbidden(text: str) -> list[str]:
    """Return the pattern of every forbidden construct found in the text."""
    return [p.pattern for p in FORBIDDEN_PATTERNS if p.search(text)]
