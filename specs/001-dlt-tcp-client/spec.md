# Feature Specification: Pure Python DLT V1 TCP Client for Windows

**Feature Branch**: `001-dlt-tcp-client`

**Created**: 2026-07-01

**Status**: Draft

**Input**: User description: "Pure Python DLT V1 TCP receiver/parser for Windows that connects to dlt-daemon over TCP, reads binary DLT V1 frames, exposes structured message objects, formats readable text for supported verbose messages, preserves raw payloads for non-verbose or unsupported messages, and supports reconnect, callbacks, iterator usage, filtering, logging, and strict/non-strict error handling."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Receive Structured DLT Messages (Priority: P1)

A Windows Python application developer needs to connect to an ECU or AAOS target
running dlt-daemon and receive realtime DLT V1 messages as structured objects so
the application can inspect ECU, application, context, level, payload, and raw
frame data without shelling out to Linux-only tooling.

**Why this priority**: This is the core value of the feature. Without reliable
binary stream reception and structured message output, readable formatting,
callbacks, reconnect, and filtering have no useful data source.

**Independent Test**: Start a controllable DLT TCP source on the default DLT port
or a test port, send valid DLT V1 frames with standard, optional, and extended
headers, and verify each received object contains the expected metadata,
payload bytes, payload hex, and raw frame.

**Acceptance Scenarios**:

1. **Given** a reachable DLT TCP endpoint emitting one complete DLT V1 frame,
   **When** the application receives messages, **Then** it gets one structured
   message object with parsed header metadata and raw payload preserved.
2. **Given** a TCP receive operation returns a partial frame followed by the
   remaining bytes later, **When** the application receives messages, **Then** it
   gets exactly one complete message object and no partial-message output.
3. **Given** one TCP receive operation contains multiple complete DLT V1 frames,
   **When** the application receives messages, **Then** it gets one structured
   message object per frame in stream order.

---

### User Story 2 - Read Human-Friendly Diagnostic Lines (Priority: P2)

A diagnostic engineer needs supported verbose DLT messages to be shown as readable
text lines while still seeing honest fallback output for non-verbose messages or
unsupported verbose argument types.

**Why this priority**: Readable output is the main usability improvement over raw
binary data, but it must not misrepresent non-verbose messages that require
external descriptions.

**Independent Test**: Send verbose DLT V1 frames containing supported string,
signed integer, unsigned integer, boolean, floating point, and raw-byte arguments,
then send non-verbose and partially unsupported messages. Verify formatted text
for supported values and payload-hex fallback for messages that cannot be fully
decoded.

**Acceptance Scenarios**:

1. **Given** a verbose DLT V1 message with supported argument types, **When** it is
   exposed to the application, **Then** the message includes decoded arguments and
   a readable text line in the form `[ECU] [APID:CTID] LEVEL: arg1 arg2`.
2. **Given** a non-verbose DLT V1 message, **When** it is exposed to the
   application, **Then** the message is marked non-verbose and its text uses a
   payload-hex fallback rather than inventing an original log string.
3. **Given** a verbose DLT V1 message with an unsupported argument type, **When**
   it is exposed in non-strict mode, **Then** supported arguments remain decoded,
   unsupported data is preserved as raw bytes or hex, and the stream continues.

---

### User Story 3 - Integrate Safely Into Long-Running Apps (Priority: P3)

A Python application developer needs realtime callbacks, an iterator-style message
flow, reconnect behavior, filtering, and application-controlled error handling so
the client can run inside a larger Windows diagnostic application.

**Why this priority**: Production applications need lifecycle events and recovery
behavior after the parser works, but these capabilities depend on the message
receiver and formatter being stable.

**Independent Test**: Register message, connect, disconnect, reconnect-attempt,
and error handlers; force a socket disconnect; verify the application receives the
expected events, reconnect attempts respect configured limits and delay, selected
filters are applied, and strict/non-strict parse errors behave as configured.

**Acceptance Scenarios**:

1. **Given** callbacks are registered and a connection succeeds, **When** messages
   arrive, disconnect occurs, and reconnect begins, **Then** the corresponding
   callbacks are invoked with useful event data in the expected order.
2. **Given** automatic reconnect is enabled with a retry interval, **When** the TCP
   connection drops, **Then** reconnect attempts occur after the configured delay
   without a busy loop and without crashing the host application.
3. **Given** filters for ECU, APID, CTID, level, or verbose mode, **When** messages
   arrive, **Then** only matching messages are delivered to application message
   consumers while nonmatching messages are skipped.

---

### Edge Cases

- TCP data arrives fragmented across multiple receive operations.
- One receive operation contains multiple DLT messages.
- A frame length is smaller than the minimum header size or exceeds the configured
  maximum message size.
- A message declares optional ECU ID, session ID, timestamp, or extended header
  fields but the frame ends before those fields are complete.
- A message has no extended header and must still be exposed as a raw DLT message.
- A message is non-verbose and therefore cannot be converted into the original log
  text without external mapping data.
- A verbose payload contains invalid string bytes, a null terminator, or a length
  that reaches the end of the payload.
- A verbose payload contains an unsupported argument type after one or more
  supported arguments.
- A connect, read, reconnect, or shutdown operation times out.
- The remote endpoint closes the socket during frame reception.
- Repeated connect, receive, and close cycles occur in one Windows process.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST let an application connect to a DLT TCP endpoint by
  providing a host and optional port, with port 3490 as the default.
- **FR-002**: System MUST treat incoming data as a binary DLT stream and MUST NOT
  decode raw socket data as plain text or process it line by line.
- **FR-003**: System MUST buffer stream data until complete DLT frames are
  available, including support for fragmented frames and multiple frames in one
  receive operation.
- **FR-004**: System MUST parse the DLT V1 standard header fields needed to
  determine header type, message counter, total message length, endianness,
  optional-field presence, and extended-header presence.
- **FR-005**: System MUST validate message length before exposing a message and
  MUST surface invalid lengths as parser errors or skip them according to the
  configured error mode.
- **FR-006**: System MUST parse optional ECU ID, session ID, and timestamp fields
  when the header declares them.
- **FR-007**: System MUST parse the extended header when present, including message
  info, argument count, application ID, context ID, verbose flag, and log level.
- **FR-008**: System MUST expose messages without an extended header as raw
  messages with whatever metadata and payload bytes can be parsed safely.
- **FR-009**: System MUST distinguish verbose and non-verbose messages and include
  a `verbose` indicator in each message object.
- **FR-010**: System MUST decode verbose payload arguments for strings, signed
  integers, unsigned integers, booleans, floating point numbers, and raw bytes.
- **FR-011**: System MUST respect the message endianness when decoding supported
  numeric and floating point argument values.
- **FR-012**: System MUST decode string arguments by length, remove a trailing null
  terminator when present, and preserve readable output when bytes are not valid
  UTF-8 by using a documented fallback.
- **FR-013**: System MUST preserve unsupported verbose argument data as raw bytes
  or hex and MUST NOT stop the entire stream in non-strict mode.
- **FR-014**: System MUST expose each received message as a structured object with
  ECU, APID, CTID, session ID, timestamp, counter, level, level name, verbose flag,
  decoded arguments, text, raw payload, raw frame, and payload hex when available.
- **FR-015**: System MUST provide a default text representation for supported
  verbose messages in the form `[ECU] [APID:CTID] LEVEL: arg1 arg2 arg3`.
- **FR-016**: System MUST format non-verbose messages and undecodable payloads with
  payload-hex fallback and MUST NOT claim full text decoding without external
  message descriptions.
- **FR-017**: System MUST allow applications to register handlers for message,
  connect, disconnect, reconnect-attempt, and error events.
- **FR-018**: System MUST allow applications to consume messages through an
  iterator-style flow as an alternative to callbacks.
- **FR-019**: System MUST support automatic reconnect when enabled, with
  configurable retry delay and optional maximum retry count.
- **FR-020**: System MUST avoid tight retry loops when reconnecting.
- **FR-021**: System MUST support strict and non-strict parse modes: strict mode
  surfaces parse errors to the caller, and non-strict mode continues the stream
  where safe while reporting the error.
- **FR-022**: System MUST provide typed error categories for connection failures,
  parser failures, unsupported payload types, and invalid frames.
- **FR-023**: System MUST use application-configurable diagnostic logging and MUST
  NOT print directly from the core library.
- **FR-024**: System MUST support filtering by ECU ID, APID, CTID, log level,
  verbose-only, and non-verbose-only criteria before delivering messages to
  application consumers.
- **FR-025**: System MUST keep file-based DLT storage, control messages, injection
  messages, GUI viewing, DLT V2, FIBEX/ARXML mapping, and full non-verbose
  decoding out of the first-version scope.

### Protocol and Platform Requirements *(mandatory)*

- **PR-001**: Specification scope is DLT V1 messages received directly from a TCP
  dlt-daemon stream, not `.dlt` storage files and not plain text logs.
- **PR-002**: Supported first-version message forms are DLT V1 messages with
  standard headers, optional ECU/session/timestamp fields, optional extended
  headers, verbose messages with supported argument types, and non-verbose
  messages exposed with metadata and raw payload.
- **PR-003**: Unsupported first-version message forms include DLT V2, control
  messages, injection messages, file transfer, advanced network trace content,
  arrays, structs, fixed point values, variable info, full non-verbose decoding,
  and any FIBEX/ARXML-based interpretation.
- **PR-004**: The feature MUST be usable by Python applications running natively on
  supported Windows systems and MUST NOT require Linux-only tooling at runtime.
- **PR-005**: Runtime dependencies MUST remain pure Python and necessary for the
  client use case; the first version assumes no external runtime dependency is
  required unless planning proves otherwise.
- **PR-006**: Timeout behavior, reconnect behavior, maximum frame size, and invalid
  frame behavior MUST be documented before implementation begins.
- **PR-007**: Protocol validation MUST include known-good DLT V1 frames, malformed
  frames, truncated frames, non-verbose frames, and frames containing unsupported
  verbose argument types.

### Key Entities *(include if feature involves data)*

- **DLT Message**: A decoded or partially decoded diagnostic record containing ECU,
  APID, CTID, session ID, timestamp, message counter, level, verbose flag, decoded
  arguments, formatted text, raw payload, raw frame, and payload hex.
- **DLT Argument**: One verbose payload argument with a type name, decoded value
  when supported, original raw bytes, type information, and a supported/unsupported
  indicator.
- **DLT Header**: The parsed standard header and optional standard fields that
  determine frame length, counter, endianness, optional field presence, ECU ID,
  session ID, and timestamp.
- **DLT Extended Header**: The parsed message info, argument count, APID, CTID,
  verbose flag, log level, and log level name when the extended header is present.
- **Client Session**: A connection lifecycle record covering endpoint settings,
  timeout, reconnect policy, current connection state, and event delivery.
- **Client Event**: A notification delivered to the host application for message
  arrival, connection, disconnection, reconnect attempt, or error.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A Windows diagnostic application can connect to a reachable DLT TCP
  endpoint on port 3490 or a configured port and begin receiving messages within
  5 seconds under normal network conditions.
- **SC-002**: 100% of approved DLT V1 golden sample frames produce message objects
  with expected header metadata, raw payload, raw frame, and payload hex.
- **SC-003**: 100% of approved verbose payload samples for string, signed integer,
  unsigned integer, boolean, floating point, and raw bytes produce expected
  argument values and readable text.
- **SC-004**: 100% of approved non-verbose samples are marked non-verbose and use
  payload-hex fallback without claiming full original log text.
- **SC-005**: Fragmented TCP input and multi-message TCP input are reconstructed
  into the correct number of messages in stream order for all approved stream
  fixture cases.
- **SC-006**: In non-strict mode, malformed or unsupported single-message samples
  do not stop later valid messages from being delivered in the same stream.
- **SC-007**: When a connection is interrupted with automatic reconnect enabled,
  the host application receives disconnect and reconnect-attempt events, and retry
  attempts follow the configured delay within a 10% timing tolerance.
- **SC-008**: Output for an agreed sample stream can be compared against an
  established DLT viewer or receiver, and all supported fields match the reference
  interpretation.

## Assumptions

- The target log source is an ECU, AAOS, or Linux system already running
  dlt-daemon and exposing DLT messages over TCP, commonly on port 3490.
- The first version is a client/receiver only and does not replace dlt-daemon or
  send control, injection, or configuration messages to the daemon.
- The host application is trusted to provide a reachable host address and to
  configure its own application logging.
- Readable text is guaranteed only for verbose DLT messages whose argument types
  are supported by this first version.
- Non-verbose messages are useful in the first version through metadata, raw
  payload, payload hex, and message ID if safely parseable.
- Windows compatibility means native execution in a Windows Python application
  without requiring Linux command-line tools at runtime.
