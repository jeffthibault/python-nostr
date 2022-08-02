import threading
from .filter import Filters
from .message_pool import MessagePool
from .relay import Relay, RelayPolicy

class RelayManager:
    def __init__(self) -> None:
        self.relays: list[Relay] = []
        self.message_pool = MessagePool()

    def add_relay(self, url: str, read: bool, write: bool, subscriptions={}):
        policy = RelayPolicy(read, write)
        relay = Relay(url, policy, self.message_pool, subscriptions)
        self.relays.append(relay)

    def add_subscription(self, id: str, filters: Filters):
        for relay in self.relays:
            relay.add_subscription(id, filters)

    def close_subscription(self, id: str):
        for relay in self.relays:
            relay.close_subscription(id)

    def open_connections(self):
        for relay in self.relays:
            threading.Thread(
                target=relay.connect,
                name=f"{relay.url}-thread"
            ).start()

    def close_connections(self):
        for relay in self.relays:
            relay.close()

    def publish_message(self, message: str):
        for relay in self.relays:
            if relay.policy.should_write:
                relay.publish(message)
            
