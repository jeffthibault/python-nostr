import time
import json
from dataclasses import dataclass
from enum import IntEnum
from typing import List
from secp256k1 import PrivateKey, PublicKey
from hashlib import sha256

from nostr.message_type import ClientMessageType



class EventKind(IntEnum):
    SET_METADATA = 0
    TEXT_NOTE = 1
    RECOMMEND_RELAY = 2
    CONTACTS = 3
    ENCRYPTED_DIRECT_MESSAGE = 4
    DELETE = 5



@dataclass
class Event:
    public_key: str
    content: str = None
    created_at: int = None
    kind: int = EventKind.TEXT_NOTE
    tags: List[List[str]] = None
    id: str = None
    signature: str = None


    def __post_init__(self):
        if self.content is not None and not isinstance(self.content, str):
            raise TypeError("Argument 'content' must be of type str")

        if self.created_at is None:
            self.created_at = int(time.time())

        # Can't initialize the nested type above w/out more complex factory, so doing it here
        if self.tags is None:
            self.tags = []

        if self.id is None:
            self.compute_id()


    @staticmethod
    def serialize(public_key: str, created_at: int, kind: int, tags: List[List[str]], content: str) -> bytes:
        data = [0, public_key, created_at, kind, tags, content]
        data_str = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
        return data_str.encode()


    def compute_id(self):
        self.id = sha256(Event.serialize(self.public_key, self.created_at, self.kind, self.tags, self.content)).hexdigest()


    def verify(self) -> bool:
        pub_key = PublicKey(bytes.fromhex("02" + self.public_key), True) # add 02 for schnorr (bip340)

        # Always recompute id just in case something changed
        self.compute_id()

        return pub_key.schnorr_verify(bytes.fromhex(self.id), bytes.fromhex(self.signature), None, raw=True)


    def to_message(self) -> str:
        return json.dumps(
            [
                ClientMessageType.EVENT,
                {
                    "id": self.id,
                    "pubkey": self.public_key,
                    "created_at": self.created_at,
                    "kind": self.kind,
                    "tags": self.tags,
                    "content": self.content,
                    "sig": self.signature
                }
            ]
        )



@dataclass
class EncryptedDirectMessage(Event):
    recipient_pubkey: str = None
    cleartext_content: str = None
    reference_event_id: str = None


    def __post_init__(self):
        if self.content is not None:
            raise Exception("Encrypted DMs cannot use the `content` field; use `cleartext_content` instead.")

        self.kind = EventKind.ENCRYPTED_DIRECT_MESSAGE
        super().__post_init__()

        # Must specify the DM recipient's pubkey hex in a tag
        self.tags.append(['p', self.recipient_pubkey])

        # Optionally specify a reference event (DM) this is a reply to
        if self.reference_event_id:
            self.tags.append(['e', self.reference_event_id])
        
        self.compute_id()
