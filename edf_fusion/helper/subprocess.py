"""Fusion Core Subprocess Helper"""

from asyncio import create_subprocess_exec
from os import environ
from subprocess import DEVNULL

from .logging import get_logger

_LOGGER = get_logger('helper.subprocess')


async def create_subprocess_and_wait(argv: list[str], **kwargs) -> bool:
    """Create subprocess and wait for termination then return exit code"""
    for arg in ('stdin', 'stdout', 'stderr'):
        if arg not in kwargs:
            kwargs[arg] = DEVNULL
    if 'env' in kwargs:
        env = dict(environ)
        env.update(kwargs['env'])
        kwargs['env'] = env
    _LOGGER.info("starting subprocess (argv=%s)", argv)
    process = await create_subprocess_exec(*argv, **kwargs)
    _LOGGER.info("waiting for subprocess (pid=%d)", process.pid)
    returncode = await process.wait()
    _LOGGER.info(
        "subprocess ended (pid=%d, returcode=%d)",
        process.pid,
        returncode,
    )
    return returncode == 0
