# py_dlt_client

Pure Python DLT V1 TCP receiver/parser for Windows applications.

`py_dlt_client` connects to a `dlt-daemon` TCP endpoint, reconstructs binary DLT
V1 frames, parses header metadata, decodes supported verbose payload arguments,
and exposes `DltMessage` objects plus honest readable text output.

## Iterator Usage

```python
from py_dlt_client import DltClient

client = DltClient(host="192.168.1.10", port=3490, strict=False)

for message in client.messages():
    print(message.text)
```

## Callback Usage

```python
from py_dlt_client import DltClient

def on_message(message):
    print(message.text)

def on_disconnect(error):
    print(f"Disconnected: {error}")

client = DltClient(
    host="192.168.1.10",
    auto_reconnect=True,
    reconnect_interval=3,
    strict=False,
)
client.on_message(on_message)
client.on_disconnect(on_disconnect)
client.run_forever()
```

## Terminal CLI

From the repository checkout, install the package first:

```bash
python -m pip install -e .
```

Then receive live DLT TCP logs directly from a terminal:

```bash
py-dlt-client --host localhost --port 3490
```

If you have not installed the console script yet, run the module form from the
source checkout:

```bash
python -m py_dlt_client --host localhost --port 3490
```

Common diagnostic options:

```bash
py-dlt-client --host 192.168.1.10 --strict
py-dlt-client --host 192.168.1.10 --reconnect --reconnect-interval 3
py-dlt-client --host 192.168.1.10 --apid SYS --ctid INIT
py-dlt-client --host 192.168.1.10 --level ERROR --level WARN
py-dlt-client --host 192.168.1.10 --verbose-only
py-dlt-client --host 192.168.1.10 --non-verbose-only
```

Message lines are written to stdout. Connection, parser, disconnect, and
reconnect diagnostics are written to stderr. The CLI receives live TCP DLT
streams only; it does not read `.dlt` storage files.

## Output Semantics

Verbose messages with supported argument types are formatted as readable text:

```text
[ECU1] [SYS:INIT] INFO: System init started
```

Non-verbose messages do not have enough information to reconstruct original log
text without external FIBEX/ARXML descriptions, so they use payload hex fallback:

```text
[ECU1] [TEL:CRSH] NON_VERBOSE: payload_hex=0000000c01ff90aa
```

Unsupported verbose argument types are preserved as raw bytes/hex in non-strict
mode. In strict mode, parser errors and unsupported types are raised through typed
exceptions.
