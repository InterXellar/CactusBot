"""Handle data from Beam."""

import asyncio
import logging
from functools import partial

from ...packets import BanPacket, MessagePacket
from .api import BeamAPI
from .chat import BeamChat
from .constellation import BeamConstellation
from .parser import BeamParser


class BeamHandler:
    """Handle data from Beam services."""

    def __init__(self, channel, handlers):

        self.logger = logging.getLogger(__name__)

        self.api = BeamAPI()
        self.parser = BeamParser()
        self.handlers = handlers  # HACK, potentially

        self._channel = channel
        self.channel = ""

        self.chat = None
        self.constellation = None

        self.chat_events = {
            "ChatMessage": "message"
        }

        self.constellation_events = {
            "channel:followed": "follow",
            "channel:subscribed": "subscribe",
            "channel:hosted": "host"
        }

    async def run(self, *auth):
        """Connect to Beam chat and handle incoming packets."""

        channel = await self.api.get_channel(self._channel)
        self.channel = str(channel["id"])
        self.api.channel = self.channel  # HACK

        user = await self.api.login(*auth)
        chat = await self.api.get_chat(channel["id"])

        self.chat = BeamChat(channel["id"], *chat["endpoints"])
        await self.chat.connect(
            user["id"], partial(self.api.get_chat, channel["id"]))
        asyncio.ensure_future(self.chat.read(self.handle_chat))

        asyncio.ensure_future(
            self.run_constellation(channel["id"], user["id"])
        )

        await self.handle("start", None)

    async def run_constellation(self, channel_id, user_id):

        async with BeamConstellation(channel_id, user_id) as constellation:
            await constellation.connect()
            await constellation.read(self.handle_constellation)

    async def handle_chat(self, packet):
        """Handle chat packets."""

        data = packet.get("data")
        if data is None:
            return

        event = packet.get("event")

        if event in self.chat_events:
            event = self.chat_events[event]

            # HACK?
            if hasattr(self.parser, "parse_" + event):
                data = getattr(self.parser, "parse_" + event)(data)

            await self.handle(event, data)

    async def handle_constellation(self, packet):
        """Handle constellation packets."""

        if "data" not in packet:
            return
        data = packet["data"]["payload"]

        scope, _, event = packet["data"]["channel"].split(":")
        event = scope + ':' + event

        if event in self.constellation_events:
            event = self.constellation_events[event]

            # HACK
            if hasattr(self.parser, "parse_" + event):
                data = getattr(self.parser, "parse_" + event)(data)

            await self.handle(event, data)

    async def handle(self, event, data):
        """Handle event."""

        for response in await self.handlers.handle(event, data):
            if isinstance(response, MessagePacket):
                args, kwargs = self.parser.synthesize(response)
                await self.send(*args, **kwargs)

            elif isinstance(response, BanPacket):
                if response.duration:
                    await self.send(
                        response.user,
                        response.duration,
                        method="timeout"
                    )
                else:
                    pass  # TODO: full ban

    async def send(self, *args, **kwargs):
        """Send a packet to Beam."""

        if self.chat is None:
            raise ConnectionError("Chat not initialized.")

        await self.chat.send(*args, **kwargs)
