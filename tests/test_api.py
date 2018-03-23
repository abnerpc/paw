import pytest
from restless.exceptions import BadRequest

from pawapp.api import CallEventResource


def test_callevent_create_without_data():
    resource = CallEventResource()
    with pytest.raises(BadRequest):
        resource.create()


def test_call_event_create_with_bad_data():
    resource = CallEventResource()
    resource.data = {'wrong_field': 1}

    with pytest.raises(BadRequest) as bad_request:
        resource.create()

    assert bad_request
