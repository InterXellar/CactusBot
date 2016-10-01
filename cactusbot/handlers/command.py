"""Handle commands."""

from ..handler import Handler


class CommandHandler(Handler):
    """Command handler."""

    def on_message(self, packet):
        """Handle message events."""
        self.logger.debug(packet)
        self.logger.info(
            ''.join(chunk["text"] for chunk in packet if chunk["type"] == chunk["text"])
        )

        # user = packet["user"]
        message = ''.join(chunk["text"] for chunk in packet if chunk["type"] == chunk["text"])

        if message.startswith('!') and len(message) > 1:
            command, *args = message.split()
