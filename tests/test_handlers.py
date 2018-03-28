from unittest.mock import Mock, patch

import pytest

from pawapp.exceptions import InvalidDataException
from pawapp.const import (
    API_FIELDS, DB_FIELDS, CALL_TYPE_START, CALL_TYPE_END
)
from pawapp.handlers import CallEventHandler


@patch('pawapp.handlers.map_dict_fields')
def test_callevent_handle_calls(map_dict_fields):
    handler = CallEventHandler()
    handler.validate = Mock(return_value=None)
    handler.save = Mock()

    handler.handle(None)
    handler.validate.assert_called_once()
    map_dict_fields.assert_called_once_with({}, API_FIELDS, DB_FIELDS)
    handler.save.assert_called_once()


def test_callevent_handle_raise_validation_exception():
    handler = CallEventHandler()
    handler.validate = Mock(return_value={'error': 'testing'})

    with pytest.raises(InvalidDataException) as exception_info:
        handler.handle(None)

    ide = exception_info.value
    assert ide.errors['error'] == 'testing'


@pytest.mark.parametrize('data,expected_errors', [
    ({}, ['type', 'timestamp', 'call_id']),
    ({'type': 'a'}, ['type', 'timestamp', 'call_id']),
    (
        {'type': CALL_TYPE_START},
        ['timestamp', 'call_id', 'source', 'destination']
    ),
    ({'type': CALL_TYPE_END}, ['timestamp', 'call_id']),
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
def test_callevent_validate_required(data, expected_errors):
    handler = CallEventHandler()
    handler.data = data

    errors = handler.validate()
    assert len(expected_errors) == len(errors.keys())
    for key in expected_errors:
        assert key in errors
