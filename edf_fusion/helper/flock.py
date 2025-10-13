"""File Lock"""

from asyncio import sleep
from dataclasses import dataclass
from fcntl import LOCK_EX, LOCK_NB, LOCK_UN, flock
from functools import cached_property
from io import IOBase
from pathlib import Path


@dataclass(kw_only=True)
class Flock:
    """File Lock"""

    filepath: Path
    _fobj: IOBase | None = None

    @cached_property
    def lockpath(self) -> Path:
        """Lock path for file path"""
        return self.filepath.parent / f'{self.filepath.name}.lck'

    async def __aenter__(self):
        self.lockpath.touch()
        self._fobj = self.lockpath.open('rb')
        while True:
            try:
                flock(self._fobj, LOCK_EX | LOCK_NB)
                break
            except BlockingIOError:
                await sleep(1)
        return self

    async def __aexit__(self, exc_typ, exc_val, exc_trb):
        flock(self._fobj, LOCK_UN)
        self._fobj.close()
        self._fobj = None
