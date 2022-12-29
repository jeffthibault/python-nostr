import click
import json
import ssl
import time
import uuid

import nostr
from nostr.key import PrivateKey, PublicKey
from nostr.filter import Filter, Filters
from nostr.event import Event, EventKind
from nostr.relay_manager import RelayManager
from nostr.message_type import ClientMessageType

@click.group()
def command_group():
    """
Python CLI for nostr, enjoy. :)
"""


@click.command()
@click.argument('npub', type=str)
@click.argument('sleep', type=int, default=2)
def receive_messages(npub: str, sleep: int = 2):
    """
    receives messages from npub address
    """
    click.echo(f"npub: {npub}")

    author = PublicKey.from_npub(npub)
    filters = Filters([Filter(authors=[author.hex()], kinds=[EventKind.TEXT_NOTE])])

    subscription_id = uuid.uuid1().hex
    request = [ClientMessageType.REQUEST, subscription_id]
    request.extend(filters.to_json_array())

    relay_manager = RelayManager()
    relay_manager.add_relay("wss://nostr-pub.wellorder.net")
    relay_manager.add_relay("wss://relay.damus.io")
    relay_manager.add_subscription(subscription_id, filters)
    relay_manager.open_connections({"cert_reqs": ssl.CERT_NONE}) # NOTE: This disables ssl certificate verification
    time.sleep(sleep) # allow the connections to open

    message = json.dumps(request)
    relay_manager.publish_message(message)
    time.sleep(sleep) # allow the messages to send

    while relay_manager.message_pool.has_events():
      event_msg = relay_manager.message_pool.get_event()
      print(event_msg.event.content)

    relay_manager.close_connections()


@click.command()
@click.argument('nsec', type=str)
@click.argument('message', type=str)
@click.argument('sleep', type=int, default=2)
def send_message(nsec: str, message: str, sleep: int = 2):
    """
    sends a messages
    """
    relay_manager = RelayManager()
    relay_manager.add_relay("wss://nostr-pub.wellorder.net")
    relay_manager.add_relay("wss://relay.damus.io")
    relay_manager.open_connections({"cert_reqs": ssl.CERT_NONE}) # NOTE: This disables ssl certificate verification
    time.sleep(sleep) # allow the connections to open

    private_key = PrivateKey.from_nsec(nsec)

    event = Event(private_key.public_key.hex(), message)
    event.sign(private_key.hex())

    message = json.dumps([ClientMessageType.EVENT, event.to_json_object()])
    relay_manager.publish_message(message)
    time.sleep(sleep)

    relay_manager.close_connections()


@click.command()
def create_keys():
    """
    creates a private and public key
    """
    private_key = PrivateKey()
    public_key = private_key.public_key
    click.echo(f"Private key: {private_key.bech32()}")
    click.echo(f"Public key: {public_key.bech32()}")


@click.command()
@click.argument('npub', type=str)
def npub_to_hex(npub: str):
    """
    converts npub key to hex
    """
    public_key = PublicKey.from_npub(npub)
    click.echo(f"npub: {public_key.bech32()}")
    click.echo(f"hex: {public_key.hex()}")


@click.command()
def version():
    """ shows version """
    click.echo(nostr.__version__)


def main():
    command_group.add_command(create_keys)
    command_group.add_command(npub_to_hex)
    command_group.add_command(receive_messages)
    command_group.add_command(send_message)
    command_group.add_command(version)
    command_group()


if __name__ == "__main__":
    main()
