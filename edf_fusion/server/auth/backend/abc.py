"""Authentication ABC"""

from dataclasses import dataclass, field
from typing import Any

from ....concept import AuthInfo, Identity


@dataclass(kw_only=True)
class FusionAuthBackend:
    """Authentication Backend"""

    _cache: dict[str, Identity] = field(default_factory=dict)

    def _save(self, identity: Identity):
        self._cache[identity.username] = identity

    def _load(self, username: str | None) -> Identity | None:
        return self._cache.get(username)

    def _drop(self, username: str | None):
        self._cache.pop(username, None)

    async def info(self) -> AuthInfo:
        """Authentication configuration"""
        raise NotImplementedError

    async def login(self, data: dict[str, Any]) -> Identity | None:
        """Authenticate user"""
        raise NotImplementedError

    async def logout(self, identity: Identity):
        """Deauthenticate user"""
        raise NotImplementedError

    async def is_logged(self, username: str | None) -> Identity | None:
        """Determine user authentication status"""
        raise NotImplementedError
