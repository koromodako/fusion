"""Fusion Identity"""

from dataclasses import dataclass, field
from typing import Any

from .abc import Concept


@dataclass(kw_only=True)
class Identity(Concept):
    """Represent an identity and associated properties"""

    username: str
    groups: set[str] = field(default_factory=set)
    properties: dict[str, Any] = field(default_factory=dict)

    @property
    def acs(self) -> set[str]:
        """Identity access control set"""
        return {self.username} | self.groups

    @classmethod
    def from_dict(cls, dct):
        return cls(
            username=dct['username'],
            groups=set(dct['groups']),
        )

    def to_dict(self):
        return {
            'username': self.username,
            'groups': list(sorted(self.groups)),
        }

    def update(self, dct):
        # username cannot be updated
        self.groups = set(dct.get('groups', self.groups))
        self.properties = dct.get('properties', self.properties)


@dataclass(kw_only=True)
class Identities(Concept):
    """Represent an identity and associated properties"""

    _mapping: dict[str, Identity] = field(default_factory=dict)

    @property
    def as_list(self) -> list[Identity]:
        """List of stored identities"""
        return list(self._mapping.values())

    @classmethod
    def from_dict(cls, dct):
        identities = [Identity.from_dict(item) for item in dct['identities']]
        return cls(
            _mapping={identity.username: identity for identity in identities},
        )

    def to_dict(self):
        return {
            'identities': [
                identity.to_dict() for identity in self._mapping.values()
            ],
        }

    def update(self, dct):
        identities = [Identity.from_dict(item) for item in dct['identities']]
        self._mapping = {
            identity.username: identity for identity in identities
        }

    def store(self, identity: Identity):
        """Store identity in mapping"""
        self._mapping[identity.username] = identity
