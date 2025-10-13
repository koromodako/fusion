"""Fusion Concept ABC"""

from typing import Type

from ..helper.serializing import Dumpable, Loadable


class Concept(Dumpable, Loadable):
    """Interface for JSON serializable concept"""

    def update(self, dct):
        """Update concept fields from dict"""
        raise NotImplementedError


ConceptType = Type[Concept]
