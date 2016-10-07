from ...packets import MessagePacket

import json
from os import path


class BeamParser:

    ROLES = {
        "Owner": 100,
        "Founder": 91,
        "Staff": 90,
        "Global Mod": 85,
        "Mod": 50,
        "Subscriber": 20,
        "Pro": 5,
        "User": 1,
        "Muted": 0,
        "Banned": -1
    }

    with open(path.join(path.dirname(__file__), "emotes.json")) as file:
        EMOTES = json.load(file)

    @classmethod
    def parse_message(cls, packet):

        message = []
        for component in packet["message"]["message"]:
            chunk = {
                "type": component["type"],
                "data": "",
                "text": component["text"]
            }
            if component["type"] == "emoticon":
                chunk["data"] = cls.EMOTES.get(component["text"], "")
                message.append(chunk)
            elif component["type"] == "link":
                chunk["data"] = component["url"]
                message.append(chunk)
            elif component["type"] == "tag":
                chunk["data"] = component["username"]
                message.append(chunk)
            elif component["text"]:
                chunk["data"] = component["data"]
                message.append(chunk)

        return MessagePacket(
            *message,
            user=packet["user_name"],
            role=cls.ROLES[packet["user_roles"][0]]
        )
