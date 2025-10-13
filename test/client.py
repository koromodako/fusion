#!/usr/bin/env python3
"""Test Client"""

from asyncio import CancelledError, run

from aiohttp import ClientConnectorError, ClientPayloadError
from yarl import URL

from edf_fusion.client import (
    FusionCaseAPIClient,
    FusionClient,
    FusionClientConfig,
    FusionInfoAPIClient,
    create_session,
)
from edf_fusion.concept import Case
from edf_fusion.helper.logging import get_logger

_LOGGER = get_logger('client', root='test')


def _log_failure():
    _LOGGER.critical("test failure!")


async def _playbook(fusion_client: FusionClient):
    _LOGGER.info("starting playbook")
    fusion_case_api_client = FusionCaseAPIClient(
        case_cls=Case, fusion_client=fusion_client
    )
    fusion_info_api_client = FusionInfoAPIClient(fusion_client=fusion_client)
    info = await fusion_info_api_client.info()
    _LOGGER.info("retrieved info: %s", info)
    case = await fusion_case_api_client.create_case(
        Case(
            managed=True,
            tsid=None,
            name='test case',
            description='test description',
        )
    )
    if not case:
        _log_failure()
        return
    _LOGGER.info("created case: %s", case)
    case.tsid = '#00000000'
    case = await fusion_case_api_client.update_case(case)
    if not case:
        _log_failure()
        return
    _LOGGER.info("updated case: %s", case)
    case = await fusion_case_api_client.retrieve_case(case.guid)
    if not case:
        _log_failure()
        return
    _LOGGER.info("retrieved case: %s", case)
    cases = await fusion_case_api_client.enumerate_cases()
    if not cases:
        _log_failure()
        return
    _LOGGER.info("enumerated cases: %s", cases)


async def app():
    """Application entrypoint"""
    config = FusionClientConfig(
        api_url=URL('http://127.0.0.1:18080'),
        api_key='test',
    )
    session = create_session(config)
    async with session:
        fusion_client = FusionClient(config=config, session=session)
        try:
            await _playbook(fusion_client)
        except CancelledError:
            _LOGGER.info("process terminated.")
        except ClientPayloadError:
            _LOGGER.info("server disconnected")
        except ClientConnectorError:
            _LOGGER.info("cannot connect to server")


if __name__ == '__main__':
    run(app())
