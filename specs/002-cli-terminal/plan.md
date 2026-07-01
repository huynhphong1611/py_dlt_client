# Implementation Plan: DLT TCP Terminal CLI

**Branch**: `002-cli-terminal` | **Date**: 2026-07-02 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-cli-terminal/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add a cross-platform terminal entry point for the existing `py_dlt_client`
package so users can receive live DLT V1 TCP messages with `--host` and optional
`--port` without writing Python code. The implementation will reuse the existing
`DltClient`, parser, formatter, filters, reconnect behavior, and typed errors;
the CLI layer only owns argument parsing, stdout message printing, stderr
diagnostics, exit codes, and process shutdown.

## Technical Context

**Language/Version**: CPython 3.11+ on Windows and Linux, matching the current
`pyproject.toml` package requirement.

**Primary Dependencies**: Python standard library only at runtime. Use
`argparse`, `sys`, `signal` where portable, and the existing `py_dlt_client`
package. No native or third-party runtime dependencies.

**Storage**: N/A for runtime. CLI receives live TCP streams only and does not
read `.dlt` storage files. Tests may reuse in-repo binary DLT fixtures.

**Testing**: `pytest` with existing golden DLT frame fixtures, local TCP
integration harness, subprocess-based CLI invocation tests, invalid argument
tests, stdout/stderr separation tests, reconnect/disconnect tests, and
Windows-relevant cleanup tests.

**Target Platform**: Windows 10/11 and Linux terminals on CPython 3.11+.

**Project Type**: Pure Python library with an explicit CLI wrapper entry point.

**Performance Goals**: Add negligible per-message overhead beyond existing
parsing and formatting; print one line per delivered message without buffering
the entire stream. First output line should appear within 5 seconds against a
local reachable TCP source.

**Constraints**: Pure Python runtime, no native extensions, no POSIX-only APIs,
no `.dlt` file input in this feature, default port 3490, default timeout from the
library, default maximum frame size 65,535 bytes, clean socket close on Ctrl+C or
normal exit, stdout only for message lines and stderr only for diagnostics.

**Scale/Scope**: Live DLT V1 TCP streams supported by the existing parser:
standard headers, optional fields, extended headers, supported verbose argument
types, non-verbose payload hex fallback, unsupported payload fallback, APID/CTID
/ECU/level/verbose filters, and reconnect options. DLT V2, FIBEX/ARXML mapping,
control messages, injection, file transfer, GUI viewing, and `.dlt` file reading
remain out of scope.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Pure Python / Windows-first**: PASS. CLI uses CPython 3.11 standard library
  modules and existing package code only; no native or POSIX-only dependency is
  planned.
- **DLT V1 fidelity**: PASS. CLI does not reinterpret protocol bytes; it delegates
  DLT V1 frame parsing, verbose decoding, fallback handling, and typed parser
  errors to the existing library.
- **TCP reliability**: PASS. CLI exposes timeout, reconnect, retry, and clean
  shutdown behavior through existing `DltClient` ownership of the socket.
- **Test-first evidence**: PASS. Tasks must add failing-first CLI tests for
  golden verbose/non-verbose frames, malformed input, local TCP streaming,
  connection failure, reconnect, Ctrl+C cleanup, and Windows-compatible
  subprocess behavior before implementation.
- **API and diagnostics**: PASS. Public Python API remains minimal. CLI is the
  explicit stdout/stderr boundary; library code continues to use configurable
  logging rather than direct terminal writes.

## Project Structure

### Documentation (this feature)

```text
specs/002-cli-terminal/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── cli.md
└── tasks.md              # Generated later by /speckit-tasks
```

### Source Code (repository root)

```text
src/
└── py_dlt_client/
    ├── __init__.py
    ├── __main__.py       # New: enables python -m py_dlt_client
    ├── cli.py            # New: argument parsing and process behavior
    ├── client.py         # Existing DltClient transport and iterator
    ├── filters.py        # Existing filter normalization and matching
    ├── formatter.py      # Existing text formatter
    └── ...

tests/
├── fixtures/
├── unit/
│   └── test_cli_args.py          # New
├── integration/
│   ├── test_cli_stream.py        # New
│   └── tcp_harness.py            # Existing local TCP harness
└── windows/
    └── test_cli_process_cleanup.py  # New or extended cleanup coverage
```

**Structure Decision**: Keep the CLI inside `src/py_dlt_client` rather than a
separate package so it can reuse internal package APIs without introducing a new
distribution boundary. Add a `py-dlt-client` console script in `pyproject.toml`
and a `__main__.py` module so both installed command usage and
`python -m py_dlt_client` usage are validated.

## Phase 0 Research Summary

See [research.md](./research.md). All technical unknowns are resolved with
standard-library choices and reuse of current client behavior.

## Phase 1 Design Summary

See [data-model.md](./data-model.md), [contracts/cli.md](./contracts/cli.md), and
[quickstart.md](./quickstart.md). The agent-context update step was checked but
skipped because this repository does not contain an agent context update script.

## Post-Design Constitution Check

- **Pure Python / Windows-first**: PASS. Design uses `argparse`, subprocess-safe
  process behavior, and existing socket client abstractions.
- **DLT V1 fidelity**: PASS. Contract states message lines are `DltMessage.text`
  outputs from the existing formatter and preserves payload-hex fallback.
- **TCP reliability**: PASS. Data model and contract cover connect, reconnect,
  disconnect, retry exhaustion, Ctrl+C, and deterministic close behavior.
- **Test-first evidence**: PASS. Quickstart and future tasks require subprocess
  CLI tests, local TCP fixture streams, malformed frames, reconnect behavior, and
  Windows cleanup validation before implementation.
- **API and diagnostics**: PASS. CLI is the only new public terminal interface;
  stdout/stderr behavior and exit codes are documented.

## Complexity Tracking

No constitution violations.

## Dependency Audit

No runtime dependencies or native packages were added for the CLI feature. The
implementation uses the Python standard library and the existing pure Python
`py_dlt_client` package only.
