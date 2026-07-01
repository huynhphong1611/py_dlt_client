# API Notes

## Public Exports

The first-version public surface is exported from `py_dlt_client`:

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
- `format_message`

Modules not exported from `py_dlt_client.__init__` are internal.

## Error Semantics

- `DltConnectionError` covers connection setup and socket lifecycle failures.
- `DltFrameError` covers invalid lengths, truncation, and oversized frames.
- `DltParserError` covers malformed supported payload/header data.
- `DltUnsupportedTypeError` is raised in strict mode for unsupported verbose
  argument types.

In non-strict mode, per-message parse issues are reported through message error
metadata where safe and later valid messages continue to be delivered.

## Formatter Semantics

`format_message(message)` returns a readable representation, not proof that the
original source log string was reconstructed.

- Verbose supported messages use `[ECU] [APID:CTID] LEVEL: arg1 arg2`.
- Raw bytes display as `raw=<hex>`.
- Non-verbose messages use `NON_VERBOSE: payload_hex=<hex>`.
- Unknown levels display as `UNKNOWN`.
