# SPDX-License-Identifier: Apache-2.0
"""Constructs that could load something from another host.

The diagram SVGs and their stylesheet must contain none of these. A
fragment reference such as url(#arch-arrow) stays inside the page and is
allowed.
"""

import re

PATTERNS = [
    r"\bhref\s*=",
    r"\bsrc\s*=",
    r"\bsrcset\s*=",
    r"@import",
    r"@font-face",
    r"url\((?!\s*#)",
    r"image-set\(",
    r"<\s*(?:\w+:)?(?:image|img|script|foreignObject|object|embed|iframe)\b",
]

# HTML, SVG in HTML, and CSS keywords are case-insensitive.
FORBIDDEN_PATTERNS = [re.compile(p, re.IGNORECASE) for p in PATTERNS]


def forbidden(text: str) -> list[str]:
    """Return the pattern of every forbidden construct found in the text."""
    return [p.pattern for p in FORBIDDEN_PATTERNS if p.search(text)]
