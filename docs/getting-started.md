# Getting Started

## Installation

`diagnostic` is available on [PyPI](https://pypi.org/project/diagnostic/) and can be installed with [`pip`](https://pip.pypa.io/en/stable/):

```bash
pip install diagnostic
```

## Usage

This library's core functionality is provided by {class}`diagnostic.Diagnostic`. This class serves as an abstract base class for objects that contain diagnostic information, and is intended to be used as a base class for subclasses.

There are two concrete implementations provided:

- {class}`diagnostic.DiagnosticError` for exceptions that would be raised.
- {class}`diagnostic.DiagnosticWarning` for warnings that would be printed.

```{doctest} python
>>> from diagnostic import DiagnosticError
>>> path = "/path/to/config.yml"
>>> raise DiagnosticError(
...     code="configuration-not-found",
...     message="Configuration file not found",
...     causes=[
...         f"The configuration file was expected to be at {path}",
...     ],
...     hint_stmt="Please create the expected configuration file.",
...     note_stmt="`--config` option allows use of a different path.",
... )
Traceback (most recent call last):
    ...
diagnostic.DiagnosticError: configuration-not-found
<BLANKLINE>
Configuration file not found
<BLANKLINE>
Caused by:
--> The configuration file was expected to be at /path/to/config.yml
<BLANKLINE>
note: `--config` option allows use of a different path.
hint: Please create the expected configuration file.
>>> import rich
>>> rich.print(
...     DiagnosticError(
...         code="configuration-not-found",
...         message="Configuration file not found",
...         causes=[
...             f"The configuration file was expected to be at {path}",
...         ],
...         hint_stmt="Please create the expected configuration file.",
...         note_stmt="`--config` option allows use of a different path.",
...     )
... )
error: configuration-not-found
<BLANKLINE>
× Configuration file not found
╰─> The configuration file was expected to be at /path/to/config.yml
<BLANKLINE>
note: `--config` option allows use of a different path.
hint: Please create the expected configuration file.
```
