from django.forms import ModelForm

from core.models import CallEvent


class CallEventForm(ModelForm):
    class Meta(object):
        model = CallEvent
        fields = [
            'event_id',
            'call_type',
            'call_timestamp',
            'call_id',
            'source_number',
            'destination_number',
        ]
