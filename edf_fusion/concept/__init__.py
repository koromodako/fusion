"""Fusion Concept"""

from .abc import Concept, ConceptType
from .analysis import Priority, Status
from .analyzer import AnalyzerInfo
from .auth_info import AuthInfo
from .case import Case, CaseType
from .constant import Constant
from .event import Event, EventType
from .identity import Identities, Identity
from .info import Info
from .pdk import PendingDownloadKey


def to_dict_or_none(concept: Concept | None) -> dict | None:
    """Convert concept to dict if not None"""
    if concept is None:
        return None
    return concept.to_dict()


def from_dict_or_none(
    concept_cls: ConceptType, dct: dict | None
) -> Concept | None:
    """Build concept from dict if not None"""
    if dct is None:
        return None
    return concept_cls.from_dict(dct)
