from typing import List
import pytest
from nostr.event import Event, EventKind
from nostr.filter import Filter, Filters
from nostr.key import PrivateKey



@pytest.fixture(scope="module", autouse=True)
def pk1() -> PrivateKey:
    print("generated pk1")
    yield PrivateKey()


@pytest.fixture(scope="module", autouse=True)
def pk2() -> PrivateKey:
    yield PrivateKey()


@pytest.fixture(scope="module", autouse=True)
def events(pk1, pk2) -> List[Event]:
    # Note posted by pk1
    event0 = Event(
        public_key=pk1.public_key.hex(),
        content="pk1's first note!"
    )

    # DM sent by pk1 to pk2
    event1 = Event(
        public_key=pk1.public_key.hex(),
        content="Hey pk2, here's a secret",
        tags=[['p', pk2.public_key.hex()]],
        kind=EventKind.ENCRYPTED_DIRECT_MESSAGE,
    )

    # Note posted by pk2
    event2 = Event(
        public_key=pk2.public_key.hex(),
        content="pk2's first note!"
    )

    # Note posted by pk2 in response to pk1's note
    event3 = Event(
        public_key=pk2.public_key.hex(),
        content="Nice to see you here, pk1!",
        tags=[
            ['e', event0.id],
            ['p', pk1.public_key.hex()],
        ],
    )

    # Next response note by pk1 continuing thread with pk2
    event4 = Event(
        public_key=pk1.public_key.hex(),
        content="Thanks! Glad you're here, too, pk2!",
        tags=[
            ['e', event3.id],
            ['p', pk2.public_key.hex()],
        ],
    )

    yield [event0, event1, event2, event3, event4]



class TestFilter:
    def test_match_by_id(self, pk1: PrivateKey, pk2: PrivateKey, events: List[Event]):
        """ should properly match Events by id """
        filter = Filter(
            ids=[events[0].id],
        )
        assert filter.matches(events[0])
        assert filter.matches(events[1]) is False
        assert filter.matches(events[2]) is False
        assert filter.matches(events[3]) is False
        assert filter.matches(events[4]) is False

        # Test multiple Event.id entries
        filter = Filter(
            ids=[events[1].id, events[2].id],
        )
        assert filter.matches(events[0]) is False
        assert filter.matches(events[1])
        assert filter.matches(events[2])
        assert filter.matches(events[3]) is False
        assert filter.matches(events[4]) is False


    def test_match_by_kinds(self, pk1: PrivateKey, pk2: PrivateKey, events: List[Event]):
        """ should properly match Events by kind """
        filter = Filter(
            kinds=[EventKind.TEXT_NOTE],
        )

        # All except pk1's DM should match
        assert filter.matches(events[0])
        assert filter.matches(events[1]) is False
        assert filter.matches(events[2])
        assert filter.matches(events[3])
        assert filter.matches(events[4])

        filter = Filter(
            kinds=[EventKind.TEXT_NOTE, EventKind.ENCRYPTED_DIRECT_MESSAGE],
        )

        # Now everything should match
        assert filter.matches(events[0])
        assert filter.matches(events[1])
        assert filter.matches(events[2])
        assert filter.matches(events[3])
        assert filter.matches(events[4])


    def test_match_by_authors(self, pk1: PrivateKey, pk2: PrivateKey, events: List[Event]):
        """ should properly match Events by kind """
        filter = Filter(
            authors=[pk1.public_key.hex()],
        )

        # Everything sent by pk1 should match
        assert filter.matches(events[0])
        assert filter.matches(events[1])
        assert filter.matches(events[2]) is False
        assert filter.matches(events[3]) is False
        assert filter.matches(events[4])


    def test_match_by_event_refs(self, pk1: PrivateKey, pk2: PrivateKey, events: List[Event]):
        """ should properly match Events by event_ref 'e' tags """
        filter = Filter(
            event_refs=[events[0].id],
        )

        # Only pk2's reply to pk1's event1 should match
        assert filter.matches(events[0]) is False
        assert filter.matches(events[1]) is False
        assert filter.matches(events[2]) is False
        assert filter.matches(events[3])
        assert filter.matches(events[4]) is False


    def test_match_by_pubkey_refs(self, pk1: PrivateKey, pk2: PrivateKey, events: List[Event]):
        """ should properly match Events by pubkey_ref 'p' tags """
        filter = Filter(
            pubkey_refs=[pk2.public_key.hex()],
        )

        # pk1's DM to pk2 and pk1's reply to pk2 should match
        assert filter.matches(events[0]) is False
        assert filter.matches(events[1])
        assert filter.matches(events[2]) is False
        assert filter.matches(events[3]) is False
        assert filter.matches(events[4])
    

    def test_match_by_authors_and_kinds(self, pk1: PrivateKey, pk2: PrivateKey, events: List[Event]):
        """ should properly match Events by authors AND kinds """
        filter = Filter(
            authors=[pk1.public_key.hex()],
            kinds=[EventKind.TEXT_NOTE],
        )

        # Match pk1's notes
        assert filter.matches(events[0])
        assert filter.matches(events[1]) is False
        assert filter.matches(events[2]) is False
        assert filter.matches(events[3]) is False
        assert filter.matches(events[4])

        # Typical search to get all Events sent by a pubkey
        filter = Filter(
            authors=[pk1.public_key.hex()],
            kinds=[EventKind.TEXT_NOTE, EventKind.ENCRYPTED_DIRECT_MESSAGE],
        )

        # Match pk1's notes and sent DMs
        assert filter.matches(events[0])
        assert filter.matches(events[1])
        assert filter.matches(events[2]) is False
        assert filter.matches(events[3]) is False
        assert filter.matches(events[4])


    def test_match_by_kinds_and_pubkey_refs(self, pk1: PrivateKey, pk2: PrivateKey, events: List[Event]):
        """ should properly match Events by kind AND pubkey_ref 'p' tags """
        filter = Filter(
            kinds=[EventKind.TEXT_NOTE],
            pubkey_refs=[pk2.public_key.hex()],
        )

        # Only pk1's reply to pk2 should match
        assert filter.matches(events[0]) is False
        assert filter.matches(events[1]) is False
        assert filter.matches(events[2]) is False
        assert filter.matches(events[3]) is False
        assert filter.matches(events[4])

        # Typical search to get all Events sent to a pubkey
        filter = Filter(
            kinds=[EventKind.TEXT_NOTE, EventKind.ENCRYPTED_DIRECT_MESSAGE],
            pubkey_refs=[pk2.public_key.hex()],
        )

        # pk1's DM to pk2 and pk1's reply to pk2 should match
        assert filter.matches(events[0]) is False
        assert filter.matches(events[1])
        assert filter.matches(events[2]) is False
        assert filter.matches(events[3]) is False
        assert filter.matches(events[4])



class TestFilters:
    def test_match_by_authors_or_pubkey_refs(self, pk1: PrivateKey, pk2: PrivateKey, events: List[Event]):
        """ Should match on authors or pubkey_refs """
        # Typical filters for anything sent by or to a pubkey
        filter1 = Filter(
            authors=[pk1.public_key.hex()],
        )
        filter2 = Filter(
            pubkey_refs=[pk1.public_key.hex()],
        )
        filters = Filters([filter1, filter2])

        assert filters.match(events[0])
        assert filters.match(events[1])
        assert filters.match(events[2]) is False
        assert filters.match(events[3])
        assert filters.match(events[4])
