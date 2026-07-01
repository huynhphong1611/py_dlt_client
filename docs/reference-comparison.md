# Reference Comparison Procedure

Use this procedure to compare supported `py_dlt_client` output with an established
DLT viewer or receiver.

## Inputs

- One agreed sample DLT TCP stream or captured replay containing supported DLT V1
  verbose and non-verbose messages.
- A reference tool such as DLT Viewer or `dlt-receive`.
- `py_dlt_client` running against the same sample stream.

## Compare

For supported DLT V1 samples, compare:

- ECU ID
- APID
- CTID
- message counter
- verbose flag
- log level
- supported verbose argument values
- readable text for supported verbose payloads
- raw payload hex for non-verbose or unsupported messages

## Expected Result

All supported fields match the reference interpretation. Unsupported or
out-of-scope payload content is preserved as raw bytes/hex and documented as not
decoded rather than treated as a mismatch.
