
DB_FIELDS = [
    'call_type',
    'call_timestamp',
    'call_id',
    'source_number',
    'destination_number',
]

API_FIELDS = [
    'type',
    'timestamp',
    'call_id',
    'source',
    'destination',
]

CALL_TYPE_START = 'start'
CALL_TYPE_END = 'end'
CALL_TYPE_CHOICES = [
    (CALL_TYPE_START, 'Start'),
    (CALL_TYPE_END, 'End'),
]

CALL_ID_MAX_LENGTH = 32
PHONE_NUMBER_MIN_LENGTH = 10
PHONE_NUMBER_MAX_LENGTH = 11

TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

CACHE_KEY_RATES = 'connection_rates'

MESSAGE_FIELD_REQUIRED = 'This field is required.'
MESSAGE_FIELD_INVALID_VALUE = 'This field has an invalid value.'
MESSAGE_FIELD_INVALID_FORMAT = 'This field has an invalid format.'
MESSAGE_FIELD_INVALID_LENGTH = 'This field has an invalid length.'
MESSAGE_PERIOD_INVALID = 'Invalid period values'
MESSAGE_PERIOD_WRONG = 'Wrong period values'
