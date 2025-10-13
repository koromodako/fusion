"""Fusion Analysis"""

from enum import Enum


class Status(Enum):
    """Analysis Status"""

    PENDING = 'pending'
    QUEUED = 'queued'
    EXTRACTING = 'extracting'
    PROCESSING = 'processing'
    SUCCESS = 'success'
    FAILURE = 'failure'


class Priority(Enum):
    """Analysis Priority"""

    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
