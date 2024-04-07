"""Present errors that contain causes better understand what happened.
"""

from ._base import Diagnostic, DiagnosticStyle
from ._concrete import DiagnosticError, DiagnosticWarning

__all__ = ["DiagnosticStyle", "Diagnostic", "DiagnosticError", "DiagnosticWarning"]
__version__ = "2.1.0"
