# Research: Pure Python DLT V1 TCP Client for Windows

## Decision: Runtime Uses CPython 3.11+ and the Standard Library

**Rationale**: The constitution requires a pure Python, Windows-first library with
minimal dependency friction. CPython 3.11+ provides stable `socket`, `struct`,
`dataclasses`, `logging`, `threading`, `queue`, and `typing` support needed for the
client without external runtime packages.

**Alternatives considered**:

- Native DLT bindings: rejected because native extensions and external binaries
  violate the installability and Windows-first constraints.
- Async framework runtime dependency: rejected for the first version because the
  requested API is callback/iterator oriented and blocking sockets with explicit
  timeouts are sufficient.
- Python 3.8/3.9 minimum: rejected because those versions are older for a new
  library and provide less typing ergonomics for downstream users.

## Decision: Test Tooling Uses pytest as a Development Dependency

**Rationale**: The feature requires a large matrix of golden protocol fixtures,
malformed frames, local TCP integration, timeout behavior, and repeated cleanup
checks. pytest is pure Python and well suited for parameterized binary fixture
tests. It is not a runtime dependency.

**Alternatives considered**:

- Standard-library `unittest` only: viable, but less concise for fixture-heavy
  protocol matrices.
- External network test tools: rejected because local controllable TCP servers can
  be implemented with the standard library.

## Decision: DLT Frame Length Limit Defaults to 65,535 Bytes

**Rationale**: The DLT standard header carries total message length in a 16-bit
field. The first version will reject frames smaller than the minimum declared
header size or larger than the configured maximum, with the default maximum set to
65,535 bytes. This prevents unbounded buffering and aligns with the wire format.

**Alternatives considered**:

- Unlimited stream buffering: rejected because malformed input could consume
  memory indefinitely.
- Smaller arbitrary cap: rejected because it could reject valid DLT frames without
  a product reason.

## Decision: Frame Reader Owns TCP Reassembly

**Rationale**: TCP does not preserve message boundaries. The frame reader must
buffer bytes, read the minimum standard header, inspect the DLT total length, then
wait until the full frame is available before handing bytes to the parser. It must
also emit multiple frames if one receive operation contains coalesced messages.

**Alternatives considered**:

- `recv(4096)` per message: rejected because it fails for fragmented and coalesced
  TCP frames.
- Line-oriented reads: rejected because DLT TCP input is binary, not text.

## Decision: Parser Returns Typed Models and Typed Errors

**Rationale**: The host application needs stable objects for ECU/APID/CTID/level
metadata, decoded arguments, raw payload, raw frame, and formatted text. Typed
errors make strict/non-strict behavior testable and let applications distinguish
connection failures, malformed frames, unsupported argument types, and parser
failures.

**Alternatives considered**:

- Dictionaries only: rejected because typed attributes and error categories are
  clearer for a public library contract.
- Exceptions for every unsupported argument in all modes: rejected because
  non-strict streaming must continue after a bad message where safe.

## Decision: Verbose Payload Scope Is Narrow and Explicit

**Rationale**: The first version supports the requested common argument categories:
strings, signed integers, unsigned integers, booleans, float32/float64, and raw
bytes. Unsupported argument types are preserved as raw bytes/hex and marked
unsupported rather than guessed.

**Alternatives considered**:

- Full AUTOSAR DLT payload coverage: rejected as too broad for the first version.
- Treat unsupported payload bytes as decoded text: rejected because it would
  misrepresent diagnostic data.

## Decision: Non-Verbose Messages Use Honest Fallback Output

**Rationale**: Non-verbose DLT messages require external message descriptions such
as FIBEX/ARXML to reconstruct original text. The first version exposes metadata,
message ID if safely parseable, raw payload, and payload hex without claiming full
text decoding.

**Alternatives considered**:

- Implement FIBEX/ARXML mapping now: rejected as explicitly out of scope.
- Try heuristic non-verbose decoding: rejected because it is unreliable and would
  produce misleading logs.

## Decision: Reconnect Is Synchronous With Explicit Delay and Events

**Rationale**: The requested callback and iterator APIs can be served by a
blocking client loop with configurable timeout, reconnect interval, and retry
limit. Reconnect events make lifecycle behavior visible, and explicit sleep
between attempts prevents busy loops.

**Alternatives considered**:

- Silent reconnect: rejected because applications need lifecycle observability.
- Background thread always on: rejected because iterator users should be able to
  consume synchronously and close deterministically.

## Decision: Filtering Happens Before Message Delivery

**Rationale**: Filters by ECU, APID, CTID, level, verbose-only, and non-verbose-only
are easiest to reason about once a message object exists. Applying filters before
callbacks/iterator delivery avoids burdening applications with repeated checks.

**Alternatives considered**:

- Filter raw bytes before parsing: rejected because fields are not reliably known
  until headers are parsed.
- No first-version filter support: rejected because the feature specification asks
  for filtering in the first-version API design.

## Decision: Validation Uses Synthetic Fixtures Plus Reference Comparison

**Rationale**: Synthetic fixtures provide deterministic coverage for edge cases
that may be difficult to capture from real systems, while comparison against an
established DLT viewer or receiver validates supported fields against existing
ecosystem behavior.

**Alternatives considered**:

- Real ECU-only validation: rejected because it is hard to run in CI and does not
  reliably cover malformed/truncated inputs.
- Synthetic-only validation: rejected because reference comparison is an explicit
  acceptance criterion.
