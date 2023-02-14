import json
import logging

from dataclasses import dataclass
from threading import Lock
from typing import Optional
from websocket import WebSocketApp
from .event import Event
from .filter import Filters
from .message_pool import MessagePool
from .message_type import RelayMessageType
from .subscription import Subscription

@dataclass
class RelayPolicy:
    should_read: bool = True
    should_write: bool = True
    
    def to_json_object(self) -> dict[str, bool]:
        return { 
            "read": self.should_read, 
            "write": self.should_write
        }



@dataclass
class RelayProxyConnectionConfig:
    host: Optional[str] = None
    port: Optional[int] = None
    type: Optional[str] = None



@dataclass
class Relay:
    url: str
    message_pool: MessagePool
    policy: RelayPolicy = RelayPolicy()
    proxy_config: Optional[RelayProxyConnectionConfig] = None
    ssl_options: Optional[dict] = None

    def __post_init__(self):
        self.subscriptions: dict[str, Subscription] = {}
        self.lock: Lock = Lock()
        self.ws: WebSocketApp = WebSocketApp(
            self.url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )

    def connect(self):
        self.ws.run_forever(
            sslopt=self.ssl_options,
            http_proxy_host=self.proxy_config.host if self.proxy_config is not
            None else None,
            http_proxy_port=self.proxy_config.port if self.proxy_config is not
            None else None,
            proxy_type=self.proxy_config.type if self.proxy_config is not None
            else None,
        )

    def close(self):
        self.ws.close()

    def publish(self, message: str):
        self.ws.send(message)

    def add_subscription(self, id, filters: Filters):
        with self.lock:
            self.subscriptions[id] = Subscription(id, filters)

    def close_subscription(self, id: str) -> None:
        with self.lock:
            self.subscriptions.pop(id, None)

    def update_subscription(self, id: str, filters: Filters) -> None:
        with self.lock:
            subscription = self.subscriptions[id]
            subscription.filters = filters

    def to_json_object(self) -> dict:
        return {
            "url": self.url,
            "policy": self.policy.to_json_object(),
            "subscriptions": [subscription.to_json_object() for subscription in self.subscriptions.values()]
        }

    def _on_open(self, class_obj):
        logging.debug("Relay._on_open: url=%s", self.url)
        pass

    def _on_close(self, class_obj, status_code, message):
        logging.debug("Relay._on_close: url=%s, code=%s, message=%s", self.url,
                      status_code, message)
        pass

    def _on_message(self, class_obj, message: str):
        self.message_pool.add_message(message, self.url)

    def _on_error(self, class_obj, error):
        logging.debug("Relay._on_error: url=%s, error=%s", self.url, error)
        pass

    def _is_valid_message(self, message: str) -> bool:
        message = message.strip("\n")
        if not message or message[0] != '[' or message[-1] != ']':
            return False

        message_json = json.loads(message)
        message_type = message_json[0]
        if not RelayMessageType.is_valid(message_type):
            return False
        if message_type == RelayMessageType.EVENT:
            if not len(message_json) == 3:
                return False

            subscription_id = message_json[1]
            with self.lock:
                if subscription_id not in self.subscriptions:
                    return False

            event = Event.from_dict(message_json[2])
            if not event.verify():
                return False

            with self.lock:
                subscription = self.subscriptions[subscription_id]

            if not subscription.filters.match(event):
                return False

        return True
