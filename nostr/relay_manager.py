import threading
from .filter import Filters
from .message_pool import MessagePool
from .relay import Relay, RelayPolicy

class RelayManager:
    def __init__(self) -> None:
        self.relays: dict[str, Relay] = {}
        self.message_pool = MessagePool()

    def add_relay(self, url: str, read: bool, write: bool, subscriptions={}):
        policy = RelayPolicy(read, write)
        relay = Relay(url, policy, self.message_pool, subscriptions)
        self.relays[url] = relay

    def remove_relay(self, url: str):
        self.relays.pop(url)

    def add_subscription(self, id: str, filters: Filters, relay: Relay=None):
        if relay != None:
            relay.add_subscription(id, filters)
        else:
            for relay in self.relays.values():
                relay.add_subscription(id, filters)

    def close_subscription(self, id: str, relay: Relay=None):
        if relay != None:
            relay.close_subscription(id)
        else:
            for relay in self.relays.values():
                relay.close_subscription(id)

    def open_connection(self, relay: Relay=None):
        if relay != None:
            threading.Thread(
                target=relay.connect,
                name=f"{relay.url}-thread"
            ).start()
        else:
            for relay in self.relays.values():
                threading.Thread(
                    target=relay.connect,
                    name=f"{relay.url}-thread"
                ).start()

    def close_connection(self, relay: Relay=None):
        if relay != None:
            relay.close()
        else:
            for relay in self.relays.values():
                relay.close()

    def publish_message(self, message: str, relay: Relay=None):
        if relay != None:
            relay.publish(message)
        else:
            for relay in self.relays.values():
                if relay.policy.should_write:
                    relay.publish(message)
            
