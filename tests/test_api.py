import pytest
from unittest.mock import patch
from restless.exceptions import BadRequest

from pawapp.exceptions import InvalidDataException
from pawapp.api import CallEventResource


def test_callevent_create_without_data():
    resource = CallEventResource()
    with pytest.raises(BadRequest):
        resource.create()


@patch('pawapp.api.callevent_handler')
def test_call_event_create_with_bad_data(callevent_handler):
    resource = CallEventResource()
    resource.data = {'wrong_field': 1}

    def side_effect(arg):
        raise InvalidDataException({})

    callevent_handler.side_effect = side_effect
    with pytest.raises(BadRequest) as bad_request:
        resource.create()

    assert bad_request
