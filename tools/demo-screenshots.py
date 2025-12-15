"""A script to generate screenshots for the documentation."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from rich.console import Console
from rich.terminal_theme import TerminalTheme

from diagnostic import Diagnostic, DiagnosticError


def _(hex: str) -> tuple[int, int, int]:
    """Convert a hex color to an RGB tuple."""
    assert hex.startswith("#")
    return tuple(int(hex[i : i + 2], 16) for i in (1, 3, 5))


TERMINAL_THEMES = {
    # Based on Night Owl and Night Owl Light
    "light": TerminalTheme(
        foreground=_("#403F51"),
        background=_("#FBFBFB"),
        normal=[  # 8 ANSI "normal" colors, in order
            _("#403F51"),
            _("#CD4B43"),
            _("#418F6D"),
            _("#D8B13B"),
            _("#488CD1"),
            _("#C64E88"),
            _("#51A098"),
            _("#F0F0F0"),
        ],
        bright=[  # 8 ANSI "bright" colors, in order
            _("#403F51"),
            _("#CD4B43"),
            _("#418F6D"),
            _("#D8B13B"),
            _("#488CD1"),
            _("#C64E88"),
            _("#51A098"),
            _("#F0F0F0"),
        ],
    ),
    "dark": TerminalTheme(
        foreground=_("#D8DADF"),
        background=_("#2E3138"),
        normal=[  # 8 ANSI "normal" colors, in order
            _("#2E3138"),
            _("#D17277"),
            _("#A1C281"),
            _("#DFC184"),
            _("#5F89F7"),
            _("#BB7CD8"),
            _("#418F6D"),
            _("#D8DADF"),
        ],
        bright=[  # 8 ANSI "bright" colors, in order
            _("#2E3138"),
            _("#D17277"),
            _("#A1C281"),
            _("#DFC184"),
            _("#5F89F7"),
            _("#BB7CD8"),
            _("#418F6D"),
            _("#D8DADF"),
        ],
    ),
}


def render_and_save(
    diagnostic: Diagnostic,
    *,
    filename: str,
    title: str,
    theme: Literal["light", "dark"],
) -> None:
    """Render a diagnostic and save it to a file."""

    console = Console(
        record=True,
        width=101,
        # file=StringIO(),
    )
    base_dir = Path(__file__).parent.parent
    console.print(diagnostic)
    console.save_svg(
        os.fsdecode(base_dir / filename),
        title=title,
        theme=TERMINAL_THEMES[theme],
    )


class StbDiagnosticError(DiagnosticError):
    """A custom error for the `stb` command line."""

    docs_index = "https://sphinx-theme-builder.rtfd.io/errors/#{code}"


def main() -> None:
    error = StbDiagnosticError(
        code="missing-command-line-dependencies",
        message="Could not import a package that is required for the `stb` CLI.",
        causes=[
            "No module named 'build'",
        ],
        hint_stmt=(
            "During installation, make sure to include the `\\[cli]`. For example:\n"
            'pip install "sphinx-theme-builder\\[cli]"'
        ),
        note_stmt="This is a note",
    )

    render_and_save(
        error,
        filename="docs/demo-dark.svg",
        title="Sample DiagnosticError",
        theme="dark",
    )
    render_and_save(
        error,
        filename="docs/demo-light.svg",
        title="Sample DiagnosticError",
        theme="light",
    )


if __name__ == "__main__":
    main()
