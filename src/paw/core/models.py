from django.db import models


CALL_TYPE_START = 'start'
CALL_TYPE_END = 'end'
CALL_TYPE_CHOICES = [
    (CALL_TYPE_START, 'Start'),
    (CALL_TYPE_END, 'End'),
]


class CallEvent(models.Model):
    """Model for the call events ocurred"""

    event_id = models.CharField(max_length=16)
    call_type = models.CharField(max_length=5, choices=CALL_TYPE_CHOICES)
    call_timestamp = models.DateTimeField()
    call_id = models.CharField(max_length=16)
    source_number = models.CharField(max_length=9, blank=True, null=True)
    destination_number = models.CharField(max_length=9, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)


class ConnectionRate(models.Model):
    """Model for the connection rate uppon the calls"""

    from_time = models.TimeField()
    to_time = models.TimeField()
    rate = models.DecimalField(max_digits=8, decimal_places=2)

    updated_at = models.DateTimeField(auto_now=True)
