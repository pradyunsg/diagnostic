"""Development automation."""

import nox

ALL_SUPPORTED_PYTHONS = ["3.10", "3.11", "3.12", "3.13", "3.14"]
nox.options.sessions = ["lint", "docs", "test"]


@nox.session
def lint(session: nox.Session) -> None:
    session.notify("prek")
    session.notify("typecheck")


@nox.session(name="prek")
def prek(session: nox.Session) -> None:
    session.install("prek")
    session.run("prek", "run", "--all-files", *session.posargs)


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
