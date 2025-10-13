"""Fusion Download API Configuration"""

from dataclasses import dataclass
from typing import Self

from ...helper.serializing import Loadable


@dataclass(kw_only=True)
class FusionDownloadAPIConfig(Loadable):
    """Fusion Download API"""

    max_pending_count: int

    @classmethod
    def from_dict(cls, dct: dict) -> Self:
        max_pending_count = int(dct.get('max_pending_count', 25))
        return cls(max_pending_count=max(max_pending_count, 1))
