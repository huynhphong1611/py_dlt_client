# Quickstart: Validate Pure Python DLT V1 TCP Client for Windows

## Prerequisites

- Windows 10 or Windows 11 for final validation.
- CPython 3.11 or newer.
- A checkout of this repository.
- Optional: access to an ECU, AAOS, or Linux target running dlt-daemon on TCP port
  3490 for reference validation.

## Setup

From the repository root:

```bash
python -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -e ".[test]"
```

On non-Windows development machines, use the platform's virtual environment
activation path, but keep Windows validation as a required completion gate.

## Validation Scenario 1: Protocol Fixtures

Run the golden and malformed frame tests:

```bash
.venv\Scripts\python -m pytest tests/unit
```

Expected outcome:

- Golden DLT V1 frames produce the expected metadata, raw payload, raw frame, and
  payload hex.
- Malformed, truncated, and oversized frame samples produce typed parser/frame
  errors.
- Non-verbose samples are marked non-verbose and use payload-hex fallback.

## Validation Scenario 2: Local TCP Stream Handling

Run local TCP integration tests:

```bash
.venv\Scripts\python -m pytest tests/integration
```

Expected outcome:

- Fragmented TCP input produces exactly one message per declared DLT frame.
- One receive operation containing multiple frames produces multiple messages in
  stream order.
- Socket close during a partial frame reports a typed error.
- Timeout and reconnect behavior follows configured values.

## Validation Scenario 3: Windows Cleanup

Run Windows-specific lifecycle tests:

```bash
.venv\Scripts\python -m pytest tests/windows
```

Expected outcome:

- Repeated connect, receive, and close cycles release sockets.
- `close()` is idempotent.
- No background work remains after shutdown.

## Validation Scenario 4: Application Iterator Flow

Use a reachable DLT TCP endpoint or a local test server that emits DLT V1 frames.

```python
from py_dlt_client import DltClient

client = DltClient(host="192.168.1.10", port=3490, strict=False)

for message in client.messages():
    print(message.text)
```

Expected outcome:

- Supported verbose messages display readable text such as
  `[ECU1] [SYS:INIT] INFO: System init started`.
- Non-verbose messages display `NON_VERBOSE` with `payload_hex=<hex>`.
- Unsupported verbose arguments do not stop the stream in non-strict mode.

## Validation Scenario 5: Callback and Reconnect Flow

Configure callbacks and force a disconnect from the test server or target.

Expected outcome:

- `on_connect` fires after connection.
- `on_disconnect` fires after socket loss.
- `on_reconnect_attempt` fires with increasing attempt counts.
- Attempts wait approximately the configured interval with 10% tolerance.
- `on_message` receives only messages that pass configured filters.

## Validation Scenario 6: Reference Comparison

Capture or replay an agreed sample stream and compare supported output fields with
an established DLT viewer or receiver.

Expected outcome:

- ECU, APID, CTID, counter, level, verbose flag, supported argument values, and
  readable text match the reference for supported DLT V1 samples.
- Differences for unsupported or out-of-scope payload types are documented as raw
  preserved bytes rather than treated as decoded text.

## Artifact References

- Data model: [data-model.md](./data-model.md)
- Public API contract: [contracts/public-api.md](./contracts/public-api.md)
- Parser contract: [contracts/parser-contract.md](./contracts/parser-contract.md)
