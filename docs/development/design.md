# Design Notes

## Reason for existence

This library was created since I noticed that I was solving the same problem in multiple tools that I was writing, and it made sense to extract the common logic into a library. It also would be useful to help other tooling authors to improve how their errors are presented.

## "Guiding" ideas

Diagnostic's design follows a few of the key ideas, based on what I've discovered/come up with over the course of working on improving error handling across multiple command line tools.

- When presented with an error, the user will want to fix the root cause of the error. Give them the information they need to do that.
- Presenting a giant wall of text is not helpful. Present the information in a way that is easy to scan.
- Make "shortcuts" an intentional and visible decision.

The [recommendations page](../recommendations.md) covers most of the "why" for these choices.
