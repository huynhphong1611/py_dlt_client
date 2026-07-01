# Data Model: Pure Python DLT V1 TCP Client for Windows

## DltMessage

Represents one received DLT frame after safe parsing.

### Fields

- `ecu: str | None` - ECU ID from optional standard header when present.
- `apid: str | None` - Application ID from extended header when present.
- `ctid: str | None` - Context ID from extended header when present.
- `session_id: int | None` - Session ID from optional standard header.
- `timestamp: int | None` - Raw DLT timestamp from optional standard header.
- `counter: int` - Message counter from standard header.
- `level: int | None` - Numeric log level when available.
- `level_name: str | None` - Human-readable level name when available.
- `verbose: bool` - Whether the message is verbose.
- `message_id: int | None` - Non-verbose message ID if safely parseable.
- `args: list[DltArgument]` - Decoded or preserved verbose arguments.
- `text: str` - Default formatted representation.
- `raw_payload: bytes` - Payload after parsed headers.
- `raw_frame: bytes` - Complete DLT frame bytes.
- `payload_hex: str` - Hex representation of `raw_payload`.
- `errors: list[DltErrorInfo]` - Non-fatal parse or unsupported-type notes in
  non-strict mode.

### Validation Rules

- `raw_frame` length equals `header.length`.
- `payload_hex` is lowercase hex of `raw_payload`.
- `verbose=False` messages do not claim full decoded text.
- `args` contains only decoded or explicitly unsupported argument objects.

### Relationships

- Contains one `DltHeader`.
- Contains zero or one `DltExtendedHeader`.
- Contains zero or more `DltArgument` values.

## DltArgument

Represents one verbose payload argument.

### Fields

- `type_name: str` - One of `string`, `signed_int`, `unsigned_int`, `bool`,
  `float`, `raw`, or `unsupported`.
- `value: object | None` - Decoded value when supported.
- `raw: bytes` - Raw bytes consumed or preserved for the argument.
- `type_info: int` - Original DLT type information word.
- `supported: bool` - Whether `value` is fully decoded.
- `display: str` - Formatter-ready representation.

### Validation Rules

- Supported arguments have a non-`None` `value` except zero-length raw bytes.
- Unsupported arguments retain raw bytes or remaining payload bytes.
- Numeric and float values are decoded according to message endianness.

## DltHeader

Represents the DLT standard header and optional standard fields.

### Fields

- `htyp: int` - Header type byte.
- `mcnt: int` - Message counter.
- `length: int` - Total DLT message length from the wire frame.
- `big_endian: bool` - Message byte order.
- `has_extended_header: bool`
- `has_ecu_id: bool`
- `has_session_id: bool`
- `has_timestamp: bool`
- `ecu: str | None`
- `session_id: int | None`
- `timestamp: int | None`
- `header_size: int` - Parsed byte count for standard plus optional header data.

### Validation Rules

- `length` is at least the parsed header size.
- Optional fields are present only when their header flags are set.
- ECU ID is decoded from exactly four bytes with trailing null/space cleanup.

## DltExtendedHeader

Represents metadata present when the standard header declares an extended header.

### Fields

- `msin: int` - Message info byte.
- `noar: int` - Number of payload arguments declared.
- `apid: str` - Four-byte application ID.
- `ctid: str` - Four-byte context ID.
- `verbose: bool` - Verbose flag derived from message info.
- `level: int | None` - Numeric log level when available.
- `level_name: str | None` - Log level name when available.

### Validation Rules

- APID and CTID are decoded from exactly four bytes each.
- `noar` controls verbose argument parsing count.
- Missing extended header data yields a frame/parser error.

## DltClientConfig

Defines connection, parsing, filtering, and reconnect behavior.

### Fields

- `host: str` - Required target host.
- `port: int` - Target port, default 3490.
- `timeout: float | None` - Connect/read timeout.
- `auto_reconnect: bool` - Whether to reconnect after socket loss.
- `reconnect_interval: float` - Delay between reconnect attempts.
- `max_retries: int | None` - Optional retry limit.
- `strict: bool` - Whether parse errors are raised or reported and skipped.
- `max_frame_size: int` - Maximum accepted frame length, default 65,535.
- `filters: DltFilter | None` - Optional delivery filters.

### Validation Rules

- `host` is non-empty.
- `port` is between 1 and 65,535.
- `timeout`, when set, is positive.
- `reconnect_interval` is positive.
- `max_retries`, when set, is zero or greater.
- `max_frame_size` is at least the minimum DLT standard header size.

## DltFilter

Defines message delivery filters.

### Fields

- `ecu: set[str] | None`
- `apid: set[str] | None`
- `ctid: set[str] | None`
- `level: set[str | int] | None`
- `verbose_only: bool`
- `non_verbose_only: bool`

### Validation Rules

- `verbose_only` and `non_verbose_only` cannot both be true.
- Empty sets behave as no matches and should be rejected or normalized to `None`
  during configuration.

## ClientSession

Represents runtime lifecycle state for one `DltClient`.

### States

- `created` - Configured but not connected.
- `connecting` - Attempting socket connection.
- `connected` - Socket is open and messages may be read.
- `reconnecting` - Connection failed or closed and retry policy is active.
- `closing` - User requested close or loop shutdown.
- `closed` - Socket is closed and no background work remains.
- `failed` - Terminal error in strict mode or retry limit exhausted.

### State Transitions

- `created -> connecting -> connected`
- `connected -> reconnecting -> connecting` when automatic reconnect is enabled.
- `connected -> closing -> closed` on user shutdown.
- `connecting -> failed` when connection fails and reconnect is disabled.
- `reconnecting -> failed` when retry limit is exhausted.

## ClientEvent

Represents an event delivered to application callbacks.

### Event Types

- `message` - Carries `DltMessage`.
- `connect` - Carries endpoint information.
- `disconnect` - Carries optional error.
- `reconnect_attempt` - Carries attempt count and delay.
- `error` - Carries typed error.

### Validation Rules

- Message events carry a parsed `DltMessage`.
- Error-bearing events carry a typed `DltError`.
- Reconnect attempt counts start at 1 for the first retry after disconnect.

## DltErrorInfo

Represents non-fatal parse details preserved on messages in non-strict mode.

### Fields

- `category: str` - `connection`, `parser`, `unsupported_type`, or `frame`.
- `message: str` - Human-readable diagnostic.
- `offset: int | None` - Byte offset within frame or payload when known.
- `raw: bytes | None` - Relevant raw bytes when useful.

### Validation Rules

- `category` is one of the documented error categories.
- `raw` must not duplicate the entire frame unless the whole frame is invalid.
