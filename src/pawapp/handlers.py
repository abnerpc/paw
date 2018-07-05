"""Handler module for incoming data through the API"""
import datetime

from . import const
from .exceptions import InvalidDataException
from .helpers import map_dict_fields, add_list_value
from .jobs import save_callevent


class BaseEventHandler:
    """Base handler"""

    def handle(self, data):
        raise NotImplementedError


class CallEventHandler(BaseEventHandler):
    """Handle Call Event data"""

    def handle(self, data):
        """Validate and save the data"""
        self.data = data or {}

        errors = self.validate()
        if errors:
            raise InvalidDataException(errors)

        # parse the data
        map_dict_fields(self.data, const.API_FIELDS, const.DB_FIELDS)

        # save data
        self.save()

    def validate(self):
        """Validate fields from data"""
        errors = {}

        # validate the type field
        type_field = self.data.get('type')
        if not type_field:
            add_list_value(errors, 'type', 'Field type is required.')
        else:
            callevent_choices_keys = dict(const.CALL_TYPE_CHOICES).keys()
            if type_field not in callevent_choices_keys:
                add_list_value(errors, 'type', 'Invalid type value.')

        # validate the timestamp field
        timestamp_field = self.data.get('timestamp')
        if not timestamp_field:
            add_list_value(errors, 'timestamp', 'Field timestamp is required.')
        else:
            try:
                datetime.datetime.strptime(
                    timestamp_field, const.TIMESTAMP_FORMAT)
            except ValueError:
                add_list_value(
                    errors, 'timestamp', 'Invalid timestamp format.')

        # validate the call_id field
        call_id_field = self.data.get('call_id')
        if not call_id_field:
            add_list_value(errors, 'call_id', 'Field call_id is required.')
        else:
            if len(str(call_id_field)) > const.CALL_ID_MAX_LENGTH:
                add_list_value(errors, 'call_id', 'Invalid call_id length.')

        # validate source and destination fields
        for field in ['source', 'destination']:
            field_value = self.data.get(field)
            if not field_value:
                if type_field == const.CALL_TYPE_START:
                    add_list_value(
                        errors, field, 'Field {} is required.'.format(field))
            else:
                value_valid_length = (
                    len(field_value) >= const.PHONE_NUMBER_MIN_LENGTH and
                    len(field_value) <= const.PHONE_NUMBER_MAX_LENGTH
                )
                if not value_valid_length:
                    add_list_value(
                        errors, field, 'Invalid {} length.'.format(field))
                if not field_value.isdigit():
                    add_list_value(
                        errors, field, 'Invalid {} characters.'.format(field))

        return errors

    def save(self):

        # send data to be saved by another job
        save_callevent.delay(self.data)


def callevent_handler():
    return CallEventHandler()
