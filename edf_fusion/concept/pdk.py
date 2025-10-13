"""Fusion Download Info"""

from dataclasses import dataclass, field
from functools import partial
from secrets import token_urlsafe
from uuid import UUID, uuid4

from .abc import Concept


@dataclass(kw_only=True, frozen=True)
class PendingDownloadKey(Concept):
    """Pending Download Identifier"""

    guid: UUID = field(default_factory=uuid4)
    token: str = field(default_factory=partial(token_urlsafe, 16))

    @classmethod
    def from_dict(cls, dct):
        return cls(guid=UUID(dct['guid']), token=dct['token'])

    def to_dict(self):
        return {'guid': str(self.guid), 'token': self.token}

    def update(self, dct):
        raise RuntimeError("DownloadInfo.update shall not be called")
