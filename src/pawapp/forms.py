import datetime

from django import forms

from . import models, const


class CallEventForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()

        # validate timstamp format
        call_timestamp = self.cleaned_data.get('call_timestamp')
        if call_timestamp:
            try:
                datetime.datetime.strptime(call_timestamp, const.TIMESTAMP_FORMAT)
            except ValueError:
                self.add_error('call_timestamp', const.MESSAGE_FIELD_INVALID_FORMAT)

        # validate if phone numbers is required
        call_type = self.cleaned_data.get('call_type')
        if call_type == const.CALL_TYPE_START:
            if not self.cleaned_data.get('source_number') and 'source_number' not in self.errors:
                self.add_error('source_number', const.MESSAGE_FIELD_REQUIRED)
            if not self.cleaned_data.get('destination_number') and 'destination_number' not in self.errors:
                self.add_error('destination_number', const.MESSAGE_FIELD_REQUIRED)

    class Meta():
        model = models.CallEvent
        fields = ['call_type', 'call_timestamp', 'call_id', 'source_number', 'destination_number']
