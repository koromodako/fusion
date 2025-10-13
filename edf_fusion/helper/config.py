"""Fusion Core Config Helper"""

from ssl import SSLContext, create_default_context

from aiohttp import Fingerprint


class ConfigError(Exception):
    """Raised whenever a configuration error is encountered"""


def load_ssl_config(
    value: str | dict | bool,
) -> Fingerprint | SSLContext | bool:
    """Load SSL configuration value"""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return bytes.fromhex(value)
    if isinstance(value, dict):
        return create_default_context(
            cafile=value.get('cafile'),
            capath=value.get('capath'),
            cadata=value.get('cadata'),
        )
    raise ConfigError("invalid ssl configuration value!")
