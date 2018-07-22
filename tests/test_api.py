import pytest
from unittest.mock import patch, Mock
from restless.exceptions import BadRequest

from pawapp.exceptions import InvalidDataException
from pawapp.api import CallEventResource, BillResource


def test_callevent_create_without_data():
    """Test endpoint call without data"""
    resource = CallEventResource()
    with pytest.raises(BadRequest):
        resource.create()


@patch('pawapp.api.callevent_handler')
def test_call_event_create_with_bad_data(callevent_handler):
    """Test endpoint call with bad data"""
    resource = CallEventResource()
    resource.data = {'wrong_field': 1}

    def side_effect(arg):
        raise InvalidDataException({})

    callevent_handler.side_effect = side_effect
    with pytest.raises(BadRequest) as bad_request:
        resource.create()

    assert bad_request


@patch('pawapp.api.bill_handler')
@patch('pawapp.api.json')
def test_bill_detail_raise_exception(mocked_json, bill_handler):
    """Test method call raise exception"""
    handler_mock = Mock(**{'handle.side_effect': InvalidDataException([])})
    bill_handler.return_value = handler_mock
    mocked_json.dumps = Mock()

    resource = BillResource()
    res = None
    with pytest.raises(BadRequest):
        res = resource.detail('123')

    assert res is None
    bill_handler.assert_called_once_with(
        {'phone_number': '123', 'month': None, 'year': None}
    )
    mocked_json.dumps.assert_not_called()


@patch('pawapp.api.bill_handler')
@patch('pawapp.api.json')
def test_bill_detail_valid(mocked_json, bill_handler):
    """Test method call with valid data"""
    handler_mock = Mock(**{'handle.return_value': {'test': 'ok'}})
    bill_handler.return_value = handler_mock
    mocked_json.dumps = Mock(return_value='test_is_ok')

    resource = BillResource()
    res = resource.detail('321')
    assert res == 'test_is_ok'
    bill_handler.assert_called_once_with(
        {'phone_number': '321', 'month': None, 'year': None}
    )
    mocked_json.dumps.assert_called_once_with({'test': 'ok'})
