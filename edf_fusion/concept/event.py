"""Fusion Event"""

from dataclasses import dataclass
from typing import Type

from .abc import Concept
from .case import Case


@dataclass(kw_only=True)
class Event(Concept):
    """Fusion Event"""

    source: str
    category: str
    case: Case
    ext: dict | None = None

    @classmethod
    def from_dict(cls, dct):
        return cls(
            source=dct['source'],
            category=dct['category'],
            case=Case.from_dict(dct['case']),
            ext=dct['ext'],
        )

    def to_dict(self):
        return {
            'source': self.source,
            'category': self.category,
            'case': self.case.to_dict(),
            'ext': self.ext,
        }

    def update(self, dct):
        raise RuntimeError("Event.update shall not be called")


EventType = Type[Event]
