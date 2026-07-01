# Parser Contract: DLT V1 TCP Frames

## Input Contract

The parser receives complete DLT frame bytes from the frame reader. The frame
reader receives arbitrary chunks from a TCP socket and is responsible for
reconstructing complete frames.

## Frame Reader Rules

- Read binary bytes only; never decode socket data as text.
- Maintain an internal buffer for partial frames.
- Inspect the DLT standard header length field once enough bytes are buffered.
- Emit exactly one frame per declared DLT message length.
- Emit multiple frames when the buffer contains multiple complete messages.
- Reject a frame length smaller than the minimum header size.
- Reject a frame length greater than `max_frame_size`.
- On socket close during a partial frame, report a frame error with buffered byte
  context.

## Header Parsing Rules

- Parse standard header fields: header type, message counter, total length,
  endianness, optional field flags, and extended-header flag.
- Parse optional ECU ID, session ID, and timestamp only when declared by header
  flags.
- Parse extended header only when declared by the standard header.
- Expose messages without extended headers as raw messages rather than failing
  solely because metadata is absent.

## Payload Parsing Rules

- For verbose messages, parse up to the declared argument count.
- Supported argument groups: string, signed integer, unsigned integer, boolean,
  float32, float64, and raw bytes.
- Numeric and floating point values respect message endianness.
- Strings are length-delimited, strip one trailing null terminator when present,
  and use documented fallback behavior for invalid UTF-8.
- Unsupported argument types preserve raw bytes or remaining payload bytes.
- Non-verbose payloads are not decoded into original text without external
  descriptions.

## Strict Mode Behavior

- Invalid frame length raises `DltFrameError`.
- Truncated declared header fields raise `DltFrameError`.
- Unsupported verbose argument type raises `DltUnsupportedTypeError`.
- Other malformed payload data raises `DltParserError`.

## Non-Strict Mode Behavior

- Invalid frame length is reported through error handling and skipped when safe.
- Truncated frame data is reported and does not produce a normal message.
- Unsupported verbose argument data is preserved on the message as unsupported
  argument/error metadata when enough context exists.
- Later valid frames in the stream continue to be delivered after a single
  malformed or unsupported message where resynchronization is safe.

## Logging Rules

- Parser and frame reader use the `py_dlt_client` logger.
- Debug logs may include frame lengths, offsets, and error categories.
- Logs must not include direct `print()` output from core library code.
