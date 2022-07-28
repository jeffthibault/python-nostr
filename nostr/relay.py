import json
import ssl
from typing import Union
from websocket import WebSocket, WebSocketConnectionClosedException, WebSocketTimeoutException
from .event import Event
from .filter import Filters
from .message_type import RelayMessageType
from .subscription import Subscription

class RelayPolicy:
    def __init__(self, should_read: bool=True, should_write: bool=True) -> None:
        self.should_read = should_read
        self.should_write = should_write

    def to_json_object(self) -> dict[str, bool]:
        return { 
            "read": self.should_read, 
            "write": self.should_write
        }

class Relay:
    def __init__(
            self, 
            url: str, 
            policy: RelayPolicy,
            ws: WebSocket=WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE}),
            subscriptions: dict[str, Subscription]={}) -> None:
        self.url = url
        self.policy = policy
        self.ws = ws
        self.subscriptions = subscriptions

    def open_websocket_connection(self, timeout: int=None) -> None:
        if timeout != None:
            self.ws.connect(self.url, timeout=timeout)
        else:
            self.ws.connect(self.url)

    def close_websocket_connection(self) -> None:
        self.ws.close()

    def add_subscription(self, id: str, filters: Filters) -> None:
        self.subscriptions[id] = Subscription(id, filters)

    def close_subscription(self, id: str) -> None:
        self.subscriptions.pop(id)

    def update_subscription(self, id: str, filters: Filters) -> None:
        subscription = self.subscriptions[id]
        subscription.filters = filters

    def publish_message(self, message: str) -> None:
        self.ws.send(message)

    def get_message(self) -> Union[None, str]:
        while True:
            try:
                message = self.ws.recv()
                if not self._is_valid_message(message):
                    continue
                
                return message
                
            except WebSocketConnectionClosedException:
                print('received connection closed')
                break
            except WebSocketTimeoutException:
                print('ws connection timed out')
                break

        return None

    def to_json_object(self) -> dict:
        return {
            "url": self.url,
            "policy": self.policy.to_json_object(),
            "subscriptions": [subscription.to_json_object() for subscription in self.subscriptions.values()]
        }

    def _is_valid_message(self, message: str) -> bool:
        if not message or message[0] != '[' or message[-1] != ']':
            return False

        message_json = json.loads(message)
        message_type = message_json[0]
        if message_type == RelayMessageType.NOTICE:
            return True
        if message_type == RelayMessageType.END_OF_STORED_EVENTS:
            return True
        if message_type == RelayMessageType.EVENT:
            if not len(message_json) == 3:
                return False
            
            subscription_id = message_json[1]
            if subscription_id not in self.subscriptions:
                return False

            e = message_json[2]
            event = Event(e['pubkey'], e['content'], e['created_at'], e['kind'], e['tags'], e['id'], e['sig'])
            if not event.verify():
                return False

            if not self.subscriptions[subscription_id].filters.match(event):
                return False

            return True
