from django.db import models

from .const import (
    CALL_TYPE_CHOICES, CALL_ID_MAX_LENGTH, PHONE_NUMBER_MAX_LENGTH
)


class CallEvent(models.Model):
    """Model for the call events ocurred"""

    call_type = models.CharField(max_length=5, choices=CALL_TYPE_CHOICES)
    call_timestamp = models.DateTimeField()
    call_id = models.CharField(max_length=CALL_ID_MAX_LENGTH)
    source_number = models.CharField(
        max_length=PHONE_NUMBER_MAX_LENGTH, blank=True, null=True)
    destination_number = models.CharField(
        max_length=PHONE_NUMBER_MAX_LENGTH, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)


class ConnectionRate(models.Model):
    """Model for the connection rate uppon the calls"""

    from_time = models.TimeField()
    to_time = models.TimeField()
    rate = models.DecimalField(max_digits=8, decimal_places=2)

    updated_at = models.DateTimeField(auto_now=True)
