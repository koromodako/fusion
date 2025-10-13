"""Carbon Case Synchronizer"""

from asyncio import Event, get_running_loop, run, wait_for
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from pathlib import Path
from signal import SIGINT, SIGTERM

from edf_fusion.concept import Case
from edf_fusion.helper.logging import get_logger

from .config import FusionSynchronizerConfig
from .storage import FusionStorage

_LOGGER = get_logger('server.synchronizer')


class FusionSynchronizerError(Exception):
    """Fusion Synchronizer Error"""


@dataclass(kw_only=True)
class FusionSynchronizer:
    """Fusion Synchronizer"""

    config: FusionSynchronizerConfig
    storage: FusionStorage
    sync_case_impl: Callable[[FusionStorage, Case, Path], Awaitable[None]]
    _event: Event = field(default_factory=Event)

    def _shutdown(self):
        _LOGGER.warning("shutdown requested")
        self._event.set()

    async def _synchronize_loop(self):
        while not self._event.is_set():
            async for case in self.storage.enumerate_cases():
                await self.sync_case_impl(
                    self.storage, case, self.config.directory
                )
            try:
                await wait_for(self._event.wait(), 3600)
            except TimeoutError:
                continue

    async def _synchronize(self):
        loop = get_running_loop()
        for sig in (SIGINT, SIGTERM):
            loop.add_signal_handler(sig, self._shutdown)
        if not self.config.directory:
            _LOGGER.warning("synchronizer is not configured.")
            return
        try:
            await self.storage.startup()
            await self._synchronize_loop()
        except FusionSynchronizerError as exc:
            _LOGGER.error("fusion synchronizer error: %s", exc)
        finally:
            await self.storage.cleanup()

    def run(self):
        """Prepare analyzer and start analysis loop"""
        if not self.config.enabled:
            _LOGGER.warning("synchronizer is disabled.")
            return
        if not self.config.directory.is_dir():
            _LOGGER.warning(
                "synchronizer directory not found: %s",
                self.config.directory,
            )
        run(self._synchronize())
