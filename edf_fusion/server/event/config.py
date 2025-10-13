"""Fusion Event API Config"""

from dataclasses import dataclass
from functools import cached_property
from ssl import SSLContext
from typing import Self

from aiohttp import Fingerprint

from ...helper.config import load_ssl_config
from ...helper.logging import get_logger
from ...helper.serializing import Loadable

_LOGGER = get_logger('server.event.config')


@dataclass(kw_only=True)
class FusionEventAPIConfig(Loadable):
    """Fusion Event API Config"""

    webhook: str | None
    api_key: str | None
    api_ssl: Fingerprint | SSLContext | bool = True
    timeout: float

    @cached_property
    def enabled(self) -> bool:
        """Determine if event api is enabled"""
        return bool(self.webhook) and bool(self.api_key)

    @classmethod
    def from_dict(cls, dct: dict) -> Self:
        api_ssl = load_ssl_config(dct['api_ssl'])
        if not api_ssl:
            _LOGGER.warning("client-side certificate validation disabled!")
        return cls(
            webhook=dct['webhook'],
            api_key=dct['api_key'],
            api_ssl=api_ssl,
            timeout=dct['timeout'],
        )
