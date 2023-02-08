from collections import namedtuple
import pytest
import time
from nostr.event import Event, EncryptedDirectMessage, ReportEvent, ReportType
from nostr.exceptions import EventValidationException
from nostr.key import PrivateKey



class TestEvent:
    def test_event_default_time(self):
        """
            ensure created_at default value reflects the time at Event object instantiation
            see: https://github.com/jeffthibault/python-nostr/issues/23
        """
        event1 = Event(content='test event')
        time.sleep(1.5)
        event2 = Event(content='test event')
        assert event1.created_at < event2.created_at
    

    def test_content_only_instantiation(self):
        """ should be able to create an Event by only specifying content without kwarg """
        event = Event("Hello, world!")
        assert event.content is not None


    def test_event_id_recomputes(self):
        """ should recompute the Event.id to reflect the current Event attrs """
        event = Event(content="some event")

        # id should be computed on the fly
        event_id = event.id

        event.created_at += 10

        # Recomputed id should now be different
        assert event.id != event_id
    

    def test_add_event_ref(self):
        """ should add an 'e' tag for each event_ref added """
        some_event_id = "some_event_id"
        event = Event(content="Adding an 'e' tag")
        event.add_event_ref(some_event_id)
        assert ['e', some_event_id] in event.tags


    def test_add_pubkey_ref(self):
        """ should add a 'p' tag for each pubkey_ref added """
        some_pubkey = "some_pubkey"
        event = Event(content="Adding a 'p' tag")
        event.add_pubkey_ref(some_pubkey)
        assert ['p', some_pubkey] in event.tags



class TestEncryptedDirectMessage:
    def setup_class(self):
        self.sender_pk = PrivateKey()
        self.sender_pubkey = self.sender_pk.public_key.hex()
        self.recipient_pk = PrivateKey()
        self.recipient_pubkey = self.recipient_pk.public_key.hex()


    def test_content_field_moved_to_cleartext_content(self):
        """ Should transfer `content` field data to `cleartext_content` """
        dm = EncryptedDirectMessage(content="My message!", recipient_pubkey=self.recipient_pubkey)
        assert dm.content is None
        assert dm.cleartext_content is not None
    

    def test_nokwarg_content_allowed(self):
        """ Should allow creating a new DM w/no `content` nor `cleartext_content` kwarg """
        dm = EncryptedDirectMessage("My message!", recipient_pubkey=self.recipient_pubkey)
        assert dm.cleartext_content is not None
    

    def test_recipient_p_tag(self):
        """ Should generate recipient 'p' tag """
        dm = EncryptedDirectMessage(cleartext_content="Secret message!", recipient_pubkey=self.recipient_pubkey)
        assert ['p', self.recipient_pubkey] in dm.tags

    def test_unencrypted_dm_has_undefined_id(self):
        """ Should raise Exception if `id` is requested before DM is encrypted """
        dm = EncryptedDirectMessage(cleartext_content="My message!", recipient_pubkey=self.recipient_pubkey)

        with pytest.raises(Exception) as e:
            dm.id
        assert "undefined" in str(e)

        # But once we encrypt it, we can request its id
        self.sender_pk.encrypt_dm(dm)
        assert dm.id is not None

class TestReportEvent:
    def test_report_type(self):
        """ Should not let users instantiate a new ReportEvent without valid data"""
        pub_key = PrivateKey().public_key.hex()
        reported_pubkey = PrivateKey().public_key.hex()
        with pytest.raises(EventValidationException) as invalid_type_exception:
            ReportEvent(pub_key, "this was a bad note!", report_type="invalidtype", reported_pubkey=reported_pubkey)
        with pytest.raises(EventValidationException) as no_reported_pubkey:
            ReportEvent(pub_key, report_type=ReportType.NUDITY)
        assert "valid report type" in str(invalid_type_exception)
        assert "user being reported" in str(no_reported_pubkey)

    def test_report_tags(self):
        """ Should generate report-specific tags """
        report = ReportEvent(
            public_key="pubkey",
            reported_pubkey=PrivateKey().public_key.hex(),
            note_id="fakenoteid",
            report_type=ReportType.ILLEGAL,
            victim_pubkey="thevictim"
        )
        assert len(report.tags) == 3
        tag_types = [tag[0] for tag in report.tags]
        print(tag_types)
        assert tag_types == ["e", "p", "p"]
