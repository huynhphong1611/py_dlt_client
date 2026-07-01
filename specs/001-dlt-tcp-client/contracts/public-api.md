# Public API Contract: py_dlt_client

## Package Boundary

The public package name is `py_dlt_client`. The stable first-version surface is:

- `DltClient`
- `DltMessage`
- `DltArgument`
- `DltHeader`
- `DltExtendedHeader`
- `DltFilter`
- `DltError`
- `DltConnectionError`
- `DltParserError`
- `DltUnsupportedTypeError`
- `DltFrameError`
- `format_message(message)`

Any module not exported from `py_dlt_client.__init__` is internal for the first
version.

## DltClient Construction

```python
DltClient(
    host: str,
    port: int = 3490,
    timeout: float | None = 5.0,
    auto_reconnect: bool = False,
    reconnect_interval: float = 3.0,
    max_retries: int | None = None,
    strict: bool = False,
    filters: DltFilter | dict | None = None,
    max_frame_size: int = 65535,
)
```

### Contract Rules

- `host` is required and must be non-empty.
- `port` must be a valid TCP port.
- `timeout`, when provided, must be positive.
- `reconnect_interval` must be positive.
- `max_retries=None` means retry indefinitely while `auto_reconnect=True`.
- `strict=False` continues past per-message parse errors when safe.
- Construction validates configuration without opening a socket.

## Message Consumption

### Iterator Flow

```python
client = DltClient(host="192.168.1.10")
for message in client.messages():
    ...
```

### Contract Rules

- `messages()` opens a connection if needed.
- Each yielded value is a `DltMessage`.
- Messages are yielded in stream order after filtering.
- Socket loss raises or triggers reconnect according to configuration.
- Exiting the iterator or calling `close()` releases socket resources.

## Callback Flow

```python
client = DltClient(host="192.168.1.10")
client.on_message(handle_message)
client.on_connect(handle_connect)
client.on_disconnect(handle_disconnect)
client.on_reconnect_attempt(handle_reconnect)
client.on_error(handle_error)
client.run_forever()
```

### Callback Signatures

- `on_message(callback: Callable[[DltMessage], None])`
- `on_connect(callback: Callable[[], None])`
- `on_disconnect(callback: Callable[[BaseException | None], None])`
- `on_reconnect_attempt(callback: Callable[[int], None])`
- `on_error(callback: Callable[[BaseException], None])`

### Contract Rules

- Callback registration returns the client to allow chaining.
- `run_forever()` blocks until `close()` is called, retry limit is exhausted, or
  strict mode raises a terminal error.
- Callback exceptions are reported through `on_error`; strict behavior for
  callback exceptions is documented before implementation.
- Message callbacks receive only messages that pass configured filters.

## Lifecycle Methods

- `connect() -> None`
- `close() -> None`
- `run_forever() -> None`
- `messages() -> Iterator[DltMessage]`

### Contract Rules

- `connect()` establishes one socket connection or raises `DltConnectionError`.
- `close()` is idempotent and closes the socket deterministically.
- No background thread or socket handle may remain after `close()` completes.

## Message Model Contract

`DltMessage` exposes:

- `ecu`
- `apid`
- `ctid`
- `session_id`
- `timestamp`
- `counter`
- `level`
- `level_name`
- `verbose`
- `message_id`
- `args`
- `text`
- `raw_payload`
- `raw_frame`
- `payload_hex`
- `errors`

### Contract Rules

- `text` is a readable formatter output, not proof that the original source log
  string was reconstructed.
- Non-verbose messages use payload-hex fallback.
- Unsupported verbose arguments are represented explicitly and preserve raw bytes
  or remaining payload bytes.

## Error Contract

Exception hierarchy:

```python
class DltError(Exception): ...
class DltConnectionError(DltError): ...
class DltParserError(DltError): ...
class DltUnsupportedTypeError(DltError): ...
class DltFrameError(DltParserError): ...
```

### Contract Rules

- Connection failures use `DltConnectionError`.
- Invalid frame size or truncated frame data uses `DltFrameError`.
- Unsupported verbose argument types use `DltUnsupportedTypeError` in strict mode
  and message error metadata in non-strict mode.
- Parser failures include enough context for logging and diagnosis without
  requiring applications to inspect raw sockets.

## Formatting Contract

`format_message(message: DltMessage) -> str`

### Contract Rules

- Supported verbose output format: `[ECU] [APID:CTID] LEVEL: arg1 arg2 arg3`.
- Raw bytes display as lowercase hex with `raw=<hex>`.
- Non-verbose fallback format includes `NON_VERBOSE` and `payload_hex=<hex>`.
- Unknown level names use `UNKNOWN` rather than inventing a level.

## Filtering Contract

Filters may be provided as `DltFilter` or an equivalent dictionary with keys:

- `ecu`
- `apid`
- `ctid`
- `level`
- `verbose_only`
- `non_verbose_only`

### Contract Rules

- Filters are applied after safe metadata parsing and before consumer delivery.
- String filters compare normalized DLT identifier text.
- Level filters accept documented level names and numeric levels.
- `verbose_only` and `non_verbose_only` are mutually exclusive.
