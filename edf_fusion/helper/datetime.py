"""Fusion Core Datetime Helper"""

from datetime import datetime, timezone


def to_iso(dtv: datetime) -> str:
    """iso string from datetime"""
    return dtv.isoformat(timespec='seconds')


def to_iso_or_none(dtv: datetime | None) -> str | None:
    """iso string from datetime or None"""
    if dtv is None:
        return None
    return to_iso(dtv)


def from_iso(dts: str) -> datetime:
    """datetime from iso string"""
    return datetime.fromisoformat(dts)


def from_iso_or_none(dts: str | None) -> datetime | None:
    """datetime from iso string or none"""
    if not dts:
        return None
    return from_iso(dts)


def utcnow() -> datetime:
    """UTC aware datetime now"""
    return datetime.now(timezone.utc)
