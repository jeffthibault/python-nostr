from nostr.client.client import NostrClient
from nostr.event import Event
from nostr.key import PublicKey
import asyncio
import threading


async def dm():
    print("This is an example NIP-04 DM flow")
    pk = input("Enter your privatekey to post from (enter nothing for a random one): ")

    def callback(event: Event, decrypted_content):
        """
        Callback to trigger when a DM is received.
        """
        print(
            f"From {event.public_key[:3]}..{event.public_key[-3:]}: {decrypted_content}"
        )

    client = NostrClient(privatekey_hex=pk)
    await asyncio.sleep(1)

    t = threading.Thread(
        target=client.get_dm,
        args=(
            client.public_key,
            callback,
        ),
    )
    t.start()

    to_pubk_hex = (
        input("Enter other pubkey to post to (enter nothing to DM yourself): ")
        or client.public_key.hex()
    )
    print(f"Subscribing to DMs to {to_pubk_hex}")
    while True:
        msg = input("\nEnter message: ")
        client.dm(msg, PublicKey(bytes.fromhex(to_pubk_hex)))


async def post():
    print("This posts and reads a nostr note")
    pk = input("Enter your privatekey to post from (enter nothing for a random one): ")

    def callback(event: Event):
        """
        Callback to trigger when post appers.
        """
        print(f"From {event.public_key[:3]}..{event.public_key[-3:]}: {event.content}")

    sender_client = NostrClient(privatekey_hex=pk)
    await asyncio.sleep(1)

    to_pubk_hex = (
        input("Enter other pubkey (enter nothing to read your own posts): ")
        or sender_client.public_key.hex()
    )
    print(f"Subscribing to posts by {to_pubk_hex}")
    to_pubk = PublicKey(bytes.fromhex(to_pubk_hex))

    t = threading.Thread(
        target=sender_client.get_post,
        args=(
            to_pubk,
            callback,
        ),
    )
    t.start()

    while True:
        msg = input("\nEnter post: ")
        sender_client.post(msg)


# write a DM and receive DMs
asyncio.run(dm())

# make a post and subscribe to posts
# asyncio.run(post())
