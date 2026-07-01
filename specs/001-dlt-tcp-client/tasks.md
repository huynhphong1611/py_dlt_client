---
description: "Task list for Pure Python DLT V1 TCP Client for Windows"
---

# Tasks: Pure Python DLT V1 TCP Client for Windows

**Input**: Design documents from `/specs/001-dlt-tcp-client/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Tests are REQUIRED by the constitution for protocol, transport, public API, and Windows cleanup behavior. Test tasks MUST appear before implementation tasks and MUST fail before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Python library**: `src/py_dlt_client/`
- **Unit tests**: `tests/unit/`
- **Local TCP integration tests**: `tests/integration/`
- **Windows lifecycle tests**: `tests/windows/`
- **Fixtures**: `tests/fixtures/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize the pure Python package, test layout, and project metadata.

- [X] T001 Create package and test directory structure in `src/py_dlt_client/`, `tests/fixtures/`, `tests/unit/`, `tests/integration/`, and `tests/windows/`
- [X] T002 Create project metadata with CPython 3.11+, standard-library runtime dependencies, and pytest test extra in `pyproject.toml`
- [X] T003 Configure pytest discovery and strict warnings in `pyproject.toml`
- [X] T004 [P] Add package marker and public export placeholder in `src/py_dlt_client/__init__.py`
- [X] T005 [P] Add typed package marker in `src/py_dlt_client/py.typed`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Define shared constants, models, errors, fixture builders, and test harnesses used by all user stories.

**CRITICAL**: No user story work can begin until this phase is complete.

- [X] T006 Define DLT constants, header flags, type-info masks, log level mapping, default port, and max frame size in `src/py_dlt_client/constants.py`
- [X] T007 [P] Define typed exception hierarchy and error context fields in `src/py_dlt_client/exceptions.py`
- [X] T008 [P] Define dataclasses for `DltHeader`, `DltExtendedHeader`, `DltArgument`, `DltMessage`, `DltFilter`, `DltClientConfig`, and `DltErrorInfo` in `src/py_dlt_client/models.py`
- [X] T009 [P] Create deterministic DLT V1 hex/binary fixture builders for standard, optional, extended, verbose, non-verbose, malformed, and truncated frames in `tests/fixtures/dlt_frames.py`
- [X] T010 [P] Create shared pytest fixtures for importing fixture builders and asserting message fields in `tests/conftest.py`
- [X] T011 [P] Create local controllable TCP server test harness for fragmented, coalesced, timeout, and disconnect scenarios in `tests/integration/tcp_harness.py`
- [X] T012 [P] Create Windows socket cleanup assertion helpers for repeated connect/close validation in `tests/windows/cleanup_helpers.py`
- [X] T013 Export foundational public models and exceptions from `src/py_dlt_client/__init__.py`

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Receive Structured DLT Messages (Priority: P1) MVP

**Goal**: Connect to a DLT TCP source, reconstruct binary DLT V1 frames, parse standard/optional/extended headers, and expose structured message objects with raw payload and raw frame preserved.

**Independent Test**: A controllable DLT TCP source sends complete, fragmented, and coalesced DLT V1 frames; the application receives exactly one structured object per frame with expected metadata, payload bytes, payload hex, and raw frame.

### Tests for User Story 1 (REQUIRED)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation.**

- [X] T014 [P] [US1] Add standard header parsing golden-frame tests in `tests/unit/test_headers_standard.py`
- [X] T015 [P] [US1] Add optional ECU/session/timestamp and extended header parsing tests in `tests/unit/test_headers_extended.py`
- [X] T016 [P] [US1] Add invalid length, truncated header, and oversized frame tests in `tests/unit/test_frame_errors.py`
- [X] T017 [P] [US1] Add frame reader tests for partial frames and multiple frames in one buffer in `tests/unit/test_frame_reader.py`
- [X] T018 [P] [US1] Add local TCP integration test for receiving structured DLT messages in stream order in `tests/integration/test_receive_structured.py`

### Implementation for User Story 1

- [X] T019 [US1] Implement DLT standard header parsing, optional field parsing, endianness detection, and length validation in `src/py_dlt_client/headers.py`
- [X] T020 [US1] Implement extended header parsing, verbose flag detection, APID/CTID decoding, and log level mapping in `src/py_dlt_client/headers.py`
- [X] T021 [US1] Implement binary frame buffering, minimum-header inspection, `read_exact`, partial-frame handling, multi-frame emission, and max-frame validation in `src/py_dlt_client/frame_reader.py`
- [X] T022 [US1] Implement raw message assembly for messages with and without extended headers in `src/py_dlt_client/models.py`
- [X] T023 [US1] Implement initial `DltClient.connect()`, `DltClient.close()`, and `DltClient.messages()` stream loop for structured message delivery in `src/py_dlt_client/client.py`
- [X] T024 [US1] Wire parser/frame reader errors to typed exceptions and non-strict message error metadata in `src/py_dlt_client/client.py`
- [X] T025 [US1] Export `DltClient` and parser-related public types from `src/py_dlt_client/__init__.py`
- [X] T026 [US1] Run and document passing US1 validation command `python -m pytest tests/unit/test_headers_standard.py tests/unit/test_headers_extended.py tests/unit/test_frame_errors.py tests/unit/test_frame_reader.py tests/integration/test_receive_structured.py` in `specs/001-dlt-tcp-client/quickstart.md`

**Checkpoint**: User Story 1 is independently functional and provides the MVP.

---

## Phase 4: User Story 2 - Read Human-Friendly Diagnostic Lines (Priority: P2)

**Goal**: Decode supported verbose DLT payload arguments and provide honest readable text while preserving raw/hex fallback for non-verbose and unsupported payloads.

**Independent Test**: Verbose frames with string, signed int, unsigned int, bool, float, and raw bytes produce decoded arguments and text; non-verbose and unsupported messages preserve payload hex and do not invent original log text.

### Tests for User Story 2 (REQUIRED)

- [X] T027 [P] [US2] Add verbose string decoding tests including null terminator and invalid UTF-8 fallback in `tests/unit/test_payload_string.py`
- [X] T028 [P] [US2] Add signed and unsigned integer decoding tests for int8/int16/int32/int64 and uint8/uint16/uint32/uint64 in `tests/unit/test_payload_int.py`
- [X] T029 [P] [US2] Add boolean and float32/float64 decoding tests with endianness coverage in `tests/unit/test_payload_bool_float.py`
- [X] T030 [P] [US2] Add raw bytes and unsupported argument preservation tests in `tests/unit/test_payload_raw_unsupported.py`
- [X] T031 [P] [US2] Add formatter tests for verbose, non-verbose, unknown level, and unsupported payload output in `tests/unit/test_formatter.py`
- [X] T032 [P] [US2] Add integration test for mixed verbose, non-verbose, and unsupported frames continuing in non-strict mode in `tests/integration/test_decode_and_format_stream.py`

### Implementation for User Story 2

- [X] T033 [US2] Implement verbose type-info parsing and argument-count handling in `src/py_dlt_client/payload_verbose.py`
- [X] T034 [US2] Implement string argument decoding with length handling, null stripping, UTF-8 decode, and documented fallback in `src/py_dlt_client/payload_verbose.py`
- [X] T035 [US2] Implement signed and unsigned integer argument decoding with message endianness in `src/py_dlt_client/payload_verbose.py`
- [X] T036 [US2] Implement boolean, float32, float64, and raw bytes argument decoding with message endianness in `src/py_dlt_client/payload_verbose.py`
- [X] T037 [US2] Implement unsupported verbose argument handling for strict and non-strict modes in `src/py_dlt_client/payload_verbose.py`
- [X] T038 [US2] Integrate verbose payload decoding and non-verbose payload preservation into message assembly in `src/py_dlt_client/client.py`
- [X] T039 [US2] Implement `format_message()` for verbose text, raw bytes display, non-verbose fallback, and unknown levels in `src/py_dlt_client/formatter.py`
- [X] T040 [US2] Set `DltMessage.text`, `DltMessage.args`, `DltMessage.payload_hex`, and unsupported error metadata consistently in `src/py_dlt_client/models.py`
- [X] T041 [US2] Export `format_message` and `DltArgument` from `src/py_dlt_client/__init__.py`
- [X] T042 [US2] Run and document passing US2 validation command `python -m pytest tests/unit/test_payload_string.py tests/unit/test_payload_int.py tests/unit/test_payload_bool_float.py tests/unit/test_payload_raw_unsupported.py tests/unit/test_formatter.py tests/integration/test_decode_and_format_stream.py` in `specs/001-dlt-tcp-client/quickstart.md`

**Checkpoint**: User Stories 1 and 2 work independently and together.

---

## Phase 5: User Story 3 - Integrate Safely Into Long-Running Apps (Priority: P3)

**Goal**: Provide callback API, iterator API lifecycle behavior, reconnect, filtering, strict/non-strict error handling, configurable logging, and Windows cleanup behavior for long-running applications.

**Independent Test**: Register lifecycle callbacks, force disconnect/reconnect, apply filters, exercise strict and non-strict errors, and verify sockets/background work are cleaned up after repeated sessions.

### Tests for User Story 3 (REQUIRED)

- [X] T043 [P] [US3] Add public API contract tests for constructor validation, exports, callback registration, and iterator behavior in `tests/unit/test_public_api.py`
- [X] T044 [P] [US3] Add filter tests for ECU, APID, CTID, level, verbose-only, and non-verbose-only delivery in `tests/unit/test_filters.py`
- [X] T045 [P] [US3] Add strict and non-strict error behavior tests for parser and unsupported-type failures in `tests/unit/test_error_modes.py`
- [X] T046 [P] [US3] Add reconnect timing, retry limit, disconnect, reconnect-attempt, and error callback integration tests in `tests/integration/test_reconnect_callbacks.py`
- [X] T047 [P] [US3] Add iterator consumption and close-on-exit integration tests in `tests/integration/test_iterator_lifecycle.py`
- [X] T048 [P] [US3] Add Windows repeated connect/read/close cleanup tests in `tests/windows/test_socket_cleanup.py`
- [X] T049 [P] [US3] Add logging tests proving core library uses `py_dlt_client` logger and no direct stdout/stderr output in `tests/unit/test_logging.py`

### Implementation for User Story 3

- [X] T050 [US3] Implement `DltFilter` normalization, validation, and message matching in `src/py_dlt_client/filters.py`
- [X] T051 [US3] Integrate filter application before callback and iterator delivery in `src/py_dlt_client/client.py`
- [X] T052 [US3] Implement callback registration methods `on_message`, `on_connect`, `on_disconnect`, `on_reconnect_attempt`, and `on_error` in `src/py_dlt_client/client.py`
- [X] T053 [US3] Implement `run_forever()` callback loop and callback exception routing in `src/py_dlt_client/client.py`
- [X] T054 [US3] Implement automatic reconnect with configurable interval, retry limit, disconnect events, reconnect-attempt events, and no busy loop in `src/py_dlt_client/client.py`
- [X] T055 [US3] Harden iterator lifecycle so generator exit and `close()` release socket resources deterministically in `src/py_dlt_client/client.py`
- [X] T056 [US3] Add package logger usage for parser, frame reader, and client diagnostics without direct `print()` calls in `src/py_dlt_client/client.py`
- [X] T057 [US3] Export `DltFilter` and callback-ready API surface from `src/py_dlt_client/__init__.py`
- [X] T058 [US3] Run and document passing US3 validation command `python -m pytest tests/unit/test_public_api.py tests/unit/test_filters.py tests/unit/test_error_modes.py tests/unit/test_logging.py tests/integration/test_reconnect_callbacks.py tests/integration/test_iterator_lifecycle.py tests/windows/test_socket_cleanup.py` in `specs/001-dlt-tcp-client/quickstart.md`

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Complete packaging, docs, reference comparison, and full validation across all stories.

- [X] T059 [P] Add README usage examples for iterator, callback, non-verbose fallback, and strict/non-strict behavior in `README.md`
- [X] T060 [P] Add API documentation notes for public exports, typed errors, and formatter semantics in `docs/api.md`
- [X] T061 [P] Add DLT scope documentation explaining supported DLT V1 payload types and out-of-scope DLT V2/FIBEX/ARXML behavior in `docs/dlt-scope.md`
- [X] T062 [P] Add reference comparison procedure for DLT Viewer or dlt-receive sample streams in `docs/reference-comparison.md`
- [X] T063 Run full unit and integration test suite and record command/results in `specs/001-dlt-tcp-client/quickstart.md`
- [X] T064 Run Windows validation suite and record command/results in `specs/001-dlt-tcp-client/quickstart.md`
- [X] T065 Audit `pyproject.toml` to confirm no native runtime dependencies and document result in `specs/001-dlt-tcp-client/quickstart.md`
- [X] T066 Review all public contract requirements against implementation and update any contract drift in `specs/001-dlt-tcp-client/contracts/public-api.md`
- [X] T067 Review parser contract requirements against implementation and update any contract drift in `specs/001-dlt-tcp-client/contracts/parser-contract.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion; blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational; delivers MVP structured receive.
- **User Story 2 (Phase 4)**: Depends on Foundational and is most useful after US1; remains testable with fixtures.
- **User Story 3 (Phase 5)**: Depends on Foundational and integrates US1/US2 behavior for application lifecycle.
- **Polish (Phase 6)**: Depends on all intended user stories being complete.

### User Story Dependencies

- **US1 - Receive Structured DLT Messages**: MVP, no dependency on other stories after foundation.
- **US2 - Read Human-Friendly Diagnostic Lines**: Uses message/header objects from foundation and US1 message assembly; can be developed with fixture-level parser tests after foundation.
- **US3 - Integrate Safely Into Long-Running Apps**: Uses message delivery from US1 and formatted/decoded messages from US2 for full validation.

### Within Each User Story

- Tests MUST be written and observed failing before implementation tasks.
- Fixture and harness changes precede story tests.
- Models/constants/errors precede parser/client implementation.
- Parser and formatter behavior precede public API lifecycle integration.
- Story checkpoint validation must pass before moving to the next priority unless explicitly working in parallel.

---

## Parallel Opportunities

- Setup tasks T004 and T005 can run in parallel after T001 starts.
- Foundational tasks T007 through T012 can run in parallel after T006 is defined.
- US1 tests T014 through T018 can run in parallel.
- US2 tests T027 through T032 can run in parallel.
- US3 tests T043 through T049 can run in parallel.
- Documentation polish tasks T059 through T062 can run in parallel.
- Different user stories can be developed in parallel after Phase 2 if teams coordinate shared files `src/py_dlt_client/client.py`, `src/py_dlt_client/models.py`, and `src/py_dlt_client/__init__.py`.

---

## Parallel Example: User Story 1

```bash
Task: "T014 [US1] Add standard header parsing golden-frame tests in tests/unit/test_headers_standard.py"
Task: "T015 [US1] Add optional ECU/session/timestamp and extended header parsing tests in tests/unit/test_headers_extended.py"
Task: "T016 [US1] Add invalid length, truncated header, and oversized frame tests in tests/unit/test_frame_errors.py"
Task: "T017 [US1] Add frame reader tests for partial frames and multiple frames in one buffer in tests/unit/test_frame_reader.py"
Task: "T018 [US1] Add local TCP integration test for receiving structured DLT messages in stream order in tests/integration/test_receive_structured.py"
```

## Parallel Example: User Story 2

```bash
Task: "T027 [US2] Add verbose string decoding tests including null terminator and invalid UTF-8 fallback in tests/unit/test_payload_string.py"
Task: "T028 [US2] Add signed and unsigned integer decoding tests for int8/int16/int32/int64 and uint8/uint16/uint32/uint64 in tests/unit/test_payload_int.py"
Task: "T029 [US2] Add boolean and float32/float64 decoding tests with endianness coverage in tests/unit/test_payload_bool_float.py"
Task: "T030 [US2] Add raw bytes and unsupported argument preservation tests in tests/unit/test_payload_raw_unsupported.py"
Task: "T031 [US2] Add formatter tests for verbose, non-verbose, unknown level, and unsupported payload output in tests/unit/test_formatter.py"
```

## Parallel Example: User Story 3

```bash
Task: "T043 [US3] Add public API contract tests for constructor validation, exports, callback registration, and iterator behavior in tests/unit/test_public_api.py"
Task: "T044 [US3] Add filter tests for ECU, APID, CTID, level, verbose-only, and non-verbose-only delivery in tests/unit/test_filters.py"
Task: "T045 [US3] Add strict and non-strict error behavior tests for parser and unsupported-type failures in tests/unit/test_error_modes.py"
Task: "T046 [US3] Add reconnect timing, retry limit, disconnect, reconnect-attempt, and error callback integration tests in tests/integration/test_reconnect_callbacks.py"
Task: "T048 [US3] Add Windows repeated connect/read/close cleanup tests in tests/windows/test_socket_cleanup.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Write and fail US1 tests T014-T018.
4. Complete US1 implementation T019-T025.
5. Run T026 validation and stop for review.

### Incremental Delivery

1. US1: structured DLT TCP receiving and raw metadata output.
2. US2: verbose payload decoding and honest formatter output.
3. US3: callback/iterator production lifecycle, reconnect, filtering, logging, and Windows cleanup.
4. Polish: docs, reference comparison, dependency audit, full validation.

### Test-First Rule

Each user story phase starts with tests that must fail before implementation. This
is required by the project constitution and supersedes the generic optional-test
guidance in the task generation template.

---

## Notes

- All tasks include exact file paths and use the required checkbox/ID/label format.
- `[P]` tasks operate on different files and can run in parallel.
- Story labels map to spec user stories: US1 structured receive, US2 readable diagnostic lines, US3 long-running app integration.
- Shared files that require coordination: `src/py_dlt_client/client.py`, `src/py_dlt_client/models.py`, and `src/py_dlt_client/__init__.py`.
