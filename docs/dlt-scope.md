# DLT Scope

## Supported In Version 1

- DLT V1 messages received directly from a TCP dlt-daemon stream.
- Standard header parsing.
- Optional ECU ID, session ID, and timestamp fields.
- Extended header parsing for APID, CTID, verbose flag, argument count, and level.
- Verbose payload arguments:
  - string
  - signed integer
  - unsigned integer
  - boolean
  - float32 and float64
  - raw bytes
- Non-verbose metadata and payload preservation.
- Strict and non-strict parse behavior.
- Reconnect, callback, iterator, filtering, and logging behavior.

## Out Of Scope For Version 1

- DLT V2.
- Full DLT Viewer replacement.
- dlt-daemon port or replacement.
- FIBEX/ARXML mapping.
- Full non-verbose decoding.
- Control messages.
- Injection messages.
- File transfer.
- Advanced network trace content.
- Arrays, structs, fixed point values, and variable info.
- GUI viewer.
- Standard `.dlt` file writing.

## Non-Verbose Output

Non-verbose messages are not converted into original log text. The client exposes
metadata, `message_id` when safely parseable, raw payload bytes, and payload hex.
