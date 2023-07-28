# Tips

This document contains some tips/suggestions around using `diagnostic` in your project. These are intended to help set expectations, and to help you craft better error messages when using `diagnostic`.

## Pick a single style for `code` within a project

A consistent style for `code` makes the tool as a whole feel more cohesive. There are multiple styles that work well with `Diagnostic`:

- `kebab-case`: These are lower-case words separated by hyphens. This is the style that is used by [sphinx-theme-builder](https://sphinx-theme-builder.readthedocs.io/en/latest/errors/) (which also has an "errors" page listing all errors with "What the user can do").
- `E1234`: These are error codes that are similar to the error codes used by [Rust](https://doc.rust-lang.org/error-index.html).
- `TS1234`: These are error codes that are similar to the error codes used by TypeScript, with a `TS` prefix which makes them easier to search for.

## Use `causes` to provide context

`causes` is intended to be used to provide context to understand what happened and why it is a problem. It serves a distinct purpose to Python's built-in `Exception`'s `__cause__` and `__context__` attributes, which reflect the exception chain as Python objects.

`causes` is supposed to tell the user what happened, which combined with the `message`, should help them understand what the problem is. It is not intended to be used to provide a stack trace or similar information (not unless _that_ is useful context, and isn't something that the traceback above the error won't present).

## Use complete sentences for `note_stmt` and `hint_stmt`

`note_stmt` and `hint_stmt` are intended to be complete sentences (hence the `_stmt` suffix). They should serve as relevant detail or actionable guidance, rather than just being a random additional piece of information.

## Expect to spend effort on error messages

Good error messages are not easy to write. They require an investment of thought and effort to do well, and often are at odds with "quick and dirty" fixes.

Be willing to spend time on error messages _and_ the supporting documentation around it all. The users of your project will thank you for it (or, selfishly, not show up on the issue tracker complaining about certain things).

## Skip attributes when they are not useful

`Diagnostic` permits passing `None` to nearly all of its arguments. Notably, hint statements and note statements can be skipped if the error message is clear enough to be actionable without them.

While this is useful in some cases, it is important to be careful when using this flexibility. In particular, it is important to ensure that the error message is still actionable and that the error message is still clear.

## Using `code` well

One of the pieces that `DiagnosticError` requires is that each error should have a `code`. Ideally, this is a unique identifier for the error condition. This is useful for one main reason: it allows users to search for the error message and get specific results.

It also makes it possible for projects to create an error index page which, when done well, can eliminate the need for users to search for the error message in the first place.

(docs_index)=

## Docs Index Page(s)

Inspired by [Rust's error index](https://doc.rust-lang.org/error-index.html), {any}`Diagnostic` subclasses can use the `docs_index` attribute to provide a documentation URL.

The error index page(s) serve a way to provide more information about the error that a user has encountered. Notably, they serve as an excellent place to provide detailed description of what causes the error and for guidance on how to fix the error. This can be _especially_ useful for users who are not familiar with the project.

Ideally, it should be a _complete_ list of all error messages that the project can produce. This does take some effort to create, but it serves as an important piece of the usability and discoverability puzzle when it comes to error messages.

That said, an error index page is not a substitute for good error messages. The error index page should be used to provide additional context and guidance on how to fix the error, but it should not be used to avoid writing good error messages in the first place.
