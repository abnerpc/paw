import ujson
from django.db import models
from django.core.cache import cache


from . import const


class CallEvent(models.Model):
    """Model for the call events ocurred"""

    call_type = models.CharField(max_length=5, choices=const.CALL_TYPE_CHOICES)
    call_timestamp = models.DateTimeField()
    call_id = models.CharField(
        db_index=True, max_length=const.CALL_ID_MAX_LENGTH)
    source_number = models.CharField(
        max_length=const.PHONE_NUMBER_MAX_LENGTH, blank=True, null=True)
    destination_number = models.CharField(
        max_length=const.PHONE_NUMBER_MAX_LENGTH, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create_event(cls, calc_bill, **data):
        event = cls.objects.create(**data)

        if calc_bill:
            cls.calculate_bill(data.get('call_id'))

        return event

    @classmethod
    def calculate_bill(cls, call_id):
        call_events = cls.objects.filter(call_id=call_id)
        if len(call_events) != 2:
            raise Exception()

        rates = ConnectionRate.current_rates()

        for rate in rates:
            pass

    class Meta:
        unique_together = ('call_type', 'call_id')


class ConnectionRate(models.Model):
    """Model for the connection rate uppon the calls"""

    from_time = models.TimeField()
    to_time = models.TimeField()
    standing_rate = models.DecimalField(max_digits=8, decimal_places=2)
    minute_rate = models.DecimalField(max_digits=8, decimal_places=2)

    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def current_rates(cls, use_cache=True):
        if use_cache:
            rates_data = cache.get(const.CACHE_KEY_RATES)
            if rates_data:
                return ujson.loads(rates_data)

        rates = cls.objects.all()
        if rates and use_cache:
            cache.set(const.CACHE_KEY_RATES, ujson.dumps(rates))

        return rates


class Bill(models.Model):

    phone_number = models.CharField(max_length=const.PHONE_NUMBER_MAX_LENGTH)
    year = models.PositiveSmallIntegerField()
    month = models.PositiveSmallIntegerField()
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        unique_together = ('phone_number', 'year', 'month')


class BillItem(models.Model):

    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=const.PHONE_NUMBER_MAX_LENGTH)
    from_time = models.DateTimeField()
    to_time = models.DateTimeField()
    duration = models.DecimalField(max_digits=8, decimal_places=2)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
