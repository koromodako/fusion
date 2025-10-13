"""Fusion Core Filesystem Helper"""

from collections.abc import Iterator
from pathlib import Path

GUID_GLOB = '*-*-*-*-*'


def iter_guid_items(directory: Path | None) -> Iterator[Path]:
    """Iterate over directory items whose name match a simple GUID pattern"""
    if not directory:
        return
    if not directory.is_dir():
        return
    yield from directory.glob(GUID_GLOB)


def disk_usage(item: Path) -> int:
    """Compute disk usage"""
    if item.is_dir():
        return sum(
            disk_usage(subitem)
            for subitem in item.rglob('*')
            if subitem.is_file()
        )
    if item.is_file():
        return item.stat().st_size
    return 0
