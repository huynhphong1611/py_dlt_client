# CLI Contract: DLT TCP Terminal CLI

## Commands

The package exposes two equivalent terminal entry points:

```text
py-dlt-client [OPTIONS]
python -m py_dlt_client [OPTIONS]
```

Both commands receive live DLT V1 messages from a TCP endpoint. They do not read
`.dlt` storage files.

## Required Options

```text
--host HOST
```

- Required.
- Non-empty hostname or IP address.
- Examples: `localhost`, `127.0.0.1`, `192.168.1.10`.

## Connection Options

```text
--port PORT
```

- Optional.
- Default: `3490`.
- Integer range: `1..65535`.

```text
--timeout SECONDS
```

- Optional.
- Default: existing library timeout.
- Positive float.

```text
--reconnect
```

- Optional flag.
- Enables automatic reconnect after connection loss.
- Default: disabled.

```text
--reconnect-interval SECONDS
```

- Optional.
- Default: existing library reconnect interval.
- Positive float.

```text
--max-retries COUNT
```

- Optional.
- Non-negative integer.
- Omitted means unlimited retries when reconnect is enabled.

```text
--max-frame-size BYTES
```

- Optional.
- Default: existing library maximum frame size.
- Minimum: 4.

## Parser Options

```text
--strict
```

- Optional flag.
- Exits non-zero on parser/frame errors.
- Default non-strict mode attempts to continue where the existing client can
  continue and reports diagnostics on stderr.

## Filter Options

```text
--ecu ECU
--apid APID
--ctid CTID
--level LEVEL
```

- Optional.
- May be supplied multiple times.
- Values map to the existing structured filter fields.

```text
--verbose-only
--non-verbose-only
```

- Optional mutually exclusive flags.
- `--verbose-only` prints only verbose DLT messages.
- `--non-verbose-only` prints only non-verbose DLT messages.

## Output Contract

### stdout

Each delivered DLT message produces exactly one stdout line:

```text
{DltMessage.text}
```

Examples:

```text
[ECU1] [SYS:INIT] INFO: System init started
[ECU1] [TEL:CRSH] NON_VERBOSE: payload_hex=0000000c01ff90aa
```

### stderr

Connection, disconnect, reconnect, parser, and usage diagnostics are written to
stderr. Expected user-facing failures should be concise and should not show a
Python traceback by default.

Examples:

```text
connect error: [Errno 111] Connection refused
reconnect attempt 2
parser error: invalid DLT frame length
```

## Exit Codes

```text
0  intentional user stop, clean shutdown, or clean stream completion
1  runtime connection, parser, retry exhaustion, or unexpected CLI failure
2  invalid command-line arguments from argparse
```

## Compatibility Rules

- Must work from Windows and Linux terminals.
- Must not require native dependencies.
- Must close the TCP connection on Ctrl+C, normal completion, and handled error
  exit.
- Must preserve the existing library formatter semantics.
