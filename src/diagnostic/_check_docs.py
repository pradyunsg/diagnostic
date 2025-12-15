"""Check that all the errors in the source code have a documentation entry."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import rich
import rich.text
import rich.traceback
from rich.markup import escape

from . import DiagnosticError
from ._parsers import find_code_headings_in_document, find_codes_in_sources

rich.traceback.install(show_locals=True)


def _format_to_lines(
    names: set[str],
    codes: dict[str, list[tuple[Path, int]]] | dict[str, list[int]],
    *,
    kind: str,
    fallback_filename: str = "<unset>",
) -> str:
    """Format the codes to lines of text."""
    if not names:
        return ""

    lines = [f"[red]{len(names)} {kind}[/]:"]
    for name in sorted(names):
        lines.append(f"  [magenta]{escape(name)}[/]")
        for entry in codes[name]:
            if isinstance(entry, tuple):
                file, lineno = entry
                filename = str(file)
            else:
                lineno = entry
                filename = fallback_filename
            lines.append(f"    from [blue]{escape(filename)}[/]:[cyan]{lineno}[/]")
    return "\n".join(lines)


def _process(
    source: Path, docs_index: Path, verbose: bool, fail_on_extra: bool
) -> None:
    """Main entry point for the script."""
    code_codes = find_codes_in_sources(source)
    doc_codes = find_code_headings_in_document(docs_index)

    rich.print(f"Found {len(code_codes)} codes in the source code.")
    rich.print(f"Found {len(doc_codes)} codes in the documentation.")
    if verbose:
        rich.get_console().rule()
        rich.print("codes in the source code")
        for code, locations in code_codes.items():
            rich.print(f"  [green]{escape(code)}[/]")
            for filename, lineno in locations:
                rich.print(f"    [blue]{escape(str(filename))}[/]:[cyan]{lineno}[/]")

        rich.get_console().rule()
        rich.print(f"Headings in the {escape(str(docs_index))}")
        for code, linenos in doc_codes.items():
            rich.print(f"  [green]{escape(code)}[/]: {escape(repr(linenos))}")
        rich.get_console().rule()

    undocumented_codes = set(code_codes) - set(doc_codes)
    if not fail_on_extra:
        extra_codes: set[str] = set()
    else:
        extra_codes = set(doc_codes) - set(code_codes)

    if not undocumented_codes:
        rich.print("[bold green]All error codes in code are documented![/] :tada:")
    if not extra_codes and fail_on_extra:
        rich.print(
            "[bold green]All error codes in documentation exist in code![/] :tada:"
        )
    if not undocumented_codes and not extra_codes:
        return

    sections = [
        _format_to_lines(
            undocumented_codes,
            code_codes,
            kind="undocumented",
        ),
        _format_to_lines(
            extra_codes,
            doc_codes,
            kind="extra",
            fallback_filename=str(docs_index),
        ),
    ]
    causes = [rich.text.Text.from_markup(lines) for lines in sections if lines]

    if undocumented_codes and extra_codes:
        code = "undocumented-and-extra-codes"
        message = "Found undocumented and extra codes!"
    elif undocumented_codes:
        code = "undocumented-codes"
        message = "Found undocumented codes!"
    else:
        assert extra_codes
        code = "extra-codes"
        message = "Found extra codes!"

    raise DiagnosticError(
        code=code,
        message=message,
        causes=causes,
        hint_stmt=None,
    )


def _get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="diagnostic.check-docs",
        description=(
            "Check that all the errors in the source code have a documentation entry."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "source",
        metavar="source",
        help="Path to the source code file or directory.",
    )
    parser.add_argument(
        "docs_index",
        metavar="error-index",
        help="Path to the documentation file or directory serving as the error index.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print detailed information about the codes discovered.",
    )
    parser.add_argument(
        "--fail-on-extra",
        dest="fail_on_extra",
        default=True,
        action=argparse.BooleanOptionalAction,
        help=(
            "Fail if there are codes in the documentation headings, that are "
            "not in the source code."
        ),
    )
    parser.set_defaults(fail_on_extra=True)
    return parser


def main() -> None:
    """Main entry point for the script."""
    parser = _get_parser()
    args = parser.parse_args()

    source = Path(args.source)
    docs_index = Path(args.docs_index)

    if not source.exists():
        rich.print(f"Source {source} does not exist.", file=sys.stderr)
        sys.exit(1)
    if source.is_file() and not source.name.endswith(".py"):
        rich.print(f"Source {source} is not a Python file.", file=sys.stderr)
        sys.exit(1)

    if not docs_index.exists():
        rich.print(f"Error index {docs_index} does not exist.", file=sys.stderr)
        sys.exit(1)
    if docs_index.is_file() and not docs_index.name.endswith((".rst", ".md")):
        rich.print(
            f"Error index {docs_index} is not a reStructuredText or Markdown file.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        _process(source, docs_index, args.verbose, args.fail_on_extra)
    except DiagnosticError as e:
        rich.print(e, file=sys.stderr)
        sys.exit(1)
