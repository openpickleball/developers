# SPDX-License-Identifier: Apache-2.0
"""Check the docs for problems that Zensical's strict build does not catch.

It reports a Markdown page under the docs directory that is missing from
``nav``, a ``nav`` entry that does not name a file under the docs directory,
an absolute link such as ``/stack/``, a link to a directory such as
``stack/``, and a relative link to a file that does not exist. It finds links
by rendering each page with Python-Markdown and the same extensions Zensical
uses, so links in code are ignored exactly as the build ignores them. It
prints one line per problem to stderr and exits 1 if there are any problems,
else 0.
"""

import argparse
import re
import sys
from collections.abc import Iterator
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote

import markdown
import yaml
from zensical.config import parse_mkdocs_config

URL_SCHEME = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
CODE_TAGS = {"pre", "code"}
LINK_ATTRIBUTES = {"href", "src"}


@dataclass(frozen=True)
class Problem:
    path: str
    line: int
    message: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.message}"


@dataclass(frozen=True)
class Renderer:
    """Python-Markdown settings, built the way Zensical builds them."""

    extensions: list[str]
    configs: dict[str, dict[str, object]] = field(default_factory=dict)

    @classmethod
    def from_config(cls, config_path: Path) -> "Renderer":
        config = parse_mkdocs_config(str(config_path))
        return cls(config["markdown_extensions"], config["mdx_configs"])

    def render(self, text: str) -> tuple[str, list[str]]:
        """Return the page's HTML and every reference definition's target."""
        md = markdown.Markdown(
            extensions=self.extensions, extension_configs=self.configs
        )
        html = md.convert(text)
        return html, [url for url, _title in md.references.values()]


class LinkCollector(HTMLParser):
    """Collect href and src values that are not inside pre or code."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.targets: list[str] = []
        self.code_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in CODE_TAGS:
            self.code_depth += 1
        if self.code_depth:
            return
        for name, value in attrs:
            if name in LINK_ATTRIBUTES and value is not None:
                self.targets.append(value)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag not in CODE_TAGS:
            self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        if tag in CODE_TAGS and self.code_depth:
            self.code_depth -= 1


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


def link_targets(renderer: Renderer, text: str) -> list[str]:
    """Return every link target the rendered page has outside code.

    Reference definitions count even when no link uses them.
    """
    html, references = renderer.render(text)
    collector = LinkCollector()
    collector.feed(html)
    collector.close()
    return collector.targets + references


def source_line(text: str, target: str) -> int:
    """Return the first source line that contains the target, else 1."""
    for candidate in (target, unquote(target)):
        index = text.find(candidate)
        if index >= 0:
            return text.count("\n", 0, index) + 1
    return 1


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
    label: str, page: Path, docs_root: Path, renderer: Renderer
) -> Iterator[Problem]:
    text = page.read_text()
    found: dict[tuple[int, str], None] = {}
    for target in link_targets(renderer, text):
        message = check_target(page, docs_root, target)
        if message is not None:
            found[(source_line(text, target), message)] = None
    for line, message in sorted(found):
        yield Problem(label, line, message)


def check(config_path: Path) -> list[Problem]:
    config = yaml.safe_load(config_path.read_text()) or {}
    docs_name = config.get("docs_dir", "docs")
    docs_root = (config_path.parent / docs_name).resolve()
    config_name = config_path.name
    renderer = Renderer.from_config(config_path)
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
        problems.extend(link_problems(label, docs_root / page, docs_root, renderer))
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
