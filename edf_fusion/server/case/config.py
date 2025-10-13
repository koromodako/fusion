"""Fusion Case API Configuration"""

from dataclasses import dataclass
from typing import Self

from ...helper.serializing import Loadable


@dataclass(kw_only=True)
class FusionCaseAPIConfig(Loadable):
    """Fusion Case API Configuration"""

    @classmethod
    def from_dict(cls, dct: dict) -> Self:
        return cls()
