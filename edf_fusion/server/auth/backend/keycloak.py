"""PyCloak authentication"""

from dataclasses import dataclass
from functools import cached_property
from time import time
from typing import Any

from keycloak import KeycloakOpenID
from keycloak.exceptions import KeycloakPostError

from ....concept import AuthInfo, Identity
from ....helper.logging import get_logger
from ..config import KeycloakConfig
from .abc import FusionAuthBackend

_LOGGER = get_logger('server.auth.backend.keycloak')
_JWT = 'jwt'
_ACCESS_TOKEN = 'access_token'
_REFRESH_TOKEN = 'refresh_token'


def _expired(identity: Identity) -> bool:
    """Determine cache entry expiration status"""
    return identity.properties.get('exp', 0) <= time()


@dataclass(kw_only=True)
class KeycloakAuthBackend(FusionAuthBackend):
    """Keycloak authentication"""

    keycloak_config: KeycloakConfig

    @cached_property
    def _keycloak_oid(self) -> KeycloakOpenID:
        return KeycloakOpenID(
            server_url=self.keycloak_config.server_url,
            client_id=self.keycloak_config.client_id,
            realm_name=self.keycloak_config.realm_name,
            client_secret_key=self.keycloak_config.client_secret,
            verify=self.keycloak_config.verify,
        )

    async def info(self) -> AuthInfo:
        return AuthInfo(
            type='keycloak',
            parameters={
                'host': self.keycloak_config.server_url,
                'realm': self.keycloak_config.realm_name,
                'client': self.keycloak_config.client_id,
                'redirect_uri': self.keycloak_config.redirect_uri,
            },
        )

    async def login(self, data: dict[str, Any]) -> Identity | None:
        """Authenticate user"""
        code = data.get('code')
        if not code:
            return None
        jwt = await self._keycloak_oid.a_token(
            code=code,
            grant_type='authorization_code',
            redirect_uri=self.keycloak_config.redirect_uri,
        )
        access_token = await self._keycloak_oid.a_decode_token(
            jwt.get(_ACCESS_TOKEN, {})
        )
        username = access_token.get('preferred_username')
        if not username:
            _LOGGER.warning("access refused: %s", username)
            return None
        identity = Identity(
            username=username,
            groups=set(access_token.get('groups', [])),
            properties={_JWT: jwt, 'exp': access_token.get('exp', 0)},
        )
        self._save(identity)
        _LOGGER.info("access granted: %s", username)
        return identity

    async def logout(self, identity: Identity):
        """Deauthenticate user"""
        identity = self._load(identity.username)
        if not identity:
            return
        jwt = identity.properties[_JWT]
        try:
            await self._keycloak_oid.a_logout(jwt.get(_REFRESH_TOKEN))
        except:
            _LOGGER.exception("access revoked: %s", identity.username)
            return
        self._drop(identity.username)
        _LOGGER.info("access revoked: %s", identity.username)

    async def is_logged(self, username: str | None) -> Identity | None:
        """Determine user authentication status"""
        if not username:
            return None
        identity = self._load(username)
        if not identity:
            return None
        if not _expired(identity):
            return identity
        jwt = identity.properties[_JWT]
        access_token = await self._keycloak_oid.a_introspect(
            jwt.get(_ACCESS_TOKEN)
        )
        if access_token.get('active', False):
            identity.update({})
            self._save(identity)
            return identity
        try:
            fresh_jwt = await self._keycloak_oid.a_refresh_token(
                jwt.get(_REFRESH_TOKEN)
            )
        except KeycloakPostError:
            _LOGGER.error("access refresh failed: %s", username)
            self._cache.pop(username)
            return None

        access_token = await self._keycloak_oid.a_decode_token(
            fresh_jwt.get(_ACCESS_TOKEN)
        )
        identity.update(
            {
                'groups': access_token.get('groups', []),
                'properties': {
                    _JWT: fresh_jwt,
                    'exp': access_token.get('exp', 0),
                },
            }
        )
        self._save(identity)
        _LOGGER.info("access refreshed: %s", username)
        return identity
