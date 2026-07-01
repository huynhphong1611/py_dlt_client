# Feature Specification: DLT TCP Terminal CLI

**Feature Branch**: `002-cli-terminal`

**Created**: 2026-07-02

**Status**: Draft

**Input**: User description: "Dựa vào code hiện tại hãy build CLI để có thể dùng terminal trên Windows hay Linux, truyền --host và --port là có thể show raw log."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Stream Logs From Terminal (Priority: P1)

A diagnostic user needs to run one terminal command on Windows or Linux, provide a
DLT TCP host and port, and immediately see incoming DLT log lines printed in the
terminal without writing a Python script.

**Why this priority**: This is the primary value of the feature. The existing
library already receives and formats DLT TCP messages; users now need a direct
terminal workflow.

**Independent Test**: Start a controllable DLT TCP source that emits supported
verbose and non-verbose DLT V1 frames, run the CLI with host and port arguments,
and verify one output line appears per received message.

**Acceptance Scenarios**:

1. **Given** a reachable DLT TCP endpoint emitting verbose DLT V1 messages,
   **When** the user runs the CLI with `--host` and `--port`, **Then** the terminal
   prints readable log lines for received messages.
2. **Given** the endpoint emits non-verbose or unsupported messages, **When** the
   CLI receives them, **Then** the terminal prints the existing fallback text with
   payload hex rather than claiming a fully decoded original log string.
3. **Given** the user presses Ctrl+C, **When** the CLI is running, **Then** the
   command exits cleanly and releases the TCP connection.

---

### User Story 2 - Diagnose Connection Problems (Priority: P2)

A diagnostic user needs clear terminal feedback when host, port, connection, or
stream errors occur, so failures are understandable without inspecting Python
tracebacks by default.

**Why this priority**: A CLI is commonly used during debugging. Clear connection
and parser feedback prevents confusion when the target is offline, the port is
wrong, or the DLT stream contains malformed data.

**Independent Test**: Run the CLI against an unused local port and against a test
source that closes the connection. Verify the command reports the problem on
stderr and exits with a non-zero status unless reconnect is enabled.

**Acceptance Scenarios**:

1. **Given** the target host or port is unreachable, **When** the user runs the
   CLI, **Then** the terminal shows a concise connection error and exits non-zero.
2. **Given** stream parsing encounters a bad message in non-strict mode, **When**
   later valid messages arrive, **Then** the CLI continues printing valid messages
   and reports the parse problem through diagnostic output.
3. **Given** strict mode is enabled, **When** parsing fails, **Then** the CLI exits
   non-zero after reporting the parser error.

---

### User Story 3 - Narrow Terminal Output (Priority: P3)

A diagnostic user needs to limit terminal output by DLT metadata such as APID,
CTID, ECU ID, log level, or verbose mode so high-volume streams can be inspected
without changing application code.

**Why this priority**: Filtering is not required for a minimal receive command,
but it makes the CLI useful against real noisy DLT streams.

**Independent Test**: Run the CLI against a mixed stream with APID, CTID, level,
verbose, and non-verbose samples. Verify only matching lines are printed for each
filter option.

**Acceptance Scenarios**:

1. **Given** a stream containing multiple APIDs and CTIDs, **When** the user
   supplies APID or CTID filters, **Then** only matching messages are printed.
2. **Given** a stream containing several log levels, **When** the user supplies
   level filters, **Then** only matching levels are printed.
3. **Given** a stream containing verbose and non-verbose messages, **When** the
   user chooses verbose-only or non-verbose-only output, **Then** only that message
   class is printed.

---

### Edge Cases

- Host is omitted or empty.
- Port is omitted, non-numeric, below 1, or above 65535.
- The target host is unreachable.
- The target closes the socket while the CLI is running.
- Ctrl+C occurs while blocked waiting for network data.
- The stream contains malformed, truncated, or unsupported DLT V1 messages.
- The stream contains non-verbose messages that cannot be converted to original
  log text.
- Terminal output is piped to another command or redirected to a file.
- Filters match no messages.
- Reconnect is enabled and the target repeatedly disconnects.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a terminal command for receiving DLT V1 TCP logs
  using the existing DLT client library behavior.
- **FR-002**: CLI MUST accept `--host` as a required target host argument.
- **FR-003**: CLI MUST accept `--port` as an optional TCP port argument and default
  to 3490 when omitted.
- **FR-004**: CLI MUST print one terminal output line for each delivered DLT
  message using the library's existing message text semantics.
- **FR-005**: CLI MUST preserve honest fallback output for non-verbose or
  unsupported messages, including payload hex when full text is not available.
- **FR-006**: CLI MUST write normal message output to stdout.
- **FR-007**: CLI MUST write connection, parse, reconnect, and usage diagnostics
  to stderr.
- **FR-008**: CLI MUST exit with status 0 when stopped intentionally by the user.
- **FR-009**: CLI MUST exit with a non-zero status for invalid arguments,
  connection failure without reconnect, or strict parser failure.
- **FR-010**: CLI MUST support a strict mode option that exits on parser errors.
- **FR-011**: CLI MUST support automatic reconnect options for users who want the
  command to keep trying after socket loss.
- **FR-012**: CLI MUST support filtering by ECU ID, APID, CTID, log level,
  verbose-only, and non-verbose-only criteria.
- **FR-013**: CLI MUST cleanly close the TCP connection on Ctrl+C or normal exit.
- **FR-014**: CLI MUST be usable on both Windows and Linux terminals after package
  installation.
- **FR-015**: CLI MUST NOT read `.dlt` storage files in this feature; input remains
  a live DLT TCP stream.

### Protocol and Platform Requirements *(mandatory)*

- **PR-001**: CLI scope is DLT V1 messages received directly from a TCP
  dlt-daemon-compatible stream.
- **PR-002**: CLI output follows the existing structured-message formatter:
  readable text for supported verbose messages and payload-hex fallback for
  non-verbose or unsupported messages.
- **PR-003**: CLI MUST rely on the existing pure Python runtime package and MUST
  NOT introduce native runtime dependencies.
- **PR-004**: CLI validation MUST include local TCP integration tests using
  supported verbose, non-verbose, malformed, and disconnect scenarios.
- **PR-005**: CLI validation MUST include Windows-compatible process invocation
  behavior, argument parsing, stdout/stderr separation, and Ctrl+C cleanup.

### Key Entities *(include if feature involves data)*

- **CLI Invocation**: The user command, arguments, filters, reconnect options, and
  strict/non-strict behavior selected for one terminal run.
- **CLI Output Line**: One stdout line derived from a delivered DLT message's text.
- **CLI Diagnostic Event**: A stderr message for connection status, reconnect
  attempts, parse errors, or usage errors.
- **CLI Exit Result**: The final process status and reason for termination.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can run the CLI with host and port against a local test DLT
  TCP source and see the first received log line within 5 seconds.
- **SC-002**: 100% of approved verbose CLI fixture messages produce the same text
  line as the library formatter.
- **SC-003**: 100% of approved non-verbose CLI fixture messages print payload-hex
  fallback and do not claim full original log text.
- **SC-004**: Invalid argument cases exit non-zero and produce a concise stderr
  message in all approved validation cases.
- **SC-005**: Ctrl+C or intentional stop closes the TCP connection and exits with
  status 0 in approved validation cases.
- **SC-006**: Filter validation cases print only matching messages for ECU, APID,
  CTID, level, verbose-only, and non-verbose-only options.
- **SC-007**: The command is invokable after installation on both Windows and Linux
  validation environments.

## Assumptions

- "Raw log" for this CLI means terminal lines produced from received DLT messages:
  readable verbose text where supported, and payload-hex fallback where not.
- The user wants live TCP receive behavior, not `.dlt` storage file reading.
- The CLI can reuse the existing DLT TCP client, formatter, filters, strict mode,
  and reconnect behavior.
- The default port remains 3490.
- The first CLI version can block in the foreground until the user stops it,
  connection fails, or retry limits are exhausted.
