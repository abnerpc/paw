"""Handler module for incoming data through the API"""
import datetime

from . import const
from .exceptions import InvalidDataException
from .helpers import map_dict_fields, add_list_value, last_period
from .jobs import save_callevent
from .models import Bill
from .forms import CallEventForm


class BaseDataHandler:
    """Base data handler"""

    def __init__(self, data):
        self.data = data or {}
        self.errors = {}

    def handle(self):
        """Process the current data.

        **MUST BE OVERRIDDEN BY THE USER** - By default, this returns
        ``NotImplementedError``.

        Returns:
            dict: Result for the data processed.
        """
        raise NotImplementedError

    def validate(self):
        """Run the validation for the current data.

        **MUST BE OVERRIDDEN BY THE USER** - By default, this returns
        ``NotImplementedError``.
        """
        raise NotImplementedError

    def add_error(self, field, message):
        """Add message error for a field.

        Args:
            field (str): Field name.
            message (str): Message error.
        """
        add_list_value(self.errors, field, message)


class CallEventHandler(BaseDataHandler):
    """Handler class for CallEvent data."""

    def __init__(self, data):
        super().__init__(data)

    def handle(self):
        """Process CallEvent current data.

        Raises:
            InvalidDataException: Raises if data is not valid.
        """

        # parse the data
        map_dict_fields(self.data, const.API_FIELDS, const.DB_FIELDS)

        self.validate()
        if self.errors:
            raise InvalidDataException(self.errors)

        # save data
        self.save()

    def validate(self):
        """Validate fields for current data."""

        form = CallEventForm(self.data)
        if not form.is_valid():
            self.errors = form.errors
            map_dict_fields(self.errors, const.DB_FIELDS, const.API_FIELDS)

    def save(self):
        """Save current data for CallEvent.

        This function calls an async job to save the current data.
        """
        # send data to be saved by another job
        save_callevent.delay(self.data)


class BillHandler(BaseDataHandler):
    """Handler class for Bill data."""

    def __init__(self, data):
        super().__init__(data)

    def handle(self):
        """Process Bill current data.

        Raises:
            InvalidDataException: Raises if data is not valid.
        """
        self.validate()
        if self.errors:
            raise InvalidDataException(self.errors)

        phone_number = self.data.get('phone_number')
        month = self.data.get('month')
        year = self.data.get('year')

        # if a period was not informed, get the current last one
        if not month and not year:
            year, month = last_period()

        bill_data = Bill.data_by_number_period(phone_number, month, year)
        return bill_data

    def validate(self):
        """Validate fields for current data."""

        # validate phone number
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
                    self.add_error(
                        'period', const.MESSAGE_FIELD_INVALID_LENGTH
                    )
                else:
                    period_date = datetime.date(year, month, 1)
                    last_period_date = datetime.date(*last_period(), day=1)
                    if period_date > last_period_date:
                        self.add_error('period', const.MESSAGE_PERIOD_INVALID)
            except ValueError:
                self.add_error('period', const.MESSAGE_FIELD_INVALID_VALUE)


def callevent_handler(data):
    """Convenient function to return CallEvent handler instance."""
    return CallEventHandler(data)


def bill_handler(data):
    """Convenient function to return Bill handler instance."""
    return BillHandler(data)
