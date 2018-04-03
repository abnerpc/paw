from django.db import IntegrityError
from django_rq import job

from . import const
from .models import CallEvent


@job
def save_callevent(data):
    try:
        calc_bill = data.get('call_type') == const.CALL_TYPE_END
        CallEvent.create_event(calc_bill, **data)
    except IntegrityError as ie:
        # todo: log, email, callback ?
        pass