"""Fusion Constant API Config"""

from dataclasses import dataclass
from pathlib import Path
from typing import Self

from ...helper.serializing import Loadable


@dataclass(kw_only=True)
class FusionConstantAPIConfig(Loadable):
    """Fusion Constant API Configuration"""

    auth_required: bool
    constant_path: Path

    @classmethod
    def from_dict(cls, dct: dict) -> Self:
        return cls(
            auth_required=dct['auth_required'],
            constant_path=Path(dct['constant_path']),
        )
