"""Present errors that contain causes better understand what happened."""

from ._base import Diagnostic, DiagnosticStyle
from ._concrete import DiagnosticError, DiagnosticWarning

__all__ = ["Diagnostic", "DiagnosticError", "DiagnosticStyle", "DiagnosticWarning"]
__version__ = "3.0.0"
