# Research: DLT TCP Terminal CLI

## Decision: Use `argparse` for CLI parsing

**Rationale**: `argparse` is in the Python standard library, works on Windows and
Linux, produces conventional usage errors with exit status 2, and avoids any
third-party runtime dependency.

**Alternatives considered**:

- Click/Typer: nicer ergonomics but adds a dependency not justified for a small
  diagnostic command.
- Manual `sys.argv` parsing: dependency-free but more error-prone and less
  consistent for help and validation.

## Decision: Provide both `py-dlt-client` and `python -m py_dlt_client`

**Rationale**: A console script is the normal installed terminal workflow, while
`python -m py_dlt_client` is useful from a source checkout and on systems where
script directories are not on `PATH`.

**Alternatives considered**:

- Console script only: simpler but less convenient during development and local
  validation.
- Module execution only: avoids packaging metadata changes but is less discoverable
  after installation.

## Decision: Reuse `DltClient.messages()` for streaming

**Rationale**: The existing iterator already owns connection setup, frame reads,
parsing, filtering, reconnect decisions, and socket cleanup. Reusing it keeps the
CLI thin and prevents a second transport implementation.

**Alternatives considered**:

- Callback API: works, but iterator flow maps more directly to line-by-line
  terminal output and exit handling.
- Direct socket reads in CLI: rejected because it would duplicate tested client
  behavior and risk protocol drift.

## Decision: Print messages to stdout and diagnostics to stderr

**Rationale**: This preserves shell composability. Users can pipe or redirect log
lines without mixing connection status and parser diagnostics into the data stream.

**Alternatives considered**:

- All output to stdout: simpler but breaks piping and automated processing.
- Python logging for CLI diagnostics only: configurable but less predictable for a
  first terminal tool; library logging remains unchanged.

## Decision: Use simple documented exit codes

**Rationale**: Return 0 for intentional user stop or clean completion, 1 for
runtime connection/parser failures, and `argparse`'s conventional 2 for invalid
arguments. This is portable and sufficient for shell automation.

**Alternatives considered**:

- Many specialized exit codes: more precise but unnecessary for initial CLI scope.
- Return 130 for Ctrl+C: common in shells, but the spec requires intentional user
  stop to exit with status 0.

## Decision: Keep reconnect opt-in by default

**Rationale**: Existing `DltClient` defaults to no auto-reconnect. For a terminal
command, a failed one-shot connection should produce a visible non-zero result
unless the user explicitly asks to keep trying.

**Alternatives considered**:

- Reconnect by default: useful on unstable links but can make invalid host/port
  mistakes appear to hang.

## Decision: Map CLI filters directly to existing `DltFilter`

**Rationale**: Existing filter behavior already supports ECU, APID, CTID, level,
verbose-only, and non-verbose-only. Direct mapping avoids divergent semantics.

**Alternatives considered**:

- Post-format text filtering: easy to implement but loses structured DLT metadata
  semantics.
- New CLI-only filter implementation: duplicates existing tested behavior.

## Decision: Validate through subprocess CLI tests plus local TCP harness

**Rationale**: The CLI behavior includes process exit codes, stdout/stderr
separation, Ctrl+C handling, and packaging entry points, which cannot be fully
validated through function-level tests alone.

**Alternatives considered**:

- Unit tests only: insufficient for terminal and process behavior.
- Manual validation only: violates deterministic test-first requirements.
