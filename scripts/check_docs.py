# SPDX-License-Identifier: Apache-2.0
"""Check the docs for problems that Zensical's strict build does not catch.

It reports a Markdown page under the docs directory that is missing from
``nav``, a ``nav`` entry that names a file that does not exist, and an
absolute link such as ``/stack/``. Links in code blocks and code spans are
ignored. It prints one line per problem to stderr and exits 1 if there are
any problems, else 0.
"""

import argparse
import re
import sys
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import yaml

FENCE_OPEN = re.compile(r"^ {0,3}(`{3,}|~{3,})")
CODE_SPAN = re.compile(r"(`+)(.+?)(?<!`)\1(?!`)", re.DOTALL)
ABSOLUTE_LINKS = (
    re.compile(r"\]\(\s*<?/(?!/)"),
    re.compile(r"^ {0,3}\[[^\]]+\]:\s*<?/(?!/)", re.MULTILINE),
    re.compile(r"\b(?:href|src)\s*=\s*[\"']?/(?!/)", re.IGNORECASE),
)


@dataclass(frozen=True)
class Problem:
    path: str
    line: int
    message: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.message}"


def nav_paths(entry: object) -> Iterator[str]:
    """Yield every local file path named in a nav entry, in order."""
    match entry:
        case str() if "://" in entry:
            return
        case str():
            yield entry
        case dict():
            for value in entry.values():
                yield from nav_paths(value)
        case list():
            for item in entry:
                yield from nav_paths(item)


def blank(text: str) -> str:
    """Replace every character but newlines with a space."""
    return re.sub(r"[^\n]", " ", text)


def strip_code(text: str) -> str:
    """Blank out fenced code blocks and code spans, keeping line numbers."""
    lines = text.split("\n")
    fence: str | None = None
    for index, line in enumerate(lines):
        if fence is None:
            opened = FENCE_OPEN.match(line)
            if opened:
                fence = opened.group(1)
                lines[index] = ""
            continue
        stripped = line.strip()
        if stripped.startswith(fence) and set(stripped) == {fence[0]}:
            fence = None
        lines[index] = ""
    prose = "\n".join(lines)
    return CODE_SPAN.sub(lambda m: blank(m.group(0)), prose)


def absolute_links(path: str, text: str) -> Iterator[Problem]:
    prose = strip_code(text)
    found: set[int] = set()
    for pattern in ABSOLUTE_LINKS:
        for match in pattern.finditer(prose):
            found.add(prose.count("\n", 0, match.start()) + 1)
    for line in sorted(found):
        yield Problem(path, line, "absolute link, use a relative link to the page")


def check(config_path: Path) -> list[Problem]:
    config = yaml.safe_load(config_path.read_text()) or {}
    docs_name = config.get("docs_dir", "docs")
    docs_dir = config_path.parent / docs_name
    config_name = config_path.name
    problems: list[Problem] = []

    in_nav = list(nav_paths(config.get("nav", [])))
    for entry in in_nav:
        if not (docs_dir / entry).is_file():
            problems.append(
                Problem(config_name, 1, f"nav names {entry}, which does not exist")
            )

    pages = sorted(p.relative_to(docs_dir).as_posix() for p in docs_dir.rglob("*.md"))
    listed = set(in_nav)
    for page in pages:
        if page not in listed:
            problems.append(Problem(f"{docs_name}/{page}", 1, "page is not in nav"))
        text = (docs_dir / page).read_text()
        problems.extend(absolute_links(f"{docs_name}/{page}", text))
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", type=Path, default=Path("mkdocs.yml"))
    args = parser.parse_args(argv)
    problems = check(args.config)
    for problem in problems:
        print(problem, file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
