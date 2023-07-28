"""Tests the functional behaviour of the base class

The various test cases in this module use DiagnsticError as a concrete subclass
since one is necessary to use the `Diagnostic` class's logic (as shown in the
first test).
"""

from __future__ import annotations

import pytest
from rich.text import Text

from diagnostic import Diagnostic, DiagnosticError


class TestDiagnostic:
    def test_rejects_direct_instantiation_due_to_no_style_given(self):
        # GIVEN / WHEN
        with pytest.raises(TypeError) as exc_info:
            Diagnostic(
                code="code",
                message="message",
                causes=[],
                hint_stmt=None,
            )

        # THEN
        error_str = str(exc_info.value)

        assert "subclass of Diagnostic" in error_str
        assert "style" in error_str

    def test_permits_creation_without_code(self) -> None:
        # GIVEN
        class DerivedError(DiagnosticError):
            pass

        # WHEN
        with pytest.raises(ValueError) as exc_info:
            DerivedError(message="", causes=[], hint_stmt=None)

        # THEN
        error_str = str(exc_info.value)
        assert "`code` must be provided" in error_str
        assert "DerivedError" in error_str

    def test_can_fetch_code_from_subclass(self) -> None:
        # GIVEN
        class DerivedError(DiagnosticError):
            code = "subclass-code"

        # WHEN
        obj = DerivedError(message="", causes=[], hint_stmt=None)

        # THEN
        assert obj.code == "subclass-code"

    def test_can_fetch_code_from_arguments(self) -> None:
        # GIVEN
        code = "subclass-code"

        # WHEN
        obj = DiagnosticError(code=code, message="", causes=[], hint_stmt=None)

        # THEN
        assert obj.code == code

    def test_can_fetch_code_from_arguments_in_subclass(self) -> None:
        # GIVEN
        class DerivedError(DiagnosticError):
            pass

        # WHEN
        obj = DerivedError(message="", causes=[], hint_stmt=None, code="subclass-code")

        # THEN
        assert obj.code == "subclass-code"

    @pytest.mark.parametrize(
        "name",
        [
            "this-is-a-good-kebab-case-name",
            "E123",
            "toolname-123",
            "toolname-category-123",
            "toolname-E123",
        ],
    )
    def test_permits_valid_names(self, name: str) -> None:
        # GIVEN
        class DerivedError(DiagnosticError):
            code = name

        # WHEN
        error = DerivedError(message="", causes=[], hint_stmt=None)

        # THEN
        assert error.code == name

    @pytest.mark.parametrize(
        "name",
        [
            "bad_name",
            "BAD_NAME",
            "_bad",
            "bad-name-",
            "bad--name",
            "-bad-name",
        ],
    )
    def test_rejects_incorrect_code_names(self, name: str) -> None:
        # GIVEN
        class DerivedError(DiagnosticError):
            code = name

        # WHEN
        with pytest.raises(ValueError) as exc_info:
            DerivedError(message="", causes=[], hint_stmt=None)

        # THEN
        error_str = str(exc_info.value)

        assert "error code" in error_str
        assert repr(name) in error_str
        assert "must be kebab-case" in error_str
        assert "DerivedError" in error_str

    def test_permits_creation_without_details_link(self) -> None:
        # GIVEN
        class DerivedError(DiagnosticError):
            code = "subclass-code"

        # WHEN
        obj = DerivedError(message="", causes=[], hint_stmt=None)

        # THEN
        assert obj.details_link is None

    def test_reject_docs_url_without_code_template(self) -> None:
        # GIVEN
        class DerivedError(DiagnosticError):
            code = "subclass-code"
            docs_index = "https://example.com/"

        # WHEN
        with pytest.raises(ValueError) as exc_info:
            DerivedError(message="", causes=[], hint_stmt=None)

        # THEN
        error_str = str(exc_info.value)

        assert "{code}" in error_str
        assert "DerivedError" in error_str

    @pytest.mark.parametrize(
        "url", ["https://example.com/{code}", "https://example.com/#{code}"]
    )
    def test_uses_docs_url_with_templated_code(self, url: str) -> None:
        # GIVEN
        class DerivedError(DiagnosticError):
            code = "subclass-code"
            docs_index = url

        expected = url.format(code=DerivedError.code)

        # WHEN
        obj = DerivedError(message="", causes=[], hint_stmt=None)

        # THEN
        assert obj.details_link == expected
        assert repr(obj) == (
            "<DerivedError("
            "code='subclass-code', "
            "message='', "
            "causes=[], "
            "note_stmt=None, "
            "hint_stmt=None, "
            f"details_link='{expected}'"
            ")>"
        )

    def test_non_list_causes(self):
        # GIVEN
        causes = "not a list"

        # WHEN
        with pytest.raises(TypeError) as exc_info:
            DiagnosticError(
                code="code",
                message="message",
                causes=causes,  # type: ignore
                hint_stmt=None,
            )

        # THEN
        error_str = str(exc_info.value)

        assert "causes" in error_str
        assert "list" in error_str
        assert "DiagnosticError" in error_str


@pytest.mark.parametrize("code_str", ["basic", "dashed-name"])
@pytest.mark.parametrize("message", ["Message", Text("Message")])
@pytest.mark.parametrize("causes", [[], ["causes"], [Text("causes")]])
@pytest.mark.parametrize("note_stmt", [None, "Note", Text("Note")])
@pytest.mark.parametrize("hint_stmt", [None, "Hint", Text("Hint")])
@pytest.mark.parametrize("docs_url", [None, "https://example.com/{code}"])
def test_diagnostic_error_repr(
    code_str: str,
    message: str | Text,
    causes: list[str] | list[Text],
    note_stmt: None | str | Text,
    hint_stmt: None | str | Text,
    docs_url: None | str,
) -> None:
    # GIVEN
    class DerivedError(DiagnosticError):
        code = code_str
        docs_index = docs_url

    err = DerivedError(
        message=message,
        causes=causes,
        note_stmt=note_stmt,
        hint_stmt=hint_stmt,
    )
    details_link = (
        repr(docs_url.format(code=code_str)) if docs_url is not None else "None"
    )

    # WHEN
    representation = repr(err)

    # THEN
    assert representation == (
        "<DerivedError("
        f"code={code_str!r}, "
        f"message={message!r}, "
        f"causes={causes!r}, "
        f"note_stmt={note_stmt!r}, "
        f"hint_stmt={hint_stmt!r}, "
        f"details_link={details_link}"
        ")>"
    )
