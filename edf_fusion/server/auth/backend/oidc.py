"""OIDC authentication"""

from dataclasses import dataclass
from functools import cached_property
from typing import Any
import jwt

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError

from ....concept import AuthInfo, Identity
from ....helper.logging import get_logger
from ..config import BasicConfig
from .abc import FusionAuthBackend

_PH = PasswordHasher()
_LOGGER = get_logger('server.auth.backend.oidc')


@dataclass(kw_only=True)
class OAuthBackend(FusionAuthBackend):
    """Basic authentication"""

    oidc_config: OIDCConfig


    @cached_property
    async def _oidc_config(self):
        try:
            async with httpx.AsyncClient(follow_redirects=True, headers=headers, timeout=5) as client:
                response = await client.get(self.oidc_config.discovery_url)
                response.raise_for_status()
                return response.json()
        except Exception:
            raise HTTPException(status_code=400, detail="Bad Request")


    @cached_property
    def _oidc_client(self) -> OAuth2Client:
        return OAuth2Client(
            client_id=self.oidc_config.OIDC_CLIENT_ID,
            client_secret=self.oidc_config.OIDC_CLIENT_SECRET,
            scope="openid profile",
            redirect_uri=self.oidc_config.OIDC_REDIRECT_URI,
        )


    async def info(self) -> AuthInfo:
        return AuthInfo(
            type='oidc', 
            parameters={
                'client_id': self.oidc_config.client_id,
                'discovery_url': self.oidc_config.discovery_url,
                'redirect_uri': self.oidc_config.redirect_uri,
            },
        )


    async def login(self, data: dict[str, Any]) -> Identity | None:
        """Authenticate user"""

        try:
            token = _oidc_client.fetch_token(
                _oidc_config.get("token_endpoint"),
                grant_type="authorization_code",
                code=code,
            )
        except Exception:
            raise HTTPException(status_code=401, detail="OIDC login failed")

        id_token = token.get("id_token")
        alg = jwt.get_unverified_header(id_token).get("alg")

        match alg:
            case "HS256":
                decoded = jwt.decode(
                    id_token,
                    self.oidc_config.client_secret,
                    algorithms=["HS256"],
                    audience=self.oidc_config.client_id,
                )
            case "RS256":
                jwks_uri = _oidc_config.get("jwks_uri")
                issuer = _oidc_config.get("issuer")
                jwks_client = jwt.PyJWKClient(jwks_uri)

                try:
                    signing_key = jwks_client.get_signing_key_from_jwt(id_token)
                    decoded = jwt.decode(
                        id_token,
                        key=signing_key.key,
                        algorithms=["RS256"],
                        audience=self.oidc_config.OIDC_CLIENT_ID,
                        issuer=issuer,
                    )
                except Exception:
            _LOGGER.warning("access refused: %s", username)
            return None
            case _:
            _LOGGER.warning("access refused: %s", username)
            return None


        sub = decoded.get("sub")
        if not sub:
            _LOGGER.warning("access refused: %s", username)
            return None

        preferred_username = decoded.get("preferred_username", None)
        
        access_token = token.get("access_token", None)
        if not access_token:
            _LOGGER.warning("access refused: %s", username)
            return None

        identity = Identity(
            username=sub,
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
