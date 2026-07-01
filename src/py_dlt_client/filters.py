"""Message delivery filtering."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .models import DltFilter, DltMessage


def normalize_filter(value: DltFilter | dict[str, Any] | None) -> DltFilter | None:
    if value is None:
        return None
    if isinstance(value, DltFilter):
        result = value
    else:
        result = DltFilter(
            ecu=_norm_set(value.get("ecu")),
            apid=_norm_set(value.get("apid")),
            ctid=_norm_set(value.get("ctid")),
            level=_norm_set(value.get("level")),
            verbose_only=bool(value.get("verbose_only", False)),
            non_verbose_only=bool(value.get("non_verbose_only", False)),
        )
    if result.verbose_only and result.non_verbose_only:
        raise ValueError("verbose_only and non_verbose_only are mutually exclusive")
    return result


def matches_filter(message: DltMessage, filters: DltFilter | None) -> bool:
    if filters is None:
        return True
    if filters.verbose_only and not message.verbose:
        return False
    if filters.non_verbose_only and message.verbose:
        return False
    if filters.ecu is not None and message.ecu not in filters.ecu:
        return False
    if filters.apid is not None and message.apid not in filters.apid:
        return False
    if filters.ctid is not None and message.ctid not in filters.ctid:
        return False
    if filters.level is not None and message.level not in filters.level and message.level_name not in filters.level:
        return False
    return True


def _norm_set(value: Any) -> set[Any] | None:
    if value is None:
        return None
    if isinstance(value, (str, bytes)) or not isinstance(value, Iterable):
        values = {value}
    else:
        values = set(value)
    return values or None
