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

    CHAT_EVENTS = {
        "ChatMessage": "message"
    }

    CONSTELLATION_EVENTS = {
        "channel:followed": "follow",
        "channel:subscribed": "subscribe",
        "channel:hosted": "host"
    }

    def __init__(self, channel, handlers):

        self.logger = logging.getLogger(__name__)

        self.api = BeamAPI()
        self.parser = BeamParser()
        self.handlers = handlers  # TODO: move to a more general superclass

        self.channel = channel

        self.chat = None
        self.constellation = None

    async def run(self, *auth):
        """Connect to Beam chat and handle incoming packets."""

        channel = await self.api.get_channel(self.channel)
        self.channel = str(channel["id"])

        user = await self.api.login(*auth)
        chat = await self.api.get_chat(channel["id"])

        self.chat = BeamChat(channel["id"], *chat["endpoints"])
        await self.chat.connect(
            user["id"], partial(self.api.get_chat, channel["id"]))
        asyncio.ensure_future(self.chat.read(self.handle_chat))

        self.constellation = BeamConstellation(channel["id"], user["id"])
        await self.constellation.connect()
        asyncio.ensure_future(
            self.constellation.read(self.handle_constellation))

        await self.handle("start", None)

    async def handle_chat(self, packet):
        """Handle chat packets."""

        data = packet.get("data")
        if data is None:
            return

        event = packet.get("event")

        if event in self.CHAT_EVENTS:
            event = self.CHAT_EVENTS[event]

            if not hasattr(self.parser, "parse_" + event):
                return

            data = getattr(self.parser, "parse_" + event)(data)

            await self.handle(event, data)

    async def handle_constellation(self, packet):
        """Handle constellation packets."""

        if "data" not in packet:
            return
        data = packet["data"]["payload"]

        scope, _, event = packet["data"]["channel"].split(":")
        event = scope + ':' + event

        if event in self.CONSTELLATION_EVENTS:
            event = self.CONSTELLATION_EVENTS[event]

            if not hasattr(self.parser, "parse_" + event):
                return

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
