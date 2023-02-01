from typing import *
import ssl
import time
import json
import os
import base64

from ..event import Event
from ..relay_manager import RelayManager
from ..message_type import ClientMessageType
from ..key import PrivateKey, PublicKey

from ..filter import Filter, Filters
from ..event import Event, EventKind
from ..relay_manager import RelayManager
from ..message_type import ClientMessageType

# from aes import AESCipher
from . import cbc


class NostrClient:
    relays = [
        "wss://relay.snort.social",
        "wss://nostr-pub.wellorder.net",
        "wss://nostr.zebedee.cloud",
        "wss://nostr.mom",
        # "wss://wss://lnbits.link/nostrrelay/client"
        # "wss://no.str.cr",
    ]  # ["wss://nostr.oxtr.dev"]  # ["wss://relay.nostr.info"] "wss://nostr-pub.wellorder.net"  "ws://91.237.88.218:2700", "wss://nostrrr.bublina.eu.org", ""wss://nostr-relay.freeberty.net"", , "wss://nostr.oxtr.dev", "wss://relay.nostr.info", "wss://nostr-pub.wellorder.net" , "wss://relayer.fiatjaf.com", "wss://nodestr.fmt.wiz.biz/", "wss://no.str.cr"
    relay_manager = RelayManager()
    private_key: PrivateKey
    public_key: PublicKey

    def __init__(self, privatekey_hex: str = "", relays: List[str] = [], connect=True):
        self.generate_keys(privatekey_hex)

        if len(relays):
            self.relays = relays

        if connect:
            for relay in self.relays:
                self.relay_manager.add_relay(relay)
            self.relay_manager.open_connections(
                {"cert_reqs": ssl.CERT_NONE}
            )  # NOTE: This disables ssl certificate verification

    def close(self):
        self.relay_manager.close_connections()

    def generate_keys(self, privatekey_hex: str = None):
        pk = bytes.fromhex(privatekey_hex) if privatekey_hex else None
        self.private_key = PrivateKey(pk)
        self.public_key = self.private_key.public_key

    def post(self, message: str):
        event = Event(self.public_key.hex(), message, kind=EventKind.TEXT_NOTE)
        event.sign(self.private_key.hex())
        message = json.dumps([ClientMessageType.EVENT, event.to_json_object()])
        self.relay_manager.publish_message(message)

    def get_post(
        self, sender_publickey: PublicKey = None, callback_func=None, filter_kwargs={}
    ):
        filter = Filter(
            authors=[sender_publickey.hex()] if sender_publickey else None,
            kinds=[EventKind.TEXT_NOTE],
            **filter_kwargs,
        )
        filters = Filters([filter])
        subscription_id = os.urandom(4).hex()
        self.relay_manager.add_subscription(subscription_id, filters)

        request = [ClientMessageType.REQUEST, subscription_id]
        request.extend(filters.to_json_array())
        message = json.dumps(request)
        self.relay_manager.publish_message(message)

        while True:
            while self.relay_manager.message_pool.has_events():
                event_msg = self.relay_manager.message_pool.get_event()
                print(event_msg.event.content)
                if callback_func:
                    callback_func(event_msg.event)
            time.sleep(0.1)

    def dm(self, message: str, to_pubkey: PublicKey):
        shared_secret = self.private_key.compute_shared_secret(to_pubkey.hex())
        aes = cbc.AESCipher(key=shared_secret)
        iv, enc_text = aes.encrypt(message)
        content = f"{base64.b64encode(enc_text).decode('utf-8')}?iv={base64.b64encode(iv).decode('utf-8')}"

        event = Event(
            self.public_key.hex(),
            content,
            tags=[["p", to_pubkey.hex()]],
            kind=EventKind.ENCRYPTED_DIRECT_MESSAGE,
        )
        event.sign(self.private_key.hex())
        event_message = json.dumps([ClientMessageType.EVENT, event.to_json_object()])
        self.relay_manager.publish_message(event_message)

    def get_dm(self, sender_publickey: PublicKey, callback_func=None, filter_kwargs={}):
        filter = Filter(
            kinds=[EventKind.ENCRYPTED_DIRECT_MESSAGE],
            tags={"#p": [sender_publickey.hex()]},
            **filter_kwargs,
        )
        filters = Filters([filter])
        subscription_id = os.urandom(4).hex()
        self.relay_manager.add_subscription(subscription_id, filters)

        request = [ClientMessageType.REQUEST, subscription_id]
        request.extend(filters.to_json_array())
        message = json.dumps(request)
        self.relay_manager.publish_message(message)

        while True:
            while self.relay_manager.message_pool.has_events():
                event_msg = self.relay_manager.message_pool.get_event()
                if "?iv=" in event_msg.event.content:
                    try:
                        shared_secret = self.private_key.compute_shared_secret(
                            event_msg.event.public_key
                        )
                        aes = cbc.AESCipher(key=shared_secret)
                        enc_text_b64, iv_b64 = event_msg.event.content.split("?iv=")
                        iv = base64.decodebytes(iv_b64.encode("utf-8"))
                        enc_text = base64.decodebytes(enc_text_b64.encode("utf-8"))
                        dec_text = aes.decrypt(iv, enc_text)
                        if callback_func:
                            callback_func(event_msg.event, dec_text)
                    except:
                        pass
                break
            time.sleep(0.1)

    async def subscribe(self):
        while True:
            while self.relay_manager.message_pool.has_events():
                event_msg = self.relay_manager.message_pool.get_event()
                print(event_msg.event.content)
                break
            time.sleep(0.1)
