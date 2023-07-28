"""Concrete classes for diagnostic objects, for use in standard Python toolchain.
"""

from ._base import Diagnostic, DiagnosticStyle


class DiagnosticError(Diagnostic, Exception):
    """An exception that requires additional diagnostic information to be provided.

    This is a subclass of Exception and can be used as a normal exception, with
    the typical exception handling mechanisms. It can also be printed using
    `rich` to get a pretty presentation of the error.
    """

    style = DiagnosticStyle(
        name="error",
        color="red",
        ascii_symbol="x",
        unicode_symbol="×",
    )


class DiagnosticWarning(Diagnostic, Warning):
    """A warning that requires additional diagnostic information to be provided.

    This is a subclass of Warning and can be used as a normal warning, with
    the typical"""

    style = DiagnosticStyle(
        name="warning",
        color="yellow",
        ascii_symbol="!",
        unicode_symbol="!",
    )


# Don't expose the private module name.
DiagnosticError.__module__ = "diagnostic"
DiagnosticWarning.__module__ = "diagnostic"
