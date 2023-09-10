"""The main functional unit of this package.
"""

from __future__ import annotations

import dataclasses
import re
import textwrap
from typing import ClassVar, Iterator, Sequence

import rich
import rich.console
import rich.text

RE_code = re.compile(
    r"""
    ^                         # start
        [a-zA-Z][a-zA-Z0-9]*  # with "name" segment
        (
            -                 # then a dash
            [a-zA-Z0-9]+      # followed by "name-or-number" segment
        )*                    # allow multiple segments, separated by dashes
    $                         # end
    """,
    re.VERBOSE,
)
_RE_TAGS = re.compile(
    r"""((\\*)\[([a-z#/@][^[]*?)])""",  # copied over from rich
    re.VERBOSE,
)


def _is_valid_code(s: str) -> bool:
    return re.match(RE_code, s) is not None


def _ensure_text(s: str | rich.text.Text) -> rich.text.Text:
    if isinstance(s, str):
        return rich.text.Text(s)
    return s


def _index_prefix_rich(
    s: str | rich.text.Text,
    console: rich.console.Console,
    *,
    prefix: str,
    indent: str,
) -> rich.text.Text:
    lines = _ensure_text(s).split(allow_blank=True)
    body = console.render_str(f"\n{indent}", overflow="ignore").join(lines)
    return console.render_str(prefix, overflow="ignore") + body


def _indent_prefix(s: str | rich.text.Text, *, prefix: str, indent: str) -> str:
    first, _, rest = _ensure_text(s).plain.partition("\n")
    return "\n".join(filter(None, [prefix + first, textwrap.indent(rest, indent)]))


@dataclasses.dataclass(frozen=True)
class DiagnosticStyle:
    name: str
    color: str
    ascii_symbol: str
    unicode_symbol: str


class Diagnostic:
    """An object that holds diagnostic information to present to a reader."""

    style: ClassVar[DiagnosticStyle]
    """Data about how this diagnostic should be presented"""

    docs_index: ClassVar[str | None] = None
    """
    URL to the documentation index page(s). Must contain a "{code}" placeholder,
    which will be replaced with the code of this instance.
    """

    code: str | None = None
    """
    A unique code to help readers identify this in output, documentation, etc.

    This should be a string of the form "name[-name-or-number]*", where "name" is
    a string of letters and numbers, and "name-or-number" is a string of letters,
    numbers, and dashes.
    """

    message: str | rich.text.Text
    """A short description."""

    causes: Sequence[str | rich.text.Text]
    """A list of strings describing the causes."""

    hint_stmt: str | rich.text.Text | None
    """A hint for what the reader might want to do next."""

    note_stmt: str | rich.text.Text | None
    """
    A note with additional information, that's not part of the "causes" but
    could be useful to know for the reader.
    """

    details_link: str | None
    """
    A link to more details about the problem.

    This is determined automatically if :attr:`code` is set, and
    :attr:`docs_index` is set.
    """

    def __init__(
        self,
        *,
        code: str | None = None,
        message: str | rich.text.Text,
        causes: list[str] | list[rich.text.Text] | list[str | rich.text.Text],
        hint_stmt: str | rich.text.Text | None,
        note_stmt: str | rich.text.Text | None = None,
    ) -> None:
        """
        :param code: Maps to :attr:`code`.
        :param message: Maps to :attr:`message`.
        :param causes: Maps to :attr:`causes`.
        :param hint_stmt: Maps to :attr:`hint_stmt`.
        :param note_stmt: Maps to :attr:`note_stmt`.
        """
        super().__init__()

        if code is None:
            if self.__class__.code is None:
                raise ValueError(
                    f"Cannot create {self.__class__.__name__} object: "
                    "`code` must be provided!"
                )
            code = self.__class__.code
        if not _is_valid_code(code):
            raise ValueError(
                f"Cannot create {self.__class__.__name__} object: "
                f"error code {code!r} must be kebab-case and start "
                "with a character!"
            )
        if not isinstance(causes, list):  # type: ignore
            raise TypeError(
                f"Cannot create {self.__class__.__name__} object: "
                f"`causes` must be a list, not {type(causes).__name__}!"
            )
        if not hasattr(self.__class__, "style"):
            raise TypeError(
                f"Cannot create {self.__class__.__name__} object: "
                "`style` must be set in a subclass of Diagnostic!"
            )

        self.code = code

        self.message = message
        self.causes = causes

        self.note_stmt = note_stmt
        self.hint_stmt = hint_stmt

        if self.__class__.docs_index is not None:
            if "{code}" not in self.__class__.docs_index:
                raise ValueError(
                    f"Cannot create {self.__class__.__name__} object: "
                    "`docs_index` must contain a {code} placeholder!"
                )
            self.details_link: str | None = self.__class__.docs_index.format(
                code=self.code
            )
        else:
            self.details_link = None

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}("
            f"code={self.code!r}, "
            f"message={self.message!r}, "
            f"causes={self.causes!r}, "
            f"note_stmt={self.note_stmt!r}, "
            f"hint_stmt={self.hint_stmt!r}, "
            f"details_link={self.details_link!r}"
            ")>"
        )

    def __str__(self) -> str:
        return "\n".join(self._str_parts())

    def _str_parts(self) -> Iterator[str]:
        assert self.code is not None
        yield self.code
        yield ""
        yield _ensure_text(self.message).plain
        if self.causes:
            yield ""
            yield "Caused by:"
            for item in self.causes:
                yield _indent_prefix(item, prefix="--> ", indent="    ")
        if self.note_stmt is not None or self.hint_stmt is not None:
            yield ""
        if self.note_stmt is not None:
            yield _indent_prefix(self.note_stmt, prefix="note: ", indent="      ")
        if self.hint_stmt is not None:
            yield _indent_prefix(self.hint_stmt, prefix="hint: ", indent="      ")
        if self.details_link is not None:
            yield ""
            yield f"For more details, see {self.details_link}"

    def __rich_console__(
        self,
        console: rich.console.Console,
        options: rich.console.ConsoleOptions,
    ) -> rich.console.RenderResult:
        yield (
            f"[{self.style.color} bold]{self.style.name}[/]: " f"[bold]{self.code}[/]"
        )
        yield ""

        if not options.ascii_only:
            # Present the main message, with relevant causes indented.
            if self.causes:
                yield _index_prefix_rich(
                    self.message,
                    console,
                    prefix=f"[{self.style.color}]{self.style.unicode_symbol}[/] ",
                    indent=f"[{self.style.color}]│[/] ",
                )
                for item in self.causes[:-1]:
                    yield _index_prefix_rich(
                        item,
                        console,
                        prefix=f"[{self.style.color}]├─>[/] ",
                        indent=f"[{self.style.color}]│  [/] ",
                    )
                yield _index_prefix_rich(
                    self.causes[-1],
                    console,
                    prefix=f"[{self.style.color}]╰─>[/] ",
                    indent=f"[{self.style.color}]   [/] ",
                )
            else:
                yield _index_prefix_rich(
                    self.message,
                    console,
                    prefix=f"[{self.style.color}]×[/] ",
                    indent="  ",
                )
        else:
            yield _ensure_text(self.message)
            if self.causes:
                yield ""
                for item in self.causes:
                    yield _ensure_text(item)

        if not (self.note_stmt is None and self.hint_stmt is None):
            yield ""

        if self.note_stmt is not None:
            yield _index_prefix_rich(
                self.note_stmt,
                console,
                prefix="[magenta bold]note[/]: ",
                indent="      ",
            )
        if self.hint_stmt is not None:
            yield _index_prefix_rich(
                self.hint_stmt,
                console,
                prefix="[cyan bold]hint[/]: ",
                indent="      ",
            )

        if self.details_link is not None:
            yield ""
            yield f"For more details, see {self.details_link}"
