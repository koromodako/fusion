"""Fusion Notifier"""

from dataclasses import dataclass
from ssl import SSLContext

from aiohttp import (
    ClientConnectionError,
    ClientSession,
    ClientTimeout,
    Fingerprint,
)

from ..concept import Event
from .logging import get_logger

_LOGGER = get_logger('helper.notifier')
_FUSION_NOTIFIER_HEADER = 'X-Fusion-Notifier-Token'


@dataclass(kw_only=True)
class FusionNotifier:
    """Fusion Notifier"""

    session: ClientSession
    api_ssl: Fingerprint | SSLContext | bool = True

    async def _notify(self, webhook: str, dct: dict) -> int:
        """Emit notification"""
        try:
            async with self.session.post(
                webhook,
                ssl=self.api_ssl,
                json=dct,
            ) as resp:
                _LOGGER.info("notify %s (status=%d)", webhook, resp.status)
                return resp.status
        except TimeoutError:
            _LOGGER.error("notify %s (timeout)", webhook)
            return -1
        except ClientConnectionError:
            _LOGGER.exception("notify %s (connection)", webhook)
            return -2

    async def notify(
        self, event: Event, webhooks: list[str] = None
    ) -> dict[str, int]:
        """Send event to endpoints (including global endpoint if set)"""
        dct = event.to_dict()
        webhooks = webhooks or []
        webhooks.extend(event.case.webhooks)
        status_map = {}
        for webhook in webhooks:
            status_map[webhook] = await self._notify(webhook, dct)
        return status_map


def create_notifier_session(api_key: str, timeout: float) -> ClientSession:
    """Create aiohttp.ClientSession instance for FusionNotifier"""
    return ClientSession(
        headers={_FUSION_NOTIFIER_HEADER: api_key},
        timeout=ClientTimeout(total=timeout),
        raise_for_status=False,
    )
