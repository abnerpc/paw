"""Handler module for incoming data through the API"""
from .exceptions import InvalidDataException

from .forms import CallEventForm
from .const import DB_FIELDS, API_FIELDS
from .helpers import map_dict_fields


class BaseEventHandler:
    """Base handler"""

    def handle(self, data):
        raise NotImplementedError

    def validate(self):
        raise NotImplementedError

    def save(self):
        raise NotImplementedError


class CallEventHandler(BaseEventHandler):
    """Handle Call Event data"""

    def handle(self, data):
        """Validate and save the data"""
        self.data = data or {}

        if self.data:
            map_dict_fields(data, API_FIELDS, DB_FIELDS)

        # run validation
        is_valid, errors = self.validate()
        if not is_valid:
            map_dict_fields(errors, DB_FIELDS, API_FIELDS)
            raise InvalidDataException(errors)

        # save data
        self.save()

    def validate(self):
        """Validate the current data using a Django form"""
        form = CallEventForm(self.data)
        if not form.is_valid():
            form_errors = dict(form.errors)
            map_dict_fields(form_errors, DB_FIELDS, API_FIELDS)
            return False, form_errors

        return True, None

    def save(self):
        """Save the current data"""
        print('saving data')
        pass


def callevent_handler():
    return CallEventHandler()
