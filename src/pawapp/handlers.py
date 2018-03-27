"""Handler module for incoming data through the API"""
import datetime

from .exceptions import InvalidDataException

# from .forms import CallEventForm
from .const import (
    DB_FIELDS, API_FIELDS, CALL_TYPE_CHOICES, CALL_ID_MAX_LENGTH,
    CALL_TYPE_START, PHONE_NUMBER_MIN_LENGTH, PHONE_NUMBER_MAX_LENGTH
)
from .helpers import map_dict_fields, add_list_value


class BaseEventHandler:
    """Base handler"""

    def handle(self, data):
        raise NotImplementedError

    def save(self):
        raise NotImplementedError


class CallEventHandler(BaseEventHandler):
    """Handle Call Event data"""

    # default format for timestamp field
    timestamp_format = '%Y-%m-%dT%H:%M:%SZ'

    def handle(self, data):
        """Validate and save the data"""
        self.data = data or {}

        errors = self.validate()
        if errors:
            raise InvalidDataException(errors)

        # parse the data
        map_dict_fields(self.data, API_FIELDS, DB_FIELDS)

        # save data
        print('saved')

    def validate(self):
        """Validate fields from data"""
        errors = {}

        # validate the type field
        type_field = self.data.get('type')
        if not type_field:
            add_list_value(errors, 'type', 'Field type is required.')
        else:
            callevent_choices_keys = dict(CALL_TYPE_CHOICES).keys()
            if type_field not in callevent_choices_keys:
                add_list_value(errors, 'type', 'Invalid type value.')

        # validate the timestamp field
        timestamp_field = self.data.get('timestamp')
        if not timestamp_field:
            add_list_value(errors, 'timestamp', 'Field timestamp is required.')
        else:
            try:
                datetime.datetime.strptime(
                    timestamp_field, self.timestamp_format)
            except ValueError:
                add_list_value(
                    errors, 'timestamp', 'Invalid timestamp format.')

        # validate the call_id field
        call_id_field = self.data.get('call_id')
        if not call_id_field:
            add_list_value(errors, 'call_id', 'Field call_id is required.')
        else:
            if len(call_id_field) > CALL_ID_MAX_LENGTH:
                add_list_value(errors, 'call_id', 'Invalid call_id length.')

        # validate source and destination fields
        for field in ['source', 'destination']:
            field_value = self.data.get(field)
            if not field_value:
                if type_field == CALL_TYPE_START:
                    add_list_value(
                        errors, field, 'Field {} is required.'.format(field))
            else:
                value_valid_length = (
                    len(field_value) >= PHONE_NUMBER_MIN_LENGTH and
                    len(field_value) <= PHONE_NUMBER_MAX_LENGTH
                )
                if not value_valid_length:
                    add_list_value(
                        errors, field, 'Invalid {} length.'.format(field))
                if not field_value.isdigit():
                    add_list_value(
                        errors, field, 'Invalid {} characters.'.format(field))

        return errors


def callevent_handler():
    return CallEventHandler()
