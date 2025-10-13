"""Fusion Info API Configuration"""

from dataclasses import dataclass
from typing import Self

from ...helper.serializing import Loadable


@dataclass(kw_only=True)
class FusionInfoAPIConfig(Loadable):
    """Fusion Info API Configuration"""

    auth_required: bool

    @classmethod
    def from_dict(cls, dct: dict) -> Self:
        return cls(auth_required=dct['auth_required'])
