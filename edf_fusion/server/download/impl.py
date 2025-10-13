"""Fusion Download API"""

from asyncio import Lock
from dataclasses import dataclass, field
from datetime import timedelta
from pathlib import Path
from uuid import UUID

from aiohttp.web import Application, Request, Response, StreamResponse, get

from ...concept import PendingDownloadKey
from ...helper.aiohttp import json_response, stream_response
from ...helper.datetime import datetime, utcnow
from ...helper.logging import get_logger
from ...helper.streaming import stream_from_file
from .config import FusionDownloadAPIConfig

_LOCK = Lock()
_LOGGER = get_logger('server.download.impl')
_FIVE_SECONDS = timedelta(seconds=5)
_FUSION_DL_API = 'fusion_dl_api'


@dataclass(kw_only=True)
class _PendingDownloadInfo:
    """Pending Download"""

    created: datetime = field(default_factory=utcnow)
    filepath: Path
    filename: str


PendingDownloadMapping = dict[PendingDownloadKey, _PendingDownloadInfo]


@dataclass(kw_only=True)
class FusionDownloadAPI:
    """Fusion Download API"""

    config: FusionDownloadAPIConfig
    _pending_downloads: PendingDownloadMapping = field(default_factory=dict)

    def setup(self, webapp: Application):
        """Setup web application routes"""
        _LOGGER.info("install download api...")
        webapp[_FUSION_DL_API] = self
        webapp.add_routes(
            [
                get('/api/download/{guid}/{token}', self.download),
            ]
        )
        _LOGGER.info("download api installed.")

    def _cleanup(self):
        now = utcnow()
        to_pop = [
            pdk
            for pdk, pdi in self._pending_downloads.items()
            if now - pdi.created > _FIVE_SECONDS
        ]
        for pdk in to_pop:
            self._pending_downloads.pop(pdk, None)

    async def prepare(
        self, filepath: Path, filename: str
    ) -> PendingDownloadKey | None:
        """Prepare a file for download"""
        async with _LOCK:
            # perform cleanup if needed
            self._cleanup()
            # after cleanup, determine if too many pending downloads
            if len(self._pending_downloads) >= self.config.max_pending_count:
                return None
            # prepare download
            pdk = PendingDownloadKey()
            self._pending_downloads[pdk] = _PendingDownloadInfo(
                filepath=filepath, filename=filename
            )
            return pdk

    async def download(self, request: Request) -> Response | StreamResponse:
        """Handle client request to download a file"""
        # note: this route is public, no prior authentication required
        pdk = PendingDownloadKey(
            guid=UUID(request.match_info['guid']),
            token=request.match_info['token'],
        )
        pdi = self._pending_downloads.pop(pdk, None)
        if not pdi:
            return json_response(status=404, message="Download not found")
        response = await stream_response(
            request,
            pdi.filename,
            stream_from_file(pdi.filepath),
        )
        return response


def get_fusion_dl_api(request: Request) -> FusionDownloadAPI:
    """Retrieve FusionInfoAPI instance from request"""
    return request.app[_FUSION_DL_API]
