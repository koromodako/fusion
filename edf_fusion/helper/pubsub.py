"""Fusion Core Pub/Sub Helper"""

from asyncio import Event, Queue
from collections.abc import AsyncIterator
from dataclasses import dataclass, field

from ..concept import Concept

DEFAULT_CHANNEL = 'general'


@dataclass(kw_only=True)
class PubSub:
    """Publisher Subscriber System"""

    _terminating: Event = field(default_factory=Event)
    _channels: dict[str, dict[str, Queue[Concept | None]]] = field(
        default_factory=dict
    )

    async def subscribers(self, channel: str) -> list[str]:
        """Retrieve channel subscribers"""
        subscribers = self._channels.get(channel)
        if not subscribers:
            return []
        return list(subscribers.keys())

    async def publish(self, concept: Concept, channel: str = DEFAULT_CHANNEL):
        """Publish"""
        subscribers = self._channels.get(channel)
        if not subscribers:
            return
        for queue in subscribers.values():
            await queue.put(concept)

    async def subscribe(
        self, client_guid: str, channel: str = DEFAULT_CHANNEL
    ) -> AsyncIterator[Concept]:
        """Subscribe"""
        if self._terminating.is_set():
            return
        # create channel if needed
        if channel not in self._channels:
            self._channels[channel] = {}
        subscribers = self._channels[channel]
        # create subscriber queue if needed
        if client_guid not in subscribers:
            subscribers[client_guid] = Queue()
        # loop until unsubscribe is called
        while True:
            queue = subscribers.get(client_guid)
            if not queue:
                break
            concept = await queue.get()
            if concept is None:
                break
            yield concept
            queue.task_done()

    async def unsubscribe(
        self, client_guid: str, channel: str = DEFAULT_CHANNEL
    ):
        """Unsubscribe"""
        subscribers = self._channels.get(channel)
        if not subscribers:
            return
        queue = subscribers.pop(client_guid, None)
        if queue is not None:
            await queue.put(None)

    async def terminate(self):
        """Terminate all subscriptions"""
        self._terminating.set()
        for subscribers in self._channels.values():
            for client_guid in subscribers:
                await self.unsubscribe(client_guid)
