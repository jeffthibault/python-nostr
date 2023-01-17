import time
import json
from dataclasses import dataclass
from enum import IntEnum
from typing import List
from secp256k1 import PrivateKey, PublicKey
from hashlib import sha256

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
    content: str = ""
    created_at: int = int(time.time())
    kind: int = EventKind.TEXT_NOTE
    tags: List[List[str]] = None
    id: str = None
    signature: str = None


    def __post_init__(self):
        if self.tags is None:
            self.tags = []


    @staticmethod
    def serialize(public_key: str, created_at: int, kind: int, tags: "list[list[str]]", content: str) -> bytes:
        data = [0, public_key, created_at, kind, tags, content]
        data_str = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
        return data_str.encode()


    def compute_id(self):
        self.id = sha256(Event.serialize(self.public_key, self.created_at, self.kind, self.tags, self.content)).hexdigest()


    def sign(self, private_key_hex: str) -> None:
        if self.id is None:
            self.compute_id()
            # self.id = Event.compute_id(self.public_key, self.created_at, self.kind, self.tags, self.content)
        sk = PrivateKey(bytes.fromhex(private_key_hex))
        sig = sk.schnorr_sign(bytes.fromhex(self.id), None, raw=True)
        self.signature = sig.hex()


    def verify(self) -> bool:
        pub_key = PublicKey(bytes.fromhex("02" + self.public_key), True) # add 02 for schnorr (bip340)
        self.compute_id()
        return pub_key.schnorr_verify(bytes.fromhex(self.id), bytes.fromhex(self.signature), None, raw=True)


    def to_json_object(self) -> dict:
        return {
            "id": self.id,
            "pubkey": self.public_key,
            "created_at": self.created_at,
            "kind": self.kind,
            "tags": self.tags,
            "content": self.content,
            "sig": self.signature
        }



@dataclass
class EncryptedDirectMessage(Event):
    recipient_pubkey: str = None
    cleartext_message: str = None
    reference_event_id: str = None

    def __post_init__(self):
        self.kind = EventKind.ENCRYPTED_DIRECT_MESSAGE
        super().__post_init__()

        # Must specify the DM recipient's pubkey hex
        self.tags.append(['p', self.recipient_pubkey])

        # Optionally specify a reference event (DM) this is a reply to
        if self.reference_event_id:
            self.tags.append(['m', self.reference_event_id])
