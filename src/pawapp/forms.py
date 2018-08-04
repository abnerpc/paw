import datetime

from django import forms

from . import models, const


class CallEventForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()

        # validate timstamp format
        call_timestamp = cleaned_data.get('call_timestamp')
        if call_timestamp:
            try:
                datetime.datetime.strptime(
                    call_timestamp, const.TIMESTAMP_FORMAT
                )
            except ValueError:
                self.add_error(
                    'call_timestamp', const.MESSAGE_FIELD_INVALID_FORMAT
                )

        # validate if phone numbers is required and valid
        def validate_phone_field(field, call_type):
            field_value = cleaned_data.get(field)
            if not field_value:
                if call_type == const.CALL_TYPE_START:
                    self.add_error(field, const.MESSAGE_FIELD_REQUIRED)
                return
            if not str(field_value).isdigit():
                self.add_error(field, const.MESSAGE_FIELD_INVALID_VALUE)
            elif len(str(field_value)) < const.PHONE_NUMBER_MIN_LENGTH:
                self.add_error(field, const.MESSAGE_FIELD_INVALID_VALUE)

        call_type = cleaned_data.get('call_type')
        for field in ['source_number', 'destination_number']:
            if field not in self.errors:
                validate_phone_field(field, call_type)

    class Meta():
        model = models.CallEvent
        fields = [
            'call_type',
            'call_timestamp',
            'call_id',
            'source_number',
            'destination_number'
        ]
