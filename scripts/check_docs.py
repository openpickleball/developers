# SPDX-License-Identifier: Apache-2.0
"""Check the docs for problems that Zensical's strict build does not catch.

It reports a Markdown page under the docs directory that is missing from
``nav``, a ``nav`` entry that does not name a file under the docs directory,
an absolute link such as ``/stack/``, a link to a directory such as
``stack/``, and a relative link to a file that does not exist. Links in code
blocks and code spans are ignored. It prints one line per problem to stderr
and exits 1 if there are any problems, else 0.
"""

import argparse
import re
import sys
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

import yaml

FENCE_OPEN = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
BLANK_LINE = re.compile(r"(\n[ \t]*\n)")
URL_SCHEME = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
ASCII_PUNCTUATION = set("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~")
LINK_TARGETS = (
    re.compile(r"\]\(\s*(?:<([^>\n]*)>|([^)\s]*))"),
    re.compile(r"^ {0,3}\[[^\]\n]+\]:[ \t]*(?:<([^>\n]*)>|(\S+))", re.MULTILINE),
    re.compile(
        r"\b(?:href|src)\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s\"'>]+))",
        re.IGNORECASE,
    ),
)


@dataclass(frozen=True)
class Problem:
    path: str
    line: int
    message: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.message}"


def is_external(target: str) -> bool:
    """True for a target with a URL scheme, such as https: or mailto:."""
    return URL_SCHEME.match(target) is not None


def nav_paths(entry: object) -> Iterator[str]:
    """Yield every local file path named in a nav entry, in order."""
    match entry:
        case str() if is_external(entry):
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


def strip_fences(text: str) -> str:
    """Blank out fenced code blocks, keeping line numbers."""
    lines = text.split("\n")
    fence: str | None = None
    for index, line in enumerate(lines):
        if fence is None:
            opened = FENCE_OPEN.match(line)
            # A backtick fence's info string may not contain a backtick.
            if opened and not (opened.group(1)[0] == "`" and "`" in opened.group(2)):
                fence = opened.group(1)
                lines[index] = ""
            continue
        stripped = line.strip()
        if stripped.startswith(fence) and set(stripped) == {fence[0]}:
            fence = None
        lines[index] = ""
    return "\n".join(lines)


def strip_spans(paragraph: str) -> str:
    """Blank out the code spans in one paragraph."""
    out = list(paragraph)
    index = 0
    while index < len(paragraph):
        char = paragraph[index]
        if char == "\\" and paragraph[index + 1 : index + 2] in ASCII_PUNCTUATION:
            index += 2
            continue
        if char != "`":
            index += 1
            continue
        run = index
        while run < len(paragraph) and paragraph[run] == "`":
            run += 1
        opener = paragraph[index:run]
        closer = re.compile(rf"(?<!`){opener}(?!`)")
        match = closer.search(paragraph, run)
        if match is None:
            index = run
            continue
        out[index : match.end()] = blank(paragraph[index : match.end()])
        index = match.end()
    return "".join(out)


def strip_code(text: str) -> str:
    """Blank out fenced code blocks and code spans, keeping line numbers.

    A code span never crosses a blank line, so spans are found one
    paragraph at a time.
    """
    parts = BLANK_LINE.split(strip_fences(text))
    return "".join(
        part if BLANK_LINE.fullmatch(part) else strip_spans(part) for part in parts
    )


def link_targets(text: str) -> Iterator[tuple[int, str]]:
    """Yield the line and target of every link outside code."""
    prose = strip_code(text)
    for pattern in LINK_TARGETS:
        for match in pattern.finditer(prose):
            target = next(g for g in match.groups() if g is not None)
            yield prose.count("\n", 0, match.start()) + 1, target


def check_target(page: Path, docs_root: Path, target: str) -> str | None:
    """Return a message if a link target is not a file in the docs, else None."""
    if not target or target.startswith("//") or is_external(target):
        return None
    if target.startswith("/"):
        return "absolute link, use a relative link to the page"
    if target.startswith("#"):
        return None
    path = unquote(re.split(r"[#?]", target, maxsplit=1)[0])
    if not path:
        return None
    resolved = (page.parent / path).resolve()
    if path.endswith("/") or resolved.is_dir():
        return f"link to {path} does not name a file, link to the .md page"
    if not resolved.is_relative_to(docs_root) or not resolved.is_file():
        return f"link target {path} does not exist"
    return None


def link_problems(
    label: str, page: Path, docs_root: Path, text: str
) -> Iterator[Problem]:
    found: dict[tuple[int, str], None] = {}
    for line, target in link_targets(text):
        message = check_target(page, docs_root, target)
        if message is not None:
            found[(line, message)] = None
    for line, message in sorted(found):
        yield Problem(label, line, message)


def check(config_path: Path) -> list[Problem]:
    config = yaml.safe_load(config_path.read_text()) or {}
    docs_name = config.get("docs_dir", "docs")
    docs_root = (config_path.parent / docs_name).resolve()
    config_name = config_path.name
    problems: list[Problem] = []

    listed: set[str] = set()
    for entry in nav_paths(config.get("nav", [])):
        resolved = (docs_root / entry).resolve()
        if resolved.is_relative_to(docs_root) and resolved.is_file():
            listed.add(resolved.relative_to(docs_root).as_posix())
        else:
            problems.append(
                Problem(
                    config_name,
                    1,
                    f"nav names {entry}, which is not a file under {docs_name}/",
                )
            )

    pages = sorted(p.relative_to(docs_root).as_posix() for p in docs_root.rglob("*.md"))
    for page in pages:
        label = f"{docs_name}/{page}"
        if page not in listed:
            problems.append(Problem(label, 1, "page is not in nav"))
        path = docs_root / page
        problems.extend(link_problems(label, path, docs_root, path.read_text()))
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
