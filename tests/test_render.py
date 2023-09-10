"""Test the rendering of DiagnosticError objects."""

from __future__ import annotations

import io
import os
from typing import Any, cast

import pytest
import yaml
from rich.console import Console
from rich.text import Text

from diagnostic import DiagnosticError


# --- Data loading -------------------------------------------------------------
def load_data_from_yaml(filename: str) -> list[dict[str, Any]]:
    def my_rich_text_constructor(
        loader: yaml.FullLoader, node: yaml.ScalarNode
    ) -> Text:
        return Text.from_markup(cast(str, loader.construct_scalar(node)))

    complete_filename = os.path.join(
        os.path.dirname(__file__),
        "data",
        filename,
    )

    yaml.add_constructor("!text", my_rich_text_constructor)  # type: ignore
    with open(complete_filename) as f:
        return yaml.load(f, yaml.FullLoader)  # type: ignore


error_data = pytest.mark.parametrize(
    "data",
    load_data_from_yaml("error.yml"),
    ids=lambda data: data["name"],
)


error_color_data = pytest.mark.parametrize(
    "data",
    load_data_from_yaml("error-color.yml"),
    ids=lambda data: data["name"],
)


# --- Helpers ------------------------------------------------------------------
def create_error(given: dict[str, Any]) -> DiagnosticError:
    class DerivedError(DiagnosticError):
        docs_index = given["docs_index"]

    return DerivedError(
        code=given["code"],
        message=given["message"],
        causes=given["causes"],
        note_stmt=given["note_stmt"],
        hint_stmt=given["hint_stmt"],
    )


def rendered_in_ascii(error: DiagnosticError, *, color: bool = False) -> str:
    with io.BytesIO() as stream:
        console = Console(
            file=io.TextIOWrapper(stream, encoding="ascii"),
            color_system="truecolor" if color else None,
        )
        with console.capture() as capture:
            console.print(error)
    return capture.get()


def rendered_in_unicode(error: DiagnosticError, *, color: bool = False) -> str:
    with io.StringIO() as stream:
        console = Console(
            force_terminal=False,
            file=stream,
            color_system="truecolor" if color else None,
        )
        console.print(error)
        return stream.getvalue()


# --- Tests --------------------------------------------------------------------
@error_data
def test_str(data: dict[str, Any]) -> None:
    # GIVEN
    err = create_error(data["given"])

    # WHEN
    result = str(err)

    # THEN
    assert result == data["str"]


@error_data
def test_ascii(data: dict[str, Any]) -> None:
    # GIVEN
    err = create_error(data["given"])

    # WHEN
    result = rendered_in_ascii(err)

    # THEN
    assert result == data["ascii"]


@error_data
def test_unicode(data: dict[str, Any]) -> None:
    # GIVEN
    err = create_error(data["given"])

    # WHEN
    result = rendered_in_unicode(err)

    # THEN
    assert result == data["unicode"]


@error_color_data
def test_ascii_color(data: dict[str, Any]) -> None:
    # GIVEN
    err = create_error(data["given"])
    replaced_ascii = data["ascii"].replace("\\e", "\x1b")

    # WHEN
    result = rendered_in_ascii(err, color=True)

    # THEN
    assert result == replaced_ascii, "ascii"


@error_color_data
def test_unicode_color(data: dict[str, Any]) -> None:
    # GIVEN
    err = create_error(data["given"])
    replaced_unicode = data["unicode"].replace("\\e", "\x1b")

    # WHEN
    result = rendered_in_unicode(err, color=True)

    # THEN
    assert result == replaced_unicode, "unicode"


def test_rich_text_string() -> None:
    # GIVEN
    err = DiagnosticError(
        code="test-diagnostic",
        message=Text("This contains a number (1.0)."),
        causes=[Text("This contains a URL (https://example.com).")],
        hint_stmt=Text("This contains a number (1.0)."),
        note_stmt=Text("This contains a number (1.0)."),
    )

    # WHEN
    str_result = str(err)

    # THEN
    assert str_result == (
        "test-diagnostic\n"
        "\n"
        "This contains a number (1.0).\n"
        "\n"
        "Caused by:\n"
        "--> This contains a URL (https://example.com).\n"
        "\n"
        "note: This contains a number (1.0).\n"
        "hint: This contains a number (1.0)."
    )
