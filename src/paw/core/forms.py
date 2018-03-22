from django import forms

from core.models import CallEvent, CALL_TYPE_START
from core.const import DB_FIELDS


class CallEventForm(forms.ModelForm):

    def clean_call_timestamp(self):
        """Validate timestamp data and format"""
        data = self.cleaned_data['call_timestamp']
        if not all([data.hour, data.minute, data.second]):
            raise forms.ValidationError(
                'Enter a valid time. Eg.: {0}-{1}-{2} HH:MM:SS'.format(
                    data.year, data.month, data.day))
        return data

    def clean(self):
        """Validate fields required based on the call_type"""
        cleaned_data = super().clean()
        call_type = cleaned_data.get('call_type')
        source_number = cleaned_data.get('source_number')
        destination_number = cleaned_data.get('destination_number')
        if call_type == CALL_TYPE_START:
            if not source_number:
                self.add_error(
                    'source_number',
                    'This field is required for the type start.'
                )
            if not destination_number:
                self.add_error(
                    'destination_number',
                    'This field is required for the type start.'
                )

    class Meta(object):
        model = CallEvent
        fields = DB_FIELDS
