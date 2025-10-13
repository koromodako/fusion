"""Fusion Core Tracing Helper"""

from ..concept import Identity
from .logging import get_logger

Data = dict | list | str | None


_LOGGER = get_logger('helper.tracing')


def trace_user_op(
    identity: Identity,
    operation: str,
    *,
    granted: bool,
    context: dict | None = None,
    exception: Exception | None = None,
):
    """Trace user operation and raise exception if needed"""
    outcome = 'granted' if granted else 'refused'
    log_fun = _LOGGER.info if granted else _LOGGER.warning
    log_fun = _LOGGER.error if exception else log_fun
    log_fun("%s %s to %s (%s)", outcome, operation, identity.username, context)
    if exception:
        raise exception
