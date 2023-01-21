from typing import List
import pytest
from nostr.event import Event, EventKind
from nostr.filter import Filter, Filters
from nostr.key import PrivateKey



class TestFilter:
    def setup_class(self):
        self.pk1 = PrivateKey()
        self.pk2 = PrivateKey()

        """ pk1 kicks off a thread and interacts with pk2 """
        self.pk1_thread = [
            # Note posted by pk1
            Event(
                public_key=self.pk1.public_key.hex(),
                content="pk1's first note!"
            ),
        ]
        self.pk1_thread.append(
            # Note posted by pk2 in response to pk1's note
            Event(
                public_key=self.pk2.public_key.hex(),
                content="Nice to see you here, pk1!",
                tags=[
                    ['e', self.pk1_thread[0].id],      # Replies reference which note they're directly responding to
                    ['p', self.pk1.public_key.hex()],  # Replies reference who they're responding to
                ],
            )
        )
        self.pk1_thread.append(
            # Next response note by pk1 continuing thread with pk2
            Event(
                public_key=self.pk1.public_key.hex(),
                content="Thanks! Glad you're here, too, pk2!",
                tags=[
                    ['e', self.pk1_thread[0].id],      # Threads reference the original note
                    ['e', self.pk1_thread[-1].id],     # Replies reference which note they're directly responding to
                    ['p', self.pk2.public_key.hex()],  # Replies reference who they're responding to
                ],
            )
        )

        """ pk2 starts a new thread but no one responds """
        self.pk2_thread = [
            # Note posted by pk2
            Event(
                public_key=self.pk2.public_key.hex(),
                content="pk2's first note!"
            )
        ]
        self.pk2_thread.append(
            # pk2's self-reply
            Event(
                public_key=self.pk2.public_key.hex(),
                content="So... I guess no one's following me.",
                tags=[
                    ['e', self.pk2_thread[0].id]
                ]
            )
        )

        """ pk1 DMs pk2 """
        self.pk1_pk2_dms = [
            # DM sent by pk1 to pk2
            Event(
                public_key=self.pk1.public_key.hex(),
                content="Hey pk2, here's a secret",
                tags=[['p', self.pk2.public_key.hex()]],
                kind=EventKind.ENCRYPTED_DIRECT_MESSAGE,
            ),
            Event(
                public_key=self.pk2.public_key.hex(),
                content="Thanks! I'll keep it secure.",
                tags=[['p', self.pk1.public_key.hex()]],
                kind=EventKind.ENCRYPTED_DIRECT_MESSAGE,
            )
        ]


    def test_match_by_event_id(self):
        """ should match Events by event_id """
        filter = Filter(
            event_ids=[self.pk1_thread[0].id],
        )
        assert filter.matches(self.pk1_thread[0])

        # None of the others should match
        for event in self.pk1_thread[1:] + self.pk2_thread + self.pk1_pk2_dms[1:]:
            assert filter.matches(event) is False


    def test_multiple_values_in_same_tag(self):
        """ should treat multiple tag values as OR searches """
        filter = Filter(
            event_ids=[self.pk1_thread[0].id, self.pk1_pk2_dms[0].id, "some_other_event_id"],
        )
        assert filter.matches(self.pk1_thread[0])
        assert filter.matches(self.pk1_pk2_dms[0])

        # None of the others should match
        for event in self.pk1_thread[1:] + self.pk2_thread + self.pk1_pk2_dms[1:]:
            assert filter.matches(event) is False


    def test_match_by_kinds(self):
        """ should match Events by kind """
        filter = Filter(
            kinds=[EventKind.TEXT_NOTE],
        )

        # Both threads should match
        for event in self.pk1_thread + self.pk2_thread:
            assert filter.matches(event)
        
        # DMs should not match
        for event in self.pk1_pk2_dms:
            assert filter.matches(event) is False

        # Now allow either kind
        filter = Filter(
            kinds=[EventKind.TEXT_NOTE, EventKind.ENCRYPTED_DIRECT_MESSAGE],
        )

        # Now everything should match
        for event in self.pk1_thread + self.pk2_thread + self.pk1_pk2_dms:
            assert filter.matches(event)


    def test_match_by_authors(self):
        """ should match Events by author """
        filter = Filter(authors=[self.pk1.public_key.hex()])

        # Everything sent by pk1 should match
        for event in [event for event in (self.pk1_thread + self.pk2_thread + self.pk1_pk2_dms) if event.public_key == self.pk1.public_key.hex()]:
            assert filter.matches(event)
        
        # None of pk2's should match
        for event in [event for event in (self.pk1_thread + self.pk2_thread + self.pk1_pk2_dms) if event.public_key == self.pk2.public_key.hex()]:
            assert filter.matches(event) is False


    def test_match_by_event_refs(self):
        """ should match Events by event_ref 'e' tags """
        filter = Filter(
            event_refs=[self.pk1_thread[0].id],
        )

        # All replies to pk1's initial note should match (even pk1's reply at the end)
        assert filter.matches(self.pk1_thread[1])
        assert filter.matches(self.pk1_thread[2])

        # Everything else should not match
        for event in [self.pk1_thread[0]] + self.pk2_thread + self.pk1_pk2_dms:
            assert filter.matches(event) is False


    def test_match_by_pubkey_refs(self):
        """ should match Events by pubkey_ref 'p' tags """
        filter = Filter(
            pubkey_refs=[self.pk1_thread[0].public_key],
        )

        # pk2's reply in pk1's thread should match
        assert filter.matches(self.pk1_thread[1])

        # pk2's DM reply to pk1 should match
        assert filter.matches(self.pk1_pk2_dms[1])

        # Everything else should not match
        for event in [self.pk1_thread[0], self.pk1_thread[2]] + self.pk2_thread + [self.pk1_pk2_dms[0]]:
            assert filter.matches(event) is False


    def test_match_by_arbitrary_single_letter_tag(self):
        """ should match NIP-12 arbitrary single-letter tags """
        filter = Filter()
        filter.add_arbitrary_tag('x', ["oranges"])

        # None of our Events match
        for event in self.pk1_thread + self.pk2_thread + self.pk1_pk2_dms:
            assert filter.matches(event) is False

        # A new Event that has the target tag but the wrong value should not match
        event = Event(
            public_key=self.pk1.public_key.hex(),
            content="Additional event to test with",
            tags=[
                ['x', "bananas"]
            ]
        )
        assert filter.matches(event) is False

        # But a new Event that includes the target should match
        event = Event(
            public_key=self.pk1.public_key.hex(),
            content="Additional event to test with",
            tags=[
                ['x', "oranges"]
            ]
        )
        assert filter.matches(event)

        # Filter shouldn't care if there are other extraneous values
        event.tags.append(['x', "pizza"])
        assert filter.matches(event)

        event.tags.append(['y', "honey badger"])
        assert filter.matches(event)


    def test_match_by_arbitrary_multi_letter_tag(self):
        """ should match any arbitrary multi-letter tag """
        filter = Filter()
        filter.add_arbitrary_tag('favorites', ["bitcoin"])

        # None of our Events match
        for event in self.pk1_thread + self.pk2_thread + self.pk1_pk2_dms:
            assert filter.matches(event) is False

        # A new Event that has the target tag but the wrong value should not match
        event = Event(
            public_key=self.pk1.public_key.hex(),
            content="Additional event to test with",
            tags=[
                ['favorites', "shitcoin"]
            ]
        )
        assert filter.matches(event) is False

        # But a new Event that includes the target should match
        event = Event(
            public_key=self.pk1.public_key.hex(),
            content="Additional event to test with",
            tags=[
                ['favorites', "bitcoin"]
            ]
        )
        assert filter.matches(event)

        # Filter shouldn't care if there are other extraneous values
        event.tags.append(['favorites', "sats"])
        assert filter.matches(event)

        event.tags.append(['foo', "bar"])
        assert filter.matches(event)


    def test_match_by_delegation_tag(self):
        """
            should match on delegation tag.
            Note: this is to demonstrate that it works w/out special handling, but 
            arguably Delegation filtering should have its own explicit Filter support.
        """
        filter = Filter()

        # Search just for the delegator's pubkey (only aspect of delegation search that is supported this way)
        filter.add_arbitrary_tag(
            'delegation', ["8e0d3d3eb2881ec137a11debe736a9086715a8c8beeeda615780064d68bc25dd"]
        )

        # None of our Events match
        for event in self.pk1_thread + self.pk2_thread + self.pk1_pk2_dms:
            assert filter.matches(event) is False

        # A new Event that has the target tag but the wrong value should not match
        event = Event(
            public_key=self.pk1.public_key.hex(),
            content="Additional event to test with",
            tags=[
                [
                    'delegation',
                    "some_other_delegators_pubkey",
                    "kind=1&created_at<1675721813",
                    "cbc49c65fe04a3181d72fb5a9f1c627e329d5f45d300a2dfed1c3e788b7834dad48a6d27d8e244af39c77381334ede97d4fd15abe80f35fda695fd9bd732aa1e"
                ]
            ]
        )
        assert filter.matches(event) is False

        # But a new Event that includes the target should match
        event = Event(
            public_key=self.pk1.public_key.hex(),
            content="Additional event to test with",
            tags=[
                [
                    'delegation',
                    "8e0d3d3eb2881ec137a11debe736a9086715a8c8beeeda615780064d68bc25dd",
                    "kind=1&created_at<1675721813",
                    "cbc49c65fe04a3181d72fb5a9f1c627e329d5f45d300a2dfed1c3e788b7834dad48a6d27d8e244af39c77381334ede97d4fd15abe80f35fda695fd9bd732aa1e"
                ]
            ]
        )
        assert filter.matches(event)

        # Filter shouldn't care if there are other extraneous values
        event.tags.append(['favorites', "sats"])
        assert filter.matches(event)

        event.tags.append(['foo', "bar"])
        assert filter.matches(event)


    def test_match_by_authors_and_kinds(self):
        """ should match Events by authors AND kinds """
        filter = Filter(
            authors=[self.pk1.public_key.hex()],
            kinds=[EventKind.TEXT_NOTE],
        )

        # Should match pk1's notes but not pk2's reply
        assert filter.matches(self.pk1_thread[0])
        assert filter.matches(self.pk1_thread[1]) is False
        assert filter.matches(self.pk1_thread[2])

        # Should not match anything else
        for event in self.pk2_thread + self.pk1_pk2_dms:
            assert filter.matches(event) is False

        # Typical search to get all Events sent by a pubkey
        filter = Filter(
            authors=[self.pk1.public_key.hex()],
            kinds=[EventKind.TEXT_NOTE, EventKind.ENCRYPTED_DIRECT_MESSAGE],
        )

        # Should still match pk1's notes but not pk2's reply
        assert filter.matches(self.pk1_thread[0])
        assert filter.matches(self.pk1_thread[1]) is False
        assert filter.matches(self.pk1_thread[2])

        # Should not match any of pk2's solo thread
        assert filter.matches(self.pk2_thread[0]) is False
        assert filter.matches(self.pk2_thread[1]) is False

        # Should match pk1's DM but not pk2's DM reply
        assert filter.matches(self.pk1_pk2_dms[0])
        assert filter.matches(self.pk1_pk2_dms[1]) is False


    def test_match_by_kinds_and_pubkey_refs(self):
        """ should match Events by kind AND pubkey_ref 'p' tags """
        filter = Filter(
            kinds=[EventKind.TEXT_NOTE],
            pubkey_refs=[self.pk2.public_key.hex()],
        )

        # Only pk1's reply to pk2 should match
        assert filter.matches(self.pk1_thread[2])

        # Should not match anything else
        for event in self.pk1_thread[:1] + self.pk2_thread + self.pk1_pk2_dms:
            assert filter.matches(event) is False

        # Typical search to get all Events sent to a pubkey
        filter = Filter(
            kinds=[EventKind.TEXT_NOTE, EventKind.ENCRYPTED_DIRECT_MESSAGE],
            pubkey_refs=[self.pk2.public_key.hex()],
        )

        # pk1's reply to pk2 should match
        assert filter.matches(self.pk1_thread[2])

        # pk2's DM to pk1 should match
        assert filter.matches(self.pk1_pk2_dms[0])

        # Should not match anything else
        for event in self.pk1_thread[:1] + self.pk2_thread + self.pk1_pk2_dms[1:]:
            assert filter.matches(event) is False


    def test_event_refs_json(self):
        """ should insert event_refs as "#e" in json """
        filter = Filter(event_refs=["some_event_id"])
        assert "#e" in filter.to_json_object().keys()
        assert "e" not in filter.to_json_object().keys()


    def test_pubkey_refs_json(self):
        """ should insert pubkey_refs as "#p" in json """
        filter = Filter(pubkey_refs=["some_pubkey"])
        assert "#p" in filter.to_json_object().keys()
        assert "p" not in filter.to_json_object().keys()


    def test_arbitrary_single_letter_json(self):
        """ should prefix NIP-12 arbitrary single-letter tags with "#" in json """
        filter = Filter()
        filter.add_arbitrary_tag('x', ["oranges"])
        assert "#x" in filter.to_json_object().keys()
        assert "x" not in filter.to_json_object().keys()


    def test_arbitrary_multi_letter_json(self):
        """ should include arbitrary multi-letter tags as-is in json """
        filter = Filter()
        filter.add_arbitrary_tag('foo', ["bar"])
        assert "foo" in filter.to_json_object().keys()



# Inherit from TestFilter to get all the same test data
class TestFilters(TestFilter):

    def test_match_by_authors_or_pubkey_refs(self):
        """ Should match on authors or pubkey_refs """
        # Typical filters for anything sent by or to a pubkey
        filter1 = Filter(
            authors=[self.pk1.public_key.hex()],
        )
        filter2 = Filter(
            pubkey_refs=[self.pk1.public_key.hex()],
        )
        filters = Filters([filter1, filter2])

        # Should match the entire pk1 thread and the DM exchange
        for event in self.pk1_thread + self.pk1_pk2_dms:
            assert filters.match(event)
        
        # Should not match anything in pk2's solo thread
        assert filters.match(self.pk2_thread[0]) is False
        assert filters.match(self.pk2_thread[1]) is False
