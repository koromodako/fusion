"""Fusion Info"""

from dataclasses import dataclass

from .abc import Concept


@dataclass(kw_only=True)
class Info(Concept):
    """Fusion Info"""

    api: str
    version: str

    @classmethod
    def from_dict(cls, dct):
        return cls(api=dct['api'], version=dct['version'])

    def to_dict(self):
        return {'api': self.api, 'version': self.version}

    def update(self, dct):
        self.api = dct.get('api', self.api)
        self.version = dct.get('version', self.version)
