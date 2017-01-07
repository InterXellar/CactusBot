"""Config command."""

from .command import Command


class Config(Command):
    """Config command."""

    COMMAND = "config"

    @Command.command()
    async def announce(self, kind, *args):
        """Announce subcommand."""

        if kind.lower() not in ("follow", "subscribe", "host"):
            return "Invalid announcement type: '{kind}'.".format(kind=kind)

        if args[0] == "toggle" and len(args) <= 2:

            if len(args) == 1:

                current_value = (
                    await (
                        await self.api.get_config("announce:" + kind)
                    ).json()
                )["data"]["attributes"]["announce"][kind]["announce"]

                await self.api.update_config(
                    {"announce": {kind: {"announce": not current_value}}})

                return "{kind} announcements are now {pre}abled.".format(
                    kind=kind.title(), pre=('dis', 'en')[not current_value])

            if args[1].lower() in ("on", "enable", "true"):

                await self.api.update_config(
                    {"announce": {kind: {"announce": True}}})

                return "{kind} announcements are now enabled.".format(
                    kind=kind.title())

            elif args[1].lower() in ("off", "disable", "false"):

                await self.api.update_config(
                    {"announce": {kind: {"announce": False}}})

                return "{kind} announcements are now disabled.".format(
                    kind=kind.title())

            else:
                return "Invalid toggle state: '{state}'.".format(state=args[1])

        response = await self.api.update_config(
            {"announce": {kind: {"message": ' '.join(args)}}})

        if response.status == 200:
            return "Updated announcment."

    @Command.command()
    class Spam(Command):
        """Spam configuration command."""

        @Command.command(role="moderator")
        async def urls(self, value):
            """Update URLs spam config."""

            if value in ("on", "allow", "enable", "true"):
                await self.api.update_config({"spam": {"allowUrls": True}})
                return "URLs are now allowed."

            elif value in ("off", "disallow", "disable", "false"):
                await self.api.update_config({"spam": {"allowUrls": False}})
                return "URLs are now disallowed."

            else:
                return "Invalid boolean value: '{value}'.".format(value=value)

        @Command.command()
        async def emoji(self, value: r"\d+"):
            """Update emoji spam config."""

            await self.api.update_config({"spam": {"maxEmoji": int(value)}})

            return "Maximum number of emoji is now {value}.".format(
                value=value)

        @Command.command()
        async def caps(self, value: r"\d+"):
            """Update capitals score spam config."""

            await self.api.update_config(
                {"spam": {"maxCapsScore": int(value)}})

            return "Maximum capitals score is now {value}.".format(
                value=value)
