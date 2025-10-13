"""Basic authentication"""

from dataclasses import dataclass
from typing import Any

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError

from ....concept import AuthInfo, Identity
from ....helper.logging import get_logger
from ..config import BasicConfig
from .abc import FusionAuthBackend

_PH = PasswordHasher()
_LOGGER = get_logger('server.auth.backend.basic')


@dataclass(kw_only=True)
class BasicAuthBackend(FusionAuthBackend):
    """Basic authentication"""

    basic_config: BasicConfig

    async def info(self) -> AuthInfo:
        return AuthInfo(type='basic')

    async def login(self, data: dict[str, Any]) -> Identity | None:
        username = data.get('username', '')
        password = data.get('password', '')
        basic_user = self.basic_config.users.get(username)
        if not basic_user:
            _LOGGER.error("access refused: %s", username)
            return None
        try:
            _PH.verify(basic_user.digest, password)
        except VerificationError:
            _LOGGER.error("access refused: %s", username)
            return None
        groups = basic_user.groups or self.basic_config.groups
        identity = Identity(username=username, groups=groups)
        self._save(identity)
        _LOGGER.info("access granted: %s", username)
        return identity

    async def logout(self, identity: Identity):
        self._drop(identity.username)
        _LOGGER.info("access revoked: %s", identity.username)

    async def is_logged(self, username: str | None) -> Identity | None:
        return self._load(username)
