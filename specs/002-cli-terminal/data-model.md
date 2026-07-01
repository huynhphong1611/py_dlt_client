# Data Model: DLT TCP Terminal CLI

## CLI Invocation

Represents one terminal run of the DLT receiver command.

### Fields

- `host`: required target host string. Must be non-empty.
- `port`: TCP port integer. Defaults to 3490. Must be 1 through 65535.
- `timeout`: positive float seconds or `None` if explicitly supported later.
- `strict`: boolean. When true, parser errors terminate the process non-zero.
- `reconnect`: boolean. Enables automatic reconnect after connection loss.
- `reconnect_interval`: positive float seconds between reconnect attempts.
- `max_retries`: optional non-negative integer. `None` means no retry limit.
- `max_frame_size`: integer, default 65,535 bytes, minimum 4 bytes.
- `filters`: optional CLI Filter Criteria.

### Validation Rules

- `host` is mandatory and cannot be empty.
- `port` must be numeric and in range.
- `timeout`, `reconnect_interval`, and `max_frame_size` must satisfy existing
  `DltClient` validation.
- `max_retries` must be omitted or non-negative.
- `verbose_only` and `non_verbose_only` are mutually exclusive.

## CLI Filter Criteria

Maps terminal filter options to existing structured message filters.

### Fields

- `ecu`: optional set of ECU IDs.
- `apid`: optional set of APIDs.
- `ctid`: optional set of CTIDs.
- `level`: optional set of numeric levels or level names.
- `verbose_only`: boolean.
- `non_verbose_only`: boolean.

### Relationships

- Belongs to a CLI Invocation.
- Is translated into `DltFilter` or a compatible filter dictionary for
  `DltClient`.

## CLI Output Line

One stdout line derived from a delivered `DltMessage`.

### Fields

- `text`: the exact `DltMessage.text` string produced by the existing formatter.
- `newline`: exactly one line terminator emitted after each message.

### Validation Rules

- Verbose supported messages use readable text already produced by the library.
- Non-verbose and unsupported messages preserve payload-hex fallback text.
- Output line must not include connection diagnostics.

## CLI Diagnostic Event

One stderr event emitted by the terminal entry point.

### Fields

- `kind`: usage, connect, disconnect, reconnect, parser, or runtime.
- `message`: concise human-readable diagnostic.
- `attempt`: optional reconnect attempt count.

### Validation Rules

- Diagnostics must go to stderr.
- Default diagnostics must avoid Python tracebacks for expected user-facing
  failures.
- Strict parser failure must be reported before exit.

## CLI Exit Result

Final process outcome for one invocation.

### Fields

- `code`: process exit code.
- `reason`: normal completion, user interrupt, invalid arguments, connection
  failure, parser failure, retry exhaustion, or unexpected runtime failure.

### State Transitions

```text
parsed arguments
  -> connecting
  -> streaming
  -> user interrupt -> closed -> exit 0
  -> clean EOF without reconnect -> closed -> exit 0
  -> connection/parser failure without reconnect -> closed -> exit 1
  -> disconnect with reconnect -> reconnecting -> connecting
  -> retry exhaustion -> closed -> exit 1
  -> invalid arguments -> exit 2
```
