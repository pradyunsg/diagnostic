"""Helpers for testing."""

import textwrap


def assert_matches(rendered: str, expected: str, *, newline: bool = True) -> None:
    """Assert that the rendered text matches the expected text.

    This handles the dedent and newline handling before comparing the strings, as
    well as enforcing the expected newline at the end of the string.
    """
    __tracebackhide__ = True

    assert rendered.rstrip("\n") == textwrap.dedent(expected).strip("\n")
    if newline:
        assert rendered.endswith("\n"), f"Expected newline at end: {rendered!r}"
    else:
        assert not rendered.endswith("\n"), f"Expected no newline at end: {rendered!r}"
