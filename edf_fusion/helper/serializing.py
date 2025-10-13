"""Fusion Core Serialization Helper"""

from json import dumps, loads
from pathlib import Path
from typing import Type

from yaml import safe_dump, safe_load


def dump_json(obj) -> str:
    """Convert object to JSON string"""
    return dumps(obj, separators=(',', ':'))


def load_json(text: str):
    """Load object from JSON string"""
    return loads(text)


_LOAD_STRATEGY = {
    '.json': load_json,
    '.yaml': safe_load,
    '.yml': safe_load,
}
_DUMP_STRATEGY = {
    '.json': dump_json,
    '.yaml': safe_dump,
    '.yml': safe_dump,
}


class Loadable:
    """Loadable ABC"""

    @classmethod
    def from_dict(cls, dct):
        """Build instance from JSON serializable dict"""
        raise NotImplementedError

    @classmethod
    def from_filepath(cls, filepath: Path):
        """Build instance from JSON stored in file"""
        strategy = _LOAD_STRATEGY[filepath.suffix]
        text = filepath.read_text(encoding='utf-8')
        dct = strategy(text)
        return cls.from_dict(dct)


LoadableType = Type[Loadable]


class Dumpable:
    """Dumpable ABC"""

    def to_dict(self):
        """Convert instance to JSON serializable dict"""
        raise NotImplementedError

    def to_filepath(self, filepath: Path):
        """Convert instance to JSON stored in file"""
        strategy = _DUMP_STRATEGY[filepath.suffix]
        dct = self.to_dict()
        text = strategy(dct)
        filepath.write_text(text, encoding='utf-8')


DumpableType = Type[Dumpable]
