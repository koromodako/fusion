"""Fusion Client Configuration"""

from dataclasses import dataclass, field
from functools import cached_property
from ssl import SSLContext

from aiohttp import BasicAuth, ClientTimeout, Fingerprint
from yarl import URL

from ..__version__ import version
from ..helper.logging import get_logger
from ..server.auth import FUSION_API_TOKEN_HEADER

_LOGGER = get_logger('client.config')

Headers = dict[str, str]


@dataclass(kw_only=True)
class FusionClientConfig:
    """Fusion Client Config"""

    api_url: URL
    api_ssl: Fingerprint | SSLContext | bool = True
    api_key: str | None = None
    proxy_url: URL | None = None
    proxy_auth: BasicAuth | None = None
    proxy_headers: Headers | None = None
    proxy_trust_env: bool = False
    timeout: ClientTimeout = field(default_factory=ClientTimeout)

    @cached_property
    def headers(self) -> Headers:
        """Headers"""
        headers = {'User-Agent': f'fusion-client/{version}'}
        if self.api_key:
            headers[FUSION_API_TOKEN_HEADER] = self.api_key
        return headers
