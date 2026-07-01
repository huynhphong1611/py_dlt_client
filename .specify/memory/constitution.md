<!--
Sync Impact Report
Version change: template -> 1.0.0
Modified principles:
- Template principle 1 -> I. Pure Python, Windows-First Library
- Template principle 2 -> II. DLT V1 Protocol Fidelity
- Template principle 3 -> III. TCP Transport Reliability
- Template principle 4 -> IV. Deterministic Test-First Validation
- Template principle 5 -> V. Minimal API, Typed Errors, and Observable Diagnostics
Added sections:
- Runtime and Compatibility Constraints
- Delivery Workflow and Quality Gates
Removed sections:
- None
Templates requiring updates:
- updated: .specify/templates/plan-template.md
- updated: .specify/templates/spec-template.md
- updated: .specify/templates/tasks-template.md
- not applicable: .specify/templates/commands/ does not exist
Follow-up TODOs:
- None
-->
# Pure Python DLT V1 TCP Client for Windows Constitution

## Core Principles

### I. Pure Python, Windows-First Library

The project MUST remain a pure Python client library for Windows. Runtime code MUST
avoid native extensions, compiled helper binaries, POSIX-only APIs, and platform
assumptions that fail on supported Windows versions. New runtime dependencies MUST
be pure Python, small in scope, and justified in the implementation plan.

Rationale: the client must be installable and debuggable in constrained Windows
diagnostic environments without compiler toolchains or native package friction.

### II. DLT V1 Protocol Fidelity

All parsing, encoding, filtering, and stream behavior MUST follow the DLT V1 wire
format required by the feature specification and project contracts. Unknown,
malformed, truncated, or unsupported DLT messages MUST produce deterministic typed
errors or explicit unsupported-message results instead of silent data loss.

Rationale: diagnostic log clients are only useful when byte-level interpretation is
predictable and failures preserve enough context for investigation.

### III. TCP Transport Reliability

The TCP client MUST handle connection setup, read timeouts, reconnect decisions,
partial reads, clean shutdown, and socket ownership explicitly. Public APIs MUST
make blocking behavior and timeout defaults visible. Implementations MUST close
sockets deterministically and MUST NOT leave background threads or handles running
after client shutdown.

Rationale: Windows users need a client that behaves consistently on unreliable
network links and releases resources cleanly during repeated diagnostic sessions.

### IV. Deterministic Test-First Validation

Every protocol, transport, and public API change MUST begin with tests that fail
before implementation. Required coverage includes golden DLT frames, malformed and
truncated input, TCP integration tests using a local controllable server, timeout
paths, and Windows-relevant resource cleanup. Generated tasks MUST include these
tests; omitting them is a constitution violation unless the plan documents a
temporary, approved exception.

Rationale: parser and socket regressions are hard to diagnose manually and must be
caught with repeatable evidence.

### V. Minimal API, Typed Errors, and Observable Diagnostics

Public APIs MUST expose a small, stable surface for connecting, receiving,
decoding, and closing. Errors MUST be typed and documented. Diagnostic logging MUST
use Python logging, MUST be opt-in or configurable, and MUST NOT write directly to
stdout or stderr from library code except through an explicit CLI entry point.

Rationale: downstream tools need a dependable library contract while developers
still need enough observability to debug protocol and network failures.

## Runtime and Compatibility Constraints

The implementation MUST target a supported CPython 3 version on Windows and MUST
declare the chosen minimum version in each implementation plan. The standard
library is the default for sockets, binary parsing, threading, logging, and typing.
Any third-party runtime dependency MUST be justified against the pure-Python and
minimal-scope requirements.

Feature plans MUST document:

- Supported Windows versions and Python versions.
- DLT V1 message forms in scope and explicitly out of scope.
- Timeout, reconnect, buffering, and maximum message-size behavior.
- Public API compatibility impact.
- Test strategy for protocol fixtures, local TCP integration, and Windows cleanup.

## Delivery Workflow and Quality Gates

Specifications MUST describe user-visible diagnostic workflows, independent test
scenarios, protocol edge cases, and measurable outcomes. Plans MUST pass the
constitution check before design work proceeds and MUST be re-checked after design.
Tasks MUST be grouped by independently testable user story and MUST place required
tests before implementation tasks.

No implementation is complete until:

- Golden-frame, malformed-frame, TCP integration, and timeout tests pass.
- Public API and typed errors are documented in the feature quickstart or contracts.
- Windows-specific behavior has been verified by CI, local Windows execution, or a
  documented manual validation step.
- Any approved constitution exception is recorded in the plan's complexity table
  with a simpler alternative and a removal path.

## Governance

This constitution supersedes conflicting project templates, plans, and informal
practices. Amendments MUST be proposed with the affected principles, migration
impact, and required template updates. Maintainers MUST review constitution
compliance during specification, planning, task generation, and code review.

Versioning follows semantic versioning:

- MAJOR for removing or redefining principles in a way that permits previously
  prohibited behavior.
- MINOR for adding principles, sections, or materially expanded mandatory guidance.
- PATCH for wording clarifications that do not change compliance obligations.

Every amendment MUST update the Sync Impact Report, dependent templates, version,
and Last Amended date in the same change.

**Version**: 1.0.0 | **Ratified**: 2026-07-01 | **Last Amended**: 2026-07-01
