# Tasks: DLT TCP Terminal CLI

**Input**: Design documents from `/specs/002-cli-terminal/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/cli.md](./contracts/cli.md), [quickstart.md](./quickstart.md)

**Tests**: Tests are REQUIRED by the constitution for protocol, transport, public API, and Windows cleanup behavior. Test tasks MUST appear before implementation tasks and MUST fail before implementation.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files or has no dependency on incomplete tasks
- **[Story]**: User story label for story phases only
- Every task includes an exact file path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare CLI module, module execution entry point, and subprocess test helpers.

- [X] T001 [P] Create empty CLI module scaffold with `main(argv: list[str] | None = None) -> int` in `src/py_dlt_client/cli.py`
- [X] T002 [P] Create module execution scaffold that calls `py_dlt_client.cli.main` in `src/py_dlt_client/__main__.py`
- [X] T003 [P] Create subprocess CLI runner helper for module invocation and stdout/stderr capture in `tests/integration/cli_runner.py`
- [X] T004 [P] Add CLI subprocess timeout constants and command builders for Windows/Linux-safe tests in `tests/integration/cli_runner.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Define shared CLI contract hooks before user-story work starts.

**CRITICAL**: No user story implementation should begin until this phase is complete.

- [X] T005 Add `py-dlt-client = "py_dlt_client.cli:main"` console script metadata in `pyproject.toml`
- [X] T006 Define CLI exit code constants for success, runtime error, and argparse usage behavior in `src/py_dlt_client/cli.py`
- [X] T007 Define reusable argument type validators for port, positive float, non-negative int, and frame size in `src/py_dlt_client/cli.py`

**Checkpoint**: CLI entry surfaces and shared validation hooks are ready for story implementation.

---

## Phase 3: User Story 1 - Stream Logs From Terminal (Priority: P1) MVP

**Goal**: A user runs the CLI with `--host` and optional `--port` and sees one stdout line per received DLT message.

**Independent Test**: Start the local TCP harness with supported verbose and non-verbose DLT V1 frames, run `python -m py_dlt_client --host 127.0.0.1 --port <port>`, and verify stdout contains the same message text as the existing formatter with no diagnostics mixed into stdout.

### Tests for User Story 1 (REQUIRED)

- [X] T008 [P] [US1] Add unit tests for required `--host`, default `--port 3490`, explicit `--port`, and `--help` behavior in `tests/unit/test_cli_args.py`
- [X] T009 [P] [US1] Add integration test for `python -m py_dlt_client --host 127.0.0.1 --port <port>` printing verbose and non-verbose fixture lines in `tests/integration/test_cli_stream.py`
- [X] T010 [P] [US1] Add Windows-compatible process cleanup test for Ctrl+C/user interrupt exiting 0 and closing the socket in `tests/windows/test_cli_process_cleanup.py`

### Implementation for User Story 1

- [X] T011 [US1] Implement `argparse` parser for `--host`, `--port`, `--timeout`, and `--max-frame-size` in `src/py_dlt_client/cli.py`
- [X] T012 [US1] Implement `DltClient` construction from parsed basic connection arguments in `src/py_dlt_client/cli.py`
- [X] T013 [US1] Implement streaming loop that prints each `DltMessage.text` line to stdout and flushes line output in `src/py_dlt_client/cli.py`
- [X] T014 [US1] Wire `python -m py_dlt_client` to return the CLI exit code via `SystemExit(main())` in `src/py_dlt_client/__main__.py`
- [X] T015 [US1] Verify console script invocation metadata resolves to `py_dlt_client.cli:main` in `pyproject.toml`

**Checkpoint**: MVP CLI can stream DLT TCP logs from terminal with `--host` and `--port`.

---

## Phase 4: User Story 2 - Diagnose Connection Problems (Priority: P2)

**Goal**: Users get concise stderr diagnostics and predictable exit codes for connection, disconnect, parser, strict-mode, and reconnect scenarios.

**Independent Test**: Run the CLI against an unused local port, a stream that closes, and malformed frames; verify stderr contains concise diagnostics, stdout remains message-only, and exit codes match the contract.

### Tests for User Story 2 (REQUIRED)

- [X] T016 [P] [US2] Add unit tests for invalid argument exit behavior, strict flag parsing, and no-traceback expected errors in `tests/unit/test_cli_errors.py`
- [X] T017 [P] [US2] Add integration tests for connection refused, disconnect without reconnect, malformed frame in strict mode, and stderr/stdout separation in `tests/integration/test_cli_diagnostics.py`
- [X] T018 [P] [US2] Add integration tests for `--reconnect`, `--reconnect-interval`, and `--max-retries` diagnostics using the local TCP harness in `tests/integration/test_cli_reconnect.py`

### Implementation for User Story 2

- [X] T019 [US2] Implement stderr diagnostic callbacks for connect, disconnect, reconnect attempt, and parser/runtime errors in `src/py_dlt_client/cli.py`
- [X] T020 [US2] Implement runtime exception handling that maps expected connection/parser failures to exit code 1 without default tracebacks in `src/py_dlt_client/cli.py`
- [X] T021 [US2] Implement `--strict`, `--reconnect`, `--reconnect-interval`, and `--max-retries` argument mapping to `DltClient` in `src/py_dlt_client/cli.py`
- [X] T022 [US2] Ensure CLI calls `client.close()` in a `finally` block for normal exit, handled errors, and KeyboardInterrupt in `src/py_dlt_client/cli.py`

**Checkpoint**: CLI failure modes are diagnosable and shell-friendly.

---

## Phase 5: User Story 3 - Narrow Terminal Output (Priority: P3)

**Goal**: Users can filter terminal output by ECU, APID, CTID, log level, verbose-only, and non-verbose-only options.

**Independent Test**: Run the CLI against a mixed local stream and verify each filter prints only matching message lines while preserving stderr diagnostics separately.

### Tests for User Story 3 (REQUIRED)

- [X] T023 [P] [US3] Add unit tests for repeated `--ecu`, `--apid`, `--ctid`, `--level`, `--verbose-only`, and `--non-verbose-only` parsing in `tests/unit/test_cli_filters.py`
- [X] T024 [P] [US3] Add unit test for mutually exclusive verbose mode filter validation in `tests/unit/test_cli_filters.py`
- [X] T025 [P] [US3] Add integration tests for ECU/APID/CTID/level/verbose/non-verbose filtering against mixed DLT fixture frames in `tests/integration/test_cli_filter_stream.py`

### Implementation for User Story 3

- [X] T026 [US3] Implement repeated filter arguments and verbose-mode mutually exclusive group in the `argparse` parser in `src/py_dlt_client/cli.py`
- [X] T027 [US3] Map parsed filter arguments into the existing `DltClient(filters=...)` dictionary shape in `src/py_dlt_client/cli.py`
- [X] T028 [US3] Preserve message-only stdout behavior when filters match no messages or only stderr diagnostics occur in `src/py_dlt_client/cli.py`

**Checkpoint**: CLI can reduce high-volume DLT streams using structured filters.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, validation, and compatibility checks across all stories.

- [X] T029 [P] Update README CLI usage examples for `py-dlt-client --host localhost --port 3490`, filtering, strict mode, and reconnect in `README.md`
- [X] T030 [P] Update CLI quickstart validation notes after implementation in `specs/002-cli-terminal/quickstart.md`
- [X] T031 Run focused CLI test suite and record any manual Windows caveats in `specs/002-cli-terminal/quickstart.md`
- [X] T032 Run full `pytest` suite covering existing parser/client behavior plus new CLI tests using `tests/`
- [X] T033 Confirm `pyproject.toml` still has no runtime dependencies and document that no native packages were added in `specs/002-cli-terminal/plan.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational and is the MVP.
- **User Story 2 (Phase 4)**: Depends on Foundational; can be developed after or alongside US1 but validates best once US1 streaming exists.
- **User Story 3 (Phase 5)**: Depends on Foundational; can be developed after US1 because it extends the same CLI invocation path.
- **Polish (Phase 6)**: Depends on all selected user stories.

### User Story Dependencies

- **US1 (P1)**: No dependency on other stories after Foundational. Delivers terminal streaming MVP.
- **US2 (P2)**: Uses the same CLI entry point as US1 but remains independently testable with failure sources and unused ports.
- **US3 (P3)**: Uses existing library filtering and can be validated independently against mixed fixture streams.

### Within Each User Story

- Write tests first and confirm they fail before implementation.
- Implement argument parsing before client construction.
- Implement client construction before streaming/error behavior.
- Complete story-specific tests before moving to the next priority story.

---

## Parallel Opportunities

- Setup tasks T001, T002, T003, and T004 can run in parallel.
- US1 tests T008, T009, and T010 can be authored in parallel.
- US2 tests T016, T017, and T018 can be authored in parallel.
- US3 tests T023, T024, and T025 can be authored in parallel.
- Documentation tasks T029 and T030 can run in parallel after implementation.

## Parallel Example: User Story 1

```bash
# Test authoring can be split across files:
Task: "T008 Add unit tests in tests/unit/test_cli_args.py"
Task: "T009 Add integration tests in tests/integration/test_cli_stream.py"
Task: "T010 Add cleanup tests in tests/windows/test_cli_process_cleanup.py"
```

## Parallel Example: User Story 2

```bash
# Failure-mode tests can be split across files:
Task: "T016 Add unit tests in tests/unit/test_cli_errors.py"
Task: "T017 Add diagnostics tests in tests/integration/test_cli_diagnostics.py"
Task: "T018 Add reconnect tests in tests/integration/test_cli_reconnect.py"
```

## Parallel Example: User Story 3

```bash
# Filter parser and stream tests can be split across files:
Task: "T023 Add filter parser tests in tests/unit/test_cli_filters.py"
Task: "T025 Add filter integration tests in tests/integration/test_cli_filters.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete US1 tests T008 through T010 and confirm they fail.
3. Complete US1 implementation T011 through T015.
4. Validate `python -m py_dlt_client --host 127.0.0.1 --port <port>` against the local TCP harness.

### Incremental Delivery

1. Deliver US1 to make the CLI useful for live terminal streaming.
2. Add US2 for robust diagnostics, strict mode, reconnect, and cleanup.
3. Add US3 for structured filtering on noisy DLT streams.
4. Finish documentation and full regression validation.

### Notes

- The CLI remains a thin wrapper over existing `DltClient`, parser, formatter, and filters.
- Do not add `.dlt` file reading tasks for this feature.
- Do not add runtime dependencies unless the plan is amended and constitution impact is recorded.
