import time
import json
from enum import IntEnum
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


class Event():
    def __init__(
            self, 
            public_key: str, 
            content: str, 
            created_at: int = None, 
            kind: int=EventKind.TEXT_NOTE, 
            tags: "list[list[str]]"=[], 
            id: str=None, 
            signature: str=None) -> None:
        if not isinstance(content, str):
            raise TypeError("Argument 'content' must be of type str")

        self.public_key = public_key
        self.content = content
        self.created_at = created_at or int(time.time())
        self.kind = kind
        self.tags = tags
        self.signature = signature
        self.id = id or Event.compute_id(self.public_key, self.created_at, self.kind, self.tags, self.content)

    @staticmethod
    def serialize(public_key: str, created_at: int, kind: int, tags: "list[list[str]]", content: str) -> bytes:
        data = [0, public_key, created_at, kind, tags, content]
        data_str = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
        return data_str.encode()

    @staticmethod
    def compute_id(public_key: str, created_at: int, kind: int, tags: "list[list[str]]", content: str) -> str:
        return sha256(Event.serialize(public_key, created_at, kind, tags, content)).hexdigest()

    def verify(self) -> bool:
        pub_key = PublicKey(bytes.fromhex("02" + self.public_key), True) # add 02 for schnorr (bip340)
        event_id = Event.compute_id(self.public_key, self.created_at, self.kind, self.tags, self.content)
        return pub_key.schnorr_verify(bytes.fromhex(event_id), bytes.fromhex(self.signature), None, raw=True)

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
