"""Authentication"""

from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from typing import Self

from ....helper.logging import get_logger
from ....helper.serializing import Loadable
from ..config import (
    AuthBackendConfig,
    AuthStrategy,
    BasicConfig,
    KeycloakConfig,
)
from .abc import FusionAuthBackend, Identity

_LOGGER = get_logger('server.auth.backend')


_AUTH_STRATEGY = {}
# ------------------------------------------------------------------------------
try:
    from .basic import BasicAuthBackend

    _AUTH_STRATEGY[AuthStrategy.BASIC] = lambda config: BasicAuthBackend(
        basic_config=config.basic
    )
    _LOGGER.info("basic authentication is available")
except ImportError as exc:
    _LOGGER.warning("basic authentication is not available (%s)", exc)
# ------------------------------------------------------------------------------
try:
    from .keycloak import KeycloakAuthBackend

    _AUTH_STRATEGY[AuthStrategy.KEYCLOAK] = lambda config: KeycloakAuthBackend(
        keycloak_config=config.keycloak
    )
    _LOGGER.info("keycloak authentication is available")
except ImportError as exc:
    _LOGGER.warning("keycloak authentication is not available (%s)", exc)
# ------------------------------------------------------------------------------


def instanciate_auth(config: AuthBackendConfig) -> FusionAuthBackend | None:
    """Setup webapp authentication backend"""
    if not config.enabled:
        _LOGGER.info("auth backend disabled.")
        return None
    _LOGGER.info("create %s auth...", config.strategy.value)
    strategy = _AUTH_STRATEGY.get(config.strategy)
    if not strategy:
        _LOGGER.critical(
            "cannot create auth (check server config and installed packages)"
        )
        return None
    return strategy(config)
