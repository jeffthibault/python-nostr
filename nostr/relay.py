import json
import time
from dataclasses import dataclass
from queue import Queue
from threading import Lock, Thread
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
        return {"read": self.should_read, "write": self.should_write}



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
    ssl_options: Optional[dict] = None
    proxy_config: RelayProxyConnectionConfig = None
    error_threshold: int = 5

    def __post_init__(self):
        self.outgoing_messages = Queue()
        self.subscriptions: dict[str, Subscription] = {}
        self.num_sent_events: int = 0
        self.error_counter: int = 0
        self.lock: Lock = Lock()
        self.ws: WebSocketApp = WebSocketApp(
            self.url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )
        self._connection_thread: Thread = None

    def connect(self, is_reconnect=False):
        if not self.is_connected():
            with self.lock:
                self._connection_thread = Thread(
                    target=self.ws.run_forever,
                    kwargs={
                        "sslopt": self.ssl_options,
                        "http_proxy_host": self.proxy_config.host if self.proxy_config is not None else None,
                        "http_proxy_port": self.proxy_config.port if self.proxy_config is not None else None,
                        "proxy_type": self.proxy_config.type if self.proxy_config is not None else None
                    },
                    name=f"{self.url}-connection"
                )
                self._connection_thread.start()

            if not is_reconnect:
                Thread(
                    target=self.outgoing_messages_worker,
                    name=f"{self.url}-outgoing-messages-worker",
                    daemon=True
                ).start()

            time.sleep(1)
        
    def close(self):
        if self.is_connected():
            self.ws.close()

    def is_connected(self) -> bool:
        with self.lock:
            if self._connection_thread is None or not self._connection_thread.is_alive():
                return False
            else:
                return True

    def publish(self, message: str):
        self.outgoing_messages.put(message)
        
    def outgoing_messages_worker(self):
        while True:
            if self.is_connected():
                message = self.outgoing_messages.get()
                try:
                    self.ws.send(message)
                    self.num_sent_events += 1
                except:
                    self.outgoing_messages.put(message)

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
            "subscriptions": [
                subscription.to_json_object()
                for subscription in self.subscriptions.values()
            ],
        }

    def _on_open(self, class_obj):
        pass

    def _on_close(self, class_obj, status_code, message):
        self.error_counter = 0

    def _on_message(self, class_obj, message: str):
        self.message_pool.add_message(message, self.url)
    
    def _on_error(self, class_obj, error):
        self.error_counter += 1
        if self.error_counter > self.error_threshold:
            self.close()

    def _is_valid_message(self, message: str) -> bool:
        message = message.strip("\n")
        if not message or message[0] != "[" or message[-1] != "]":
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

            e = message_json[2]
            event = Event(
                e["content"],
                e["pubkey"],
                e["created_at"],
                e["kind"],
                e["tags"],
                e["sig"],
            )
            if not event.verify():
                return False

            with self.lock:
                subscription = self.subscriptions[subscription_id]

            if subscription.filters and not subscription.filters.match(event):
                return False

        return True
