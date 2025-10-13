"""Fusion Auth API Client"""

from dataclasses import dataclass

from ...concept import AuthInfo, Concept, Identity
from ..client import FusionClient


@dataclass(kw_only=True)
class _Credentials(Concept):
    """Credentials"""

    username: str
    password: str

    @classmethod
    def from_dict(cls, dct):
        raise NotImplementedError("Credentials.from_dict shall not be called")

    def to_dict(self):
        return {'data': {'username': self.username, 'password': self.password}}

    def update(self, dct):
        raise NotImplementedError("Credentials.update shall not be called")


@dataclass(kw_only=True)
class FusionAuthAPIClient:
    """Fusion Auth API Client"""

    fusion_client: FusionClient

    async def is_logged(self) -> Identity | None:
        """Determine if user is authenticated"""
        endpoint = '/api/auth/is_logged'
        return await self.fusion_client.get(endpoint, concept_cls=Identity)

    async def login(self, username: str, password: str) -> Identity | None:
        """Authenticate user"""
        creds = _Credentials(username=username, password=password)
        endpoint = '/api/auth/login'
        return await self.fusion_client.post(
            endpoint, creds, concept_cls=Identity
        )

    async def logout(self):
        """Deauthenticate user"""
        endpoint = '/api/auth/logout'
        return await self.fusion_client.get(endpoint)

    async def config(self) -> AuthInfo | None:
        """Authentication configuration"""
        endpoint = '/api/auth/config'
        return await self.fusion_client.get(endpoint, concept_cls=AuthInfo)

    async def identities(self) -> list[Identity] | None:
        """Retrieve known identities"""
        endpoint = '/api/auth/identities'
        return await self.fusion_client.get(endpoint, concept_cls=Identity)
