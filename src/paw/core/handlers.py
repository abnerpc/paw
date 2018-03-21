from core.exceptions import InvalidDataException

from core.forms import CallEventForm


class BaseEventHandler:

    def handle():
        raise NotImplementedError


class CallEventHadler(BaseEventHandler):

    def handle(self, data):
        if not data:
            raise InvalidDataException('Missing body data')

        form = CallEventForm(data)
        if not form.is_valid():
            raise InvalidDataException(form.errors.as_json())

        # handle the data


def callevent_handler():
    return CallEventHadler()
