# Quickstart: DLT TCP Terminal CLI

## Prerequisites

- CPython 3.11 or newer.
- Package installed from the repository checkout.
- A reachable DLT TCP source such as `dlt-daemon` on port 3490, or the local TCP
  test harness used by the integration tests.

## Install for Local Validation

```bash
python -m pip install -e .[test]
```

## Basic Live Receive

```bash
py-dlt-client --host 192.168.1.10 --port 3490
```

Expected result:

- One stdout line per received DLT message.
- Supported verbose messages show readable text.
- Non-verbose or unsupported messages show payload-hex fallback text.
- Ctrl+C exits cleanly with status 0.

Equivalent source-checkout invocation:

```bash
python -m py_dlt_client --host 192.168.1.10 --port 3490
```

## Localhost Receive

`localhost` is valid when a DLT TCP source is listening on the same machine:

```bash
py-dlt-client --host localhost --port 3490
```

## Filtering

```bash
py-dlt-client --host 192.168.1.10 --apid SYS --ctid INIT
py-dlt-client --host 192.168.1.10 --level ERROR --level WARN
py-dlt-client --host 192.168.1.10 --verbose-only
py-dlt-client --host 192.168.1.10 --non-verbose-only
```

Expected result: only messages matching the selected structured DLT metadata are
printed to stdout.

## Reconnect

```bash
py-dlt-client --host 192.168.1.10 --reconnect --reconnect-interval 3
```

Expected result:

- Socket loss is reported on stderr.
- Reconnect attempts are reported on stderr.
- Matching messages continue printing after the connection returns.

## Strict Parser Mode

```bash
py-dlt-client --host 192.168.1.10 --strict
```

Expected result: a parser/frame error is reported on stderr and the command exits
with status 1.

## Validation Commands

Run all tests:

```bash
python -m pytest
```

Run only CLI-focused tests after implementation:

```bash
python -m pytest tests/unit/test_cli_args.py tests/integration/test_cli_stream.py tests/windows/test_cli_process_cleanup.py
```

## Expected CLI Test Coverage

- Console script and `python -m py_dlt_client` invocation.
- Required `--host`, default `--port`, and invalid argument handling.
- stdout contains only message lines.
- stderr contains connection, reconnect, and parser diagnostics.
- Supported verbose fixture output matches the existing formatter.
- Non-verbose fixture output preserves payload-hex fallback.
- Filters print only matching ECU/APID/CTID/level/verbose-mode messages.
- Ctrl+C closes the socket and exits with status 0.
- Connection failure without reconnect exits with status 1.

## Validation Notes

- Focused CLI validation command:

  ```bash
  python -m pytest tests/unit/test_cli_args.py tests/unit/test_cli_errors.py tests/unit/test_cli_filters.py tests/integration/test_cli_stream.py tests/integration/test_cli_diagnostics.py tests/integration/test_cli_reconnect.py tests/integration/test_cli_filter_stream.py tests/windows/test_cli_process_cleanup.py
  ```

- The focused CLI suite passed in the current Linux validation environment.
- Full repository validation passed with `python -m pytest` in the current Linux
  validation environment.
- Windows process behavior is covered by a platform-neutral cleanup test that
  verifies KeyboardInterrupt closes the client and exits successfully; a manual
  Windows terminal smoke test is still recommended before release packaging.
