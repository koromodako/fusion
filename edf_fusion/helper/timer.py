"""Fusion Core Timer module"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass
class Timer:
    """Timer object"""

    beg: datetime | None = None
    end: datetime | None = None

    @property
    def elapsed(self) -> timedelta:
        """Elasped time"""
        return self.end - self.beg

    def __enter__(self):
        self.beg = datetime.now(timezone.utc)
        self.end = None
        return self

    def __exit__(self, exc_val, exc_typ, exc_trb):
        self.end = datetime.now(timezone.utc)
