# Implementation Plan: Pure Python DLT V1 TCP Client for Windows

**Branch**: `001-dlt-tcp-client` | **Date**: 2026-07-01 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-dlt-tcp-client/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Build `py_dlt_client`, a pure Python Windows-native DLT V1 TCP receiver/parser.
The client connects to a dlt-daemon TCP endpoint, reconstructs binary DLT frames
from the stream, parses standard/optional/extended headers, decodes supported
verbose payload arguments, exposes structured message objects, formats readable
text when possible, preserves raw payload data otherwise, and supports callbacks,
iterator consumption, filtering, strict/non-strict errors, and reconnect behavior.

The technical approach is a standard-library runtime package with explicit
separation between stream framing, protocol parsing, formatting, filtering, and
client lifecycle. Tests are fixture-first: golden frames, malformed/truncated
frames, local TCP integration, reconnect timing, and Windows cleanup evidence are
created before implementation tasks.

## Technical Context

**Language/Version**: CPython 3.11+ on Windows 10/11; code must remain compatible with
currently supported CPython 3 minor versions where practical.

**Primary Dependencies**: Python standard library only at runtime. Development and
test tooling may use pure-Python packages such as pytest if introduced in project
metadata.

**Storage**: No runtime storage. Test fixtures are stored as binary/hex DLT frame
samples under `tests/fixtures/`.

**Testing**: pytest-based unit and integration tests with golden DLT V1 frames,
malformed/truncated frames, a local controllable TCP server, timeout/reconnect
tests, and Windows cleanup checks.

**Target Platform**: Windows 10/11 native Python applications receiving DLT V1 TCP
streams from ECU, AAOS, or Linux targets running dlt-daemon. Development may occur
cross-platform, but Windows validation is required before completion.

**Project Type**: Pure Python library with an optional thin CLI/example entry point
only if needed for validation. Public package/import name: `py_dlt_client`.

**Performance Goals**: Correctly reconstruct fragmented and coalesced TCP input in
stream order; begin receiving from a reachable endpoint within 5 seconds under
normal network conditions; avoid unbounded buffer growth with a documented maximum
frame size.

**Constraints**: Pure Python runtime, no native extensions, no POSIX-only APIs, no
direct `print()` from core library, configurable timeout/reconnect behavior,
strict/non-strict parse modes, and default maximum DLT frame size of 65,535 bytes
based on the 16-bit DLT message length field.

**Scale/Scope**: One TCP client session per `DltClient` instance; supports DLT V1
standard header, optional ECU/session/timestamp fields, extended header metadata,
verbose payload arguments for string, signed integer, unsigned integer, boolean,
float32/float64, and raw bytes; non-verbose messages expose metadata and raw
payload without FIBEX/ARXML interpretation.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Pure Python / Windows-first**: PASS. Runtime uses CPython standard library
  socket, struct, dataclasses, logging, threading/queue as needed, and typing.
  No native extensions or POSIX-only APIs are planned.
- **DLT V1 fidelity**: PASS. Scope explicitly covers DLT V1 TCP messages with
  standard, optional, and extended headers; unsupported DLT V2, control,
  injection, file transfer, FIBEX/ARXML, and full non-verbose decoding remain out
  of scope. Golden and malformed frame fixtures are required.
- **TCP reliability**: PASS. Plan defines binary stream buffering, partial and
  multiple-frame handling, configurable connect/read timeouts, reconnect delay,
  retry limits, strict close behavior, and socket ownership by the client session.
- **Test-first evidence**: PASS. Required tests include golden frames,
  malformed/truncated frames, local TCP integration, timeout/reconnect paths, and
  Windows cleanup/repeated-session validation.
- **API and diagnostics**: PASS. Public API is limited to client lifecycle,
  iterator/callback consumption, message/result models, filters, formatter, and
  typed errors. Diagnostics use configurable Python logging only.

Post-design re-check: PASS. `research.md`, `data-model.md`, `contracts/`, and
`quickstart.md` preserve all gates and introduce no constitution violations.

## Project Structure

### Documentation (this feature)

```text
specs/001-dlt-tcp-client/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── public-api.md
│   └── parser-contract.md
└── tasks.md             # Created by /speckit-tasks, not by this command
```

### Source Code (repository root)

```text
pyproject.toml
src/
└── py_dlt_client/
    ├── __init__.py
    ├── client.py
    ├── frame_reader.py
    ├── headers.py
    ├── payload_verbose.py
    ├── formatter.py
    ├── filters.py
    ├── models.py
    ├── constants.py
    ├── exceptions.py
    └── py.typed

tests/
├── fixtures/
├── unit/
├── integration/
└── windows/
```

**Structure Decision**: Use a single `src/py_dlt_client` library package to match
the requested project name and import examples. Keep modules flat for the first
version so parser, transport, models, and formatter boundaries are explicit
without adding package nesting before complexity exists. Keep tests separated by
fixture, unit, local TCP integration, and Windows cleanup concerns.

## Complexity Tracking

No constitution violations are planned.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
