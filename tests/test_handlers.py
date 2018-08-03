from unittest.mock import Mock, patch

import pytest

from pawapp.exceptions import InvalidDataException
from pawapp import const
from pawapp.handlers import callevent_handler, bill_handler
from pawapp.helpers import map_dict_fields


@patch('pawapp.handlers.map_dict_fields')
def test_calleventhandler_handle_calls(map_dict_fields):
    handler = callevent_handler(None)
    handler.validate = Mock()
    handler.save = Mock()

    handler.handle()
    handler.validate.assert_called_once_with()
    map_dict_fields.assert_called_once_with({}, const.API_FIELDS, const.DB_FIELDS)
    handler.save.assert_called_once_with()


@patch('pawapp.handlers.map_dict_fields')
def test_calleventhandler_handle_raise_validation_exception(map_dict_fields):
    handler = callevent_handler({'testing': 'ok'})
    handler.errors = {'error': 'testing'}
    handler.validate = Mock()

    with pytest.raises(InvalidDataException) as exception_info:
        handler.handle()

    ide = exception_info.value
    assert ide.errors['error'] == 'testing'
    map_dict_fields.assert_called_once_with({'testing': 'ok'}, const.API_FIELDS, const.DB_FIELDS)


@pytest.mark.parametrize('data,expected_errors', [
    ({}, ['type', 'timestamp', 'call_id']),
    ({'type': 'a'}, ['type', 'timestamp', 'call_id']),
    (
        {'type': const.CALL_TYPE_START},
        ['timestamp', 'call_id', 'source', 'destination']
    ),
    ({'type': const.CALL_TYPE_END}, ['timestamp', 'call_id']),
    ({'timestamp': '222'}, ['type', 'timestamp', 'call_id']),
    ({'timestamp': '2018-03-12'}, ['type', 'timestamp', 'call_id']),
    ({'timestamp': '2018-03-12 10:34:11'}, ['type', 'timestamp', 'call_id']),
    ({'timestamp': '2018-03-12T10:34:11Z'}, ['type', 'call_id']),
    ({'call_id': 33 * 'a'}, ['type', 'timestamp', 'call_id']),
    ({'call_id': 32 * 'a'}, ['type', 'timestamp']),
    ({'source': '123'}, ['type', 'timestamp', 'call_id', 'source']),
    ({'source': '564734568a3'}, ['type', 'timestamp', 'call_id', 'source']),
    ({'source': '564734568335'}, ['type', 'timestamp', 'call_id', 'source']),
    (
        {'destination': '564734568335'},
        ['type', 'timestamp', 'call_id', 'destination']
    ),
    (
        {'destination': 'a4734568335'},
        ['type', 'timestamp', 'call_id', 'destination']
    ),
])
def test_calleventhandler_validate_required(data, expected_errors):
    """Test EventCall handler validation"""
    map_dict_fields(data, const.API_FIELDS, const.DB_FIELDS)
    handler = callevent_handler(data)

    handler.validate()
    assert len(expected_errors) == len(handler.errors.keys())

    map_dict_fields(handler.errors, const.DB_FIELDS, const.API_FIELDS)
    for key in expected_errors:
        assert key in handler.errors


@patch('pawapp.handlers.Bill')
@patch('pawapp.handlers.last_period')
def test_billhandler_handle_raise_exception(last_period, model_bill):
    """Test Bill handle raising exception"""
    model_bill.data_by_number_period = Mock()
    handler = bill_handler({})
    handler.validate = Mock()
    handler.errors = {'has': 'error'}

    with pytest.raises(InvalidDataException):
        handler.handle()
    handler.validate.assert_called_once_with()
    last_period.assert_not_called()
    model_bill.data_by_number_period.assert_not_called()


@patch('pawapp.handlers.Bill')
@patch('pawapp.handlers.last_period')
def test_billhandler_handle_calls(last_period, model_bill):
    """Test Bill handle method calls"""
    model_bill.data_by_number_period = Mock(return_value={'data': 'here'})
    handler = bill_handler({'phone_number': 1, 'month': 2, 'year': 3})
    handler.validate = Mock()

    res = handler.handle()
    assert res['data'] == 'here'
    handler.validate.assert_called_once_with()
    last_period.assert_not_called()
    model_bill.data_by_number_period.assert_called_once_with(1, 2, 3)


@patch('pawapp.handlers.Bill')
@patch('pawapp.handlers.last_period')
def test_billhandler_handle_without_period(last_period, model_bill):
    """Test Bill handle method calls"""
    model_bill.data_by_number_period = Mock(return_value={'good': 'data'})
    handler = bill_handler({'phone_number': 111})
    handler.validate = Mock()
    last_period.return_value = (2022, 10)

    res = handler.handle()
    assert res['good'] == 'data'
    handler.validate.assert_called_once_with()
    last_period.assert_called_once_with()
    model_bill.data_by_number_period.assert_called_once_with(111, 10, 2022)


@pytest.mark.parametrize('phone_number,month,year,errors', [
    (None, 11, 2018, {'phone_number': [const.MESSAGE_FIELD_REQUIRED]}),
    ('aa1', 10, 2018, {'phone_number': [const.MESSAGE_FIELD_INVALID_VALUE]}),
    (123456789191, 6, 2018, {'phone_number': [const.MESSAGE_FIELD_INVALID_LENGTH]}),
    (1, 1, 2018, {}),
    (1, 13, 2018, {'period': [const.MESSAGE_FIELD_INVALID_VALUE]}),
    (1, 1, 18, {'period': [const.MESSAGE_FIELD_INVALID_LENGTH]}),
    (1, 111, 2018, {'period': [const.MESSAGE_FIELD_INVALID_LENGTH]}),
    (1, 'a', 2018, {'period': [const.MESSAGE_FIELD_INVALID_VALUE]}),
    (1, None, 2018, {'period': [const.MESSAGE_PERIOD_WRONG]}),
    (1, 0, 2018, {'period': [const.MESSAGE_PERIOD_WRONG]}),
    (1, 11, None, {'period': [const.MESSAGE_PERIOD_WRONG]}),
    (1, 11, 0, {'period': [const.MESSAGE_PERIOD_WRONG]}),
    (1, 11, 2018, {})
])
@patch('pawapp.handlers.last_period')
def test_billhandler_validate_data(last_period, phone_number, month, year, errors):
    """Test Bill validate data"""
    last_period.return_value = (2021, 9)
    handler = bill_handler({'phone_number': phone_number, 'month': month, 'year': year})
    handler.validate()

    assert len(errors) == len(handler.errors)
    for error, values in handler.errors.items():
        assert values == errors[error]
