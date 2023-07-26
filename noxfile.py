"""Development automation.
"""

import nox

ALL_SUPPORTED_PYTHONS = ["3.7", "3.8", "3.9", "3.10", "3.11"]
nox.options.sessions = ["lint", "docs", "test"]


@nox.session
def lint(session: nox.Session) -> None:
    session.notify("pre-commit")
    session.notify("typecheck")


@nox.session(name="pre-commit")
def pre_commit(session: nox.Session) -> None:
    session.install("pre-commit")
    session.run("pre-commit", "run", "--all-files", *session.posargs)


@nox.session(python=[ALL_SUPPORTED_PYTHONS[0], ALL_SUPPORTED_PYTHONS[-1]])
def typecheck(session: nox.Session) -> None:
    session.install("-e", ".[check-docs]")
    session.install("-r", "tests/requirements.txt")

    session.install("pyright")
    session.run(
        "pyright",
        "src",
        "tests",
        *session.posargs,
    )


@nox.session(python=ALL_SUPPORTED_PYTHONS)
def test(session: nox.Session) -> None:
    session.install("-e", ".[check-docs]")

    session.install("-r", "tests/requirements.txt")
    session.run(
        "pytest",
        "--cov=src",
        "--cov-branch",
        "--cov-report=term-missing",
        "--cov-report=html",
        *session.posargs,
    )


@nox.session
def docs(session: nox.Session) -> None:
    session.install("-e", ".")

    session.install("-r", "docs/requirements.txt")
    session.run("sphinx-build", "docs/", "build/docs")


@nox.session(name="docs-live")
def docs_live(session: nox.Session) -> None:
    session.install("-e", ".")

    session.install("-r", "docs/requirements.txt", "sphinx-autobuild")
    session.run("sphinx-autobuild", "docs/", "build/docs")
