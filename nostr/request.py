import json
from dataclasses import dataclass

from .filter import Filters
from .message_type import ClientMessageType

@dataclass
class Request:
    subscription_id: str
    filters: Filters

    def to_message(self) -> str:
        message = [ClientMessageType.REQUEST, self.subscription_id]
        message.extend(self.filters.to_json_array())
        return json.dumps(message)
