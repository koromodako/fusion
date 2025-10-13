"""Fusion Auth Info"""

from dataclasses import dataclass, field
from typing import Any

from .abc import Concept


@dataclass(kw_only=True)
class AuthInfo(Concept):
    """Authentication information"""

    type: str
    parameters: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, dct):
        return cls(
            type=dct['type'],
            parameters=dct['parameters'],
        )

    def to_dict(self):
        return {
            'type': self.type,
            'parameters': self.parameters,
        }

    def update(self, dct):
        self.type = dct.get('type', self.type)
        self.parameters = dct.get('parameters', self.parameters)
