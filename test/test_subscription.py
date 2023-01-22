import pytest
import json
from nostr.filter import Filter, Filters
from nostr.message_type import ClientMessageType
from nostr.subscription import Subscription


def test_subscription_id():
    """
        check that subscription contents dump to JSON and load
        back to Python with expected types
    """
    filters = Filters([Filter()])
    id = 123
    
    with pytest.raises(TypeError) as e:
        subscription = Subscription(id=id, filters=filters)
    assert "Argument 'id' must be of type str" == str(e)

    subscription = Subscription(id=str(id), filters=filters)
    request = [ClientMessageType.REQUEST, subscription.id]
    request.extend(subscription.filters.to_json_array())
    message = json.dumps(request)
    request_received = json.loads(message)
    message_type, subscription_id, req_filters = request_received
    assert isinstance(subscription_id, str)
    assert message_type == ClientMessageType.REQUEST
    assert isinstance(req_filters, dict)
