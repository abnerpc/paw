"""Handler module for incoming data through the API"""
import datetime

from . import const
from .exceptions import InvalidDataException
from .helpers import map_dict_fields, add_list_value, last_period
from .jobs import save_callevent
from .models import Bill


class BaseDataHandler:
    """Base data handler"""

    def __init__(self, data):
        self.data = data or {}
        self.errors = {}

    def handle(self):
        raise NotImplementedError

    def validate(self):
        raise NotImplementedError

    def add_error(self, field, message):
        add_list_value(self.errors, field, message)


class CallEventHandler(BaseDataHandler):
    """Handle Call Event data"""

    def __init__(self, data):
        super().__init__(data)

    def handle(self):
        """Validate and save the data"""

        self.validate()
        if self.errors:
            raise InvalidDataException(self.errors)

        # parse the data
        map_dict_fields(self.data, const.API_FIELDS, const.DB_FIELDS)

        # save data
        self.save()

    def validate(self):
        """Validate fields from data"""

        # validate the type field
        type_field = self.data.get('type')
        if not type_field:
            self.add_error('type', const.MESSAGE_FIELD_REQUIRED)
        else:
            callevent_choices_keys = dict(const.CALL_TYPE_CHOICES).keys()
            if type_field not in callevent_choices_keys:
                self.add_error('type', const.MESSAGE_FIELD_INVALID_VALUE)

        # validate the timestamp field
        timestamp_field = self.data.get('timestamp')
        if not timestamp_field:
            self.add_error('timestamp', const.MESSAGE_FIELD_REQUIRED)
        else:
            try:
                datetime.datetime.strptime(
                    timestamp_field, const.TIMESTAMP_FORMAT)
            except ValueError:
                self.add_error(
                    'timestamp', const.MESSAGE_FIELD_INVALID_FORMAT
                )

        # validate the call_id field
        call_id_field = self.data.get('call_id')
        if not call_id_field:
            self.add_error('call_id', const.MESSAGE_FIELD_REQUIRED)
        else:
            if len(str(call_id_field)) > const.CALL_ID_MAX_LENGTH:
                self.add_error('call_id', const.MESSAGE_FIELD_INVALID_LENGTH)

        # validate source and destination fields
        for field in ['source', 'destination']:
            field_value = self.data.get(field)
            if not field_value:
                if type_field == const.CALL_TYPE_START:
                    self.add_error(field, const.MESSAGE_FIELD_REQUIRED)
            else:
                value_valid_length = (
                    len(field_value) >= const.PHONE_NUMBER_MIN_LENGTH and
                    len(field_value) <= const.PHONE_NUMBER_MAX_LENGTH
                )
                if not value_valid_length:
                    self.add_error(field, const.MESSAGE_FIELD_INVALID_LENGTH)
                if not field_value.isdigit():
                    self.add_error(field, const.MESSAGE_FIELD_INVALID_VALUE)

    def save(self):
        """Save current data"""
        # send data to be saved by another job
        save_callevent.delay(self.data)


class BillHandler(BaseDataHandler):
    """Handle Bill data"""

    def __init__(self, data):
        super().__init__(data)

    def handle(self):
        """Handle Bill detail request"""

        self.validate()
        if self.errors:
            raise InvalidDataException(self.errors)

        phone_number = self.data.get('phone_number')
        month = self.data.get('month')
        year = self.data.get('year')

        if not month and not year:
            year, month = last_period()

        bill_data = Bill.data_by_number_period(phone_number, month, year)
        return bill_data

    def validate(self):
        """Validate data requested"""
        phone_number = self.data.get('phone_number', '')
        if not phone_number:
            self.add_error('phone_number', const.MESSAGE_FIELD_REQUIRED)
        elif not str(phone_number).isdigit():
            self.add_error('phone_number', const.MESSAGE_FIELD_INVALID_VALUE)
        elif len(str(phone_number)) > 11:
            self.add_error('phone_number', const.MESSAGE_FIELD_INVALID_LENGTH)

        # validate period
        month = self.data.get('month')
        year = self.data.get('year')
        if (not month and year) or (month and not year):
            self.add_error('period', const.MESSAGE_PERIOD_WRONG)
        elif month and year:
            try:
                month = int(month)
                year = int(year)
                if len(str(month)) > 2 or len(str(year)) != 4:
                    self.add_error('period', const.MESSAGE_FIELD_INVALID_LENGTH)
                else:
                    period_date = datetime.date(year, month, 1)
                    last_period_date = datetime.date(*last_period(), day=1)
                    if period_date > last_period_date:
                        self.add_error('period', const.MESSAGE_PERIOD_INVALID)
            except ValueError:
                self.add_error('period', const.MESSAGE_FIELD_INVALID_VALUE)

def callevent_handler(data):
    return CallEventHandler(data)


def bill_handler(data):
    return BillHandler(data)

