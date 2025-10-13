"""Fusion Core Zip Helper"""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from .logging import get_logger

_LOGGER = get_logger('helper.zip')


def create_zip(
    archive: Path,
    root: Path,
    files: list[Path] | None = None,
    directories: list[Path] | None = None,
):
    """Create zip archive from given items"""
    _LOGGER.info("creating zip archive: %s", archive)
    files = files or []
    files = [item for item in files if item.is_file()]
    directories = directories or []
    directories = [item for item in directories if item.is_dir()]
    with ZipFile(archive, 'w', compression=ZIP_DEFLATED) as zipf:
        for item in files:
            zipf.write(item, arcname=item.name)
        for directory in directories:
            for item in directory.rglob('*'):
                if not item.is_file():
                    continue
                zipf.write(item, arcname=str(item.relative_to(root)))


def extract_zip(archive: Path, directory: Path):
    """Extract zip archive to directory"""
    _LOGGER.info("extracting zip archive: %s", archive)
    with ZipFile(archive, 'r') as zipf:
        for member in zipf.infolist():
            if member.is_dir():
                continue
            zipf.extract(member, path=directory)
