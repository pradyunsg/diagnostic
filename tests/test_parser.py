"""Tests for the parsing and discovery logic for codes in code and docs."""

import textwrap
from pathlib import Path

import pytest

from diagnostic import _parsers as parsers


class TestDocumentationParsing:
    def test_all_heading_levels_md(self, tmp_path: Path) -> None:
        # GIVEN
        document = tmp_path / "content.md"
        content = textwrap.dedent(
            """\
                # heading-1

                content

                ## heading-2

                content

                ### heading-3

                content

                ### heading-3 ignored

                content

                #### heading-4

                content

                ##### heading-5

                content

                ###### heading-6

                content
            """
        )
        document.write_text(content)

        # WHEN
        headings = parsers.find_code_headings_in_document(document)

        # THEN
        assert headings == {
            "heading-1": [(document, 1)],
            "heading-2": [(document, 5)],
            "heading-3": [(document, 9)],
            "heading-4": [(document, 17)],
            "heading-5": [(document, 21)],
            "heading-6": [(document, 25)],
        }

    def test_all_heading_levels_rst(self, tmp_path: Path) -> None:
        # GIVEN
        document = tmp_path / "content.rst"
        content = textwrap.dedent(
            """\
                =========
                heading-1
                =========

                content

                heading-2
                =========

                content

                heading-3
                ---------

                content

                heading-3 ignored
                -----------------

                content

                heading-4
                ~~~~~~~~~

                content

                heading-5
                '''''''''

                content

                heading-6
                `````````

                content
            """
        )
        document.write_text(content)

        # WHEN
        headings = parsers.find_code_headings_in_document(document)

        # THEN
        assert headings == {
            "heading-1": [(document, 3)],
            "heading-2": [(document, 8)],
            "heading-3": [(document, 13)],
            "heading-4": [(document, 23)],
            "heading-5": [(document, 28)],
            "heading-6": [(document, 33)],
        }

    def test_rejects_non_md_rst_file(self, tmp_path: Path) -> None:
        # GIVEN
        document = tmp_path / "content.asciidoc"
        document.touch()

        # WHEN / THEN
        with pytest.raises(AssertionError):
            parsers.find_code_headings_in_document(document)


class TestCodeParsing:
    def test_picking_up_code_from_class_definitions(self, tmp_path: Path) -> None:
        # GIVEN
        source_file = tmp_path / "awesome.py"
        source = textwrap.dedent(
            """
            from diagnostic import Diagnostic


            class AwesomeThing(Diagnostic):
                code = "awesome-thing"

            class DifferentAwesomeThing(Diagnostic):
                code = "different-awesome-thing"

            class DefinitelyNotAwesomeThing(Diagnostic):
                code = "definitely not awesome"

            class NotAwesomeThing(Diagnostic):
                # code = "not-awesome-thing"
                pass
            """
        )
        source_file.write_text(source)

        # WHEN
        results = parsers.find_codes_in_sources(source_file)

        # THEN
        assert results == {
            "awesome-thing": [(source_file, 5)],
            "different-awesome-thing": [(source_file, 8)],
        }

    def test_picking_up_code_from_calls(self, tmp_path: Path) -> None:
        # GIVEN
        source_file = tmp_path / "awesome.py"
        source = textwrap.dedent(
            """
            from diagnostic import DiagnosticError


            DiagnosticError(
                code="awesome",
                message="This is a message",
                causes=[],
                hint_stmt=None,
            )
            DiagnosticError(
                code="definitely not awesome",
                message="This is a message",
                causes=[],
                hint_stmt=None,
            )
            # DiagnosticError(
            #     code="not-awesome",
            #     message="This is a message",
            #     causes=[],
            #     hint_stmt=None,
            # )

            code = "different-awesome"
            DiagnosticError(
                code=code,
                message="This is a message",
                causes=[],
                hint_stmt=None,
            )
            """
        )
        source_file.write_text(source)

        # WHEN
        results = parsers.find_codes_in_sources(source_file)

        # THEN
        assert results == {
            "awesome": [(source_file, 5)],
        }


def test_directory_traversal(tmp_path: Path) -> None:
    # GIVEN
    (tmp_path / "folder").mkdir()
    (tmp_path / "folder" / "one.md").touch()
    (tmp_path / "folder" / "two.md").touch()
    (tmp_path / "folder" / "two.png").touch()
    (tmp_path / "folder" / "subfolder").mkdir()
    (tmp_path / "folder" / "subfolder" / "three.md").touch()
    (tmp_path / "four.md").touch()

    def seen(path: Path) -> parsers.codeLocationMapping:
        return {"seen": [(path, 0)]}

    # WHEN
    result = parsers.handle_directory_traversal(tmp_path, seen, extensions=(".md",))

    # THEN
    assert result == {
        "seen": [
            (tmp_path / "four.md", 0),
            (tmp_path / "folder" / "one.md", 0),
            (tmp_path / "folder" / "two.md", 0),
            (tmp_path / "folder" / "subfolder" / "three.md", 0),
        ]
    }
