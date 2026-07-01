"""Default DLT message text formatter."""

from __future__ import annotations

from .models import DltMessage


def format_message(message: DltMessage) -> str:
    ecu = message.ecu or "----"
    apid = message.apid or "----"
    ctid = message.ctid or "----"
    level = message.level_name or "UNKNOWN"
    if not message.verbose:
        return f"[{ecu}] [{apid}:{ctid}] NON_VERBOSE: payload_hex={message.payload_hex}"
    if not message.args:
        return f"[{ecu}] [{apid}:{ctid}] {level}: payload_hex={message.payload_hex}"
    rendered = " ".join(arg.display if arg.display is not None else str(arg.value) for arg in message.args)
    return f"[{ecu}] [{apid}:{ctid}] {level}: {rendered}"
