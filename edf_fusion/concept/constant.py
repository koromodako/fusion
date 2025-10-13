"""Fusion Constant"""

from dataclasses import dataclass

from .abc import Concept


@dataclass(kw_only=True)
class Constant(Concept):
    """Fusion Constant"""

    banner: str | None
    allow_empty_acs: bool

    @classmethod
    def from_dict(cls, dct):
        return cls(
            banner=dct.get('banner'),
            allow_empty_acs=dct.get('allow_empty_acs', True),
        )

    def to_dict(self):
        return {
            'banner': self.banner,
            'allow_empty_acs': self.allow_empty_acs,
        }

    def update(self, dct):
        """Update case with dct"""
        raise RuntimeError("Constant.update shall not be called!")
