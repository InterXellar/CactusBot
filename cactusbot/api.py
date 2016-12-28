"""Interact with CactusAPI."""

import json

from .services.api import API


class CactusAPI(API):
    """Interact with CactusAPI."""

    URL = "https://cactus.exoz.one/api/v1/"

    def __init__(self, channel, **kwargs):
        super().__init__(**kwargs)

        self.channel = channel

    async def request(self, method, endpoints, is_json=True, **kwargs):
        """Send HTTP request to endpoint."""

        if is_json:
            if "headers" in kwargs:
                kwargs["headers"]["Content-Type"] = "application/json"
            else:
                kwargs["headers"] = {"Content-Type": "application/json"}

        return await super().request(method, endpoints, **kwargs)

    async def get_command(self, name=None):
        """Get a command."""

        if name is not None:
            return await self.get(
                "/user/{channel}/command/{command}".format(
                    channel=self.channel, command=name))
        return await self.get("/user/{channel}/command".format(
            channel=self.channel))

    async def add_command(self, name, response, *, user_level=0):
        """Add a command."""

        data = {
            "response": response,
            "userLevel": user_level  # TODO
        }

        return await self.patch(
            "/user/{channel}/command/{command}".format(
                channel=self.channel, command=name),
            data=json.dumps(data)
        )

    async def remove_command(self, name):
        """Remove a command."""

        return await self.delete("/user/{channel}/command/{command}".format(
            channel=self.channel, command=name))

    async def get_command_alias(self, command):
        """Get a command alias."""
        return await self.get("/user/{channel}/alias/{command}".format(
            channel=self.channel, command=command))

    async def add_alias(self, command, alias, args):
        """Create a command alias."""

        data = {
            "command": command,
            "arguments": args["message"]
        }

        return await self.patch("/user/{user}/alias/{alias}".format(
            user=self.channel, alias=alias), data=json.dumps(data))

    async def remove_alias(self, alias):
        """Remove a command alias."""

        return await self.delete("/user/{user}/alias/{alias}".format(
            user=self.channel, alias=alias))

    async def toggle_command(self, command, status):
        """Toggle the availability of a command."""

        data = {"enabled": status}

        return await self.patch("/user/{channel}/command/{command}".format(
            channel=self.channel, command=command), data=json.dumps(data))

    async def update_command_count(self, command, action):
        """Set the count of a command."""

        data = {"count": action}

        return await(
            self.patch("/user/{channel}/command/{command}/count".format(
                channel=self.channel, command=command), data=json.dumps(data)))

    async def get_quote(self, quote_id=None):
        """Get a quote."""

        if quote_id is not None:
            return await self.get("/user/{channel}/quote/{id}".format(
                channel=self.channel, id=quote_id))
        return await self.get("/user/{channel}/quote".format(
            channel=self.channel), params={"random": True})

    async def add_quote(self, quote):
        """Add a quote."""

        data = {"quote": quote}

        return await self.post(
            "/user/{channel}/quote".format(channel=self.channel),
            data=json.dumps(data)
        )

    async def edit_quote(self, quote_id, quote):
        """Edit a quote."""

        data = {"quote": quote}

        return await self.patch(
            "/user/{channel}/quote/{quote_id}".format(
                channel=self.channel, quote_id=quote_id),
            data=json.dumps(data)
        )

    async def remove_quote(self, quote_id):
        """Remove a quote."""

        return await self.delete("/user/{channel}/quote/{id}".format(
            channel=self.channel, id=quote_id))

    async def get_friend(self, name=None):
        """Get a list of friends."""

        if name is None:
            return await self.get("/channel/{channel}/friend")

        return await self.get("/channel/{channel}/friend/{name}".format(
            channel=self.channel, name=name))

    async def add_friend(self, username):
        """Add a friend."""

        return await self.patch("/channel/{channel}/friend/{name}".format(
            channel=self.channel, name=username))

    async def remove_friend(self, username):
        """Remove a friend."""

        return await self.delete("/channel/{channel}/friend/{name}".format(
            channel=self.channel, name=username))

    async def get_config(self, *keys):
        """Get the channel config."""

        if keys:
            return await self.get("/user/{channel}/config".format(
                channel=self.channel), data=json.dumps({"keys": keys}))

        return await self.get("/user/{channel}/config".format(
            channel=self.channel), is_json=False)

    async def update_config(self, value):
        """Update config attributes."""

        return await self.patch("/user/{user}/config".format(
            user=self.channel), data=json.dumps(value))

    async def add_repeat(self, command, period, *args):
        """Add a repeat."""

        data = {
            "command": command,
            "period": int(period),
            "arguments": args
        }

        return await self.post("/user/{user}/repeat".format(user=self.channel),
                               data=json.dumps(data))

    async def remove_repeat(self, repeat):
        """Remove a repeat."""

        return await self.delete("/user/{user}/repeat/{repeat}".format(
            user=self.channel, repeat=repeat))

    async def get_repeats(self):
        """Get all repeats."""

        return await self.get("/user/{user}/repeat")

    async def add_social(self, service, url):
        """Add a social service."""

        data = {"url": url}

        return await self.patch("/user/{user}/social/{service}".format(
            user=self.channel, service=service), data=json.dumps(data))

    async def remove_social(self, service):
        """Remove a social service."""

        return await self.delete("/user/{user}/social/{service}".format(
            user=self.channel, service=service))

    async def get_social(self, service=None):
        """Get social service."""

        if service is None:
            return await self.get("/user/{user}/social".format(
                user=self.channel))
        return await self.get("/user/{user}/social/{service}".format(
            user=self.channel, service=service))
