"""Supporting functions for parsing the source code and documentation.
"""

import ast
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Callable

if sys.version_info >= (3, 10):  # pragma: no cover
    from typing import TypeAlias
else:  # pragma: no cover
    from typing_extensions import TypeAlias

import docutils
import docutils.core
import docutils.nodes
import rich
from markdown_it import MarkdownIt
from rich.markup import escape

from ._base import RE_code

codeLocationMapping: TypeAlias = "dict[str, list[tuple[Path, int]]]"


def _ignoring(*, ctx: str, what: str, why: str, where: "tuple[Path, int]") -> None:
    rich.print(f"[yellow]Ignoring {escape(what)}[/]")
    rich.print(f"  [magenta]{escape(str(where[0]))}[/]:[cyan]{where[1]}[/]")
    rich.print(f"  [blue]{ctx}[/]: {escape(why)}")


def handle_directory_traversal(
    path: Path,
    func: Callable[[Path], codeLocationMapping],
    *,
    extensions: "tuple[str, ...]",
) -> codeLocationMapping:
    if not path.is_dir():
        assert path.name.endswith(
            extensions
        ), f"expected {path} to end with one of {extensions}"
        return func(path)

    codes: codeLocationMapping = defaultdict(list)
    for dirpath, _, filenames in os.walk(path):
        for filename in filenames:
            if filename.endswith(extensions):
                these_codes = func(Path(dirpath) / filename)
                for code, locations in these_codes.items():
                    codes[code].extend(locations)
    return codes


def find_codes_in_sources(src_path: Path) -> codeLocationMapping:
    """Find all the codes in the source code, using the AST.

    This uses the AST to find all the error codes in the source code. An
    error code is found in two ways:

    - A class with a `code` attribute, which is a string literal.
    - A call with a `code` keyword argument, which is a string literal.

    Returns:
        A dictionary mapping the code to a list of (filename, line number)
        tuples, where the code was found.
    """

    def find_codes_in_file(file: Path) -> codeLocationMapping:
        codes: defaultdict[str, list[tuple[Path, int]]] = defaultdict(list)

        with open(file) as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for attr in node.body:
                    if (
                        isinstance(attr, ast.Assign)
                        and len(attr.targets) == 1
                        and isinstance(attr.targets[0], ast.Name)
                        and attr.targets[0].id == "code"
                        and isinstance(attr.value, ast.Str)
                    ):
                        ref = attr.value.s
                        if not RE_code.match(ref):
                            _ignoring(
                                ctx="class-attribute",
                                what=f"{ref!r}",
                                why="not a valid code",
                                where=(file, node.lineno),
                            )
                            continue
                        codes[ref].append((file, node.lineno))
            elif isinstance(node, ast.Call):
                for kw in node.keywords:
                    if kw.arg == "code" and isinstance(kw.value, ast.Str):
                        ref = kw.value.s
                        if not RE_code.match(ref):
                            _ignoring(
                                ctx="call-argument",
                                what=f"{ref!r}",
                                why="not a valid code",
                                where=(file, node.lineno),
                            )
                            continue
                        codes[ref].append((file, node.lineno))

        return codes

    return handle_directory_traversal(src_path, find_codes_in_file, extensions=(".py",))


def find_code_headings_in_document(doc_path: Path) -> codeLocationMapping:
    """Finds all the level 2+ headings within the document.

    Returns:
        A dictionary mapping the code to a list of line numbers, where the
        heading was found.
    """

    def find_codes_in_file(doc_path: Path) -> codeLocationMapping:
        if doc_path.name.endswith(".md"):
            return find_code_headings_in_markdown(doc_path)
        else:
            assert doc_path.name.endswith(".rst")
            return find_code_headings_in_rst(doc_path)

    return handle_directory_traversal(
        doc_path, find_codes_in_file, extensions=(".md", ".rst")
    )


def find_code_headings_in_markdown(doc_path: Path) -> codeLocationMapping:
    """Finds potential code headings in a Markdown document.

    Returns:
        A dictionary mapping the code to a list of line numbers, where the
        heading was found.
    """
    parser = MarkdownIt()
    tokens = parser.parse(Path(doc_path).read_text())  # type: ignore

    found_headings: list[tuple[str, int]] = []
    current_heading: "tuple[str, int] | None" = None
    for token in tokens:
        if token.type == "heading_open":
            assert not current_heading, "active heading already"
            current_heading = ("", -1)
        elif token.type == "heading_close":
            assert current_heading, "no active heading"
            # Skip headings that are not codes
            if RE_code.match(current_heading[0]):
                found_headings.append(current_heading)
            current_heading = None
        elif current_heading is not None:
            assert token.type == "inline", "expected inline token"
            assert token.map, "expected line info"
            new_text = current_heading[0] + token.content
            assert isinstance(new_text, str)
            current_heading = (new_text, token.map[0] + 1)

    codes: codeLocationMapping = defaultdict(list)
    for heading, lineno in found_headings:
        codes[heading].append((doc_path, lineno))  # pyright: ignore

    return codes


def find_code_headings_in_rst(doc_path: Path) -> codeLocationMapping:
    """Finds all the level 2+ headings within the document.

    Returns:
        A dictionary mapping the code to a list of line numbers, where the
        heading was found.
    """

    with open(doc_path) as f:
        rst_string = f.read()

    # Parse the reStructuredText document
    document: docutils.nodes.document = docutils.core.publish_doctree(rst_string)

    # Iterate through the document and extract all headings
    codes: codeLocationMapping = defaultdict(list)
    for node in document.findall(
        condition=lambda n: getattr(n, "tagname", None) == "title"
    ):
        heading_text = node.astext()

        # Determine the level of the heading
        heading_level = -1  # we'll always have `document` as the parent
        tree = node
        while tree.parent is not None:
            tree = tree.parent
            heading_level += 1

        # Skip headings that are not codes
        if not RE_code.match(heading_text):
            continue

        assert node.line
        codes[heading_text].append((doc_path, node.line))

    return codes
