from datetime import datetime, timedelta
import pickle
from decimal import Decimal

from django.db import models
from django.core.cache import cache

from . import const
from . import exceptions


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
    def save_event(cls, calc_bill=False, **data):
        """
        Save or update Call Event

        Args:
            calc_bill (bool, optional): Should calculated the bill for this call event
            **data: Dict with Call Event data

        Returns:
            CallEvent: Instance created or updated
        """
        # save or update call event data
        call_type = data.pop('call_type')
        call_id = data.pop('call_id')
        event, _ = cls.objects.update_or_create(
            call_type=call_type,
            call_id=call_id,
            defaults=data
        )

        if calc_bill:
            call_value, call_duration = cls.calculate_call_value(call_id)
            # save bill values

        return event

    @classmethod
    def calculate_call(cls, call_id):
        """
        Calculated the call value and duration charged

        Args:
            call_id: Call event Id being calculated

        Returns:
            decimal, decimal: Two values representing the total value and duration calculated
        """
        # get start and end events for this call
        call_events = cls.objects.filter(call_id=call_id).values_list(
            'call_type', 'call_timestamp')
        if len(call_events) != 2:
            raise exceptions.WrongNumberToCalcException()
        call_events = dict(call_events)
        start_call = call_events.get('start')
        end_call = call_events.get('end')

        # get the current rates
        rates = ConnectionRate.current_rates()
        if not rates:
            raise exceptions.RatesNotFoundToCalcException()

        # hold the calculated values and durations
        calculated_values, calculated_durations = [], []
        # difference between the start and end call
        diff_between_calls = end_call - start_call
        # difference of days plus one day to loop in
        total_days = diff_between_calls.days + 1
        # flag to hold if the first interval was already found
        first_interval_found = False

        # loop over the days calculating values for the intervals
        for calc_days in range(total_days):

            # current day being calculated
            current_day = start_call.date() + timedelta(days=calc_days)

            # loop over the rates for the current day
            for from_time, to_time, standing_rate, minute_rate in rates:

                # from/to datetime to be the current interval calculated
                from_datetime = datetime.combine(current_day, from_time)
                to_datetime = datetime.combine(current_day, to_time)

                # if the difference in days is negative, set the to_datetime for the next day
                # used for intervals when start time is bigger than the end time
                diff = (to_datetime - from_datetime)
                if diff.days < 0:
                    to_datetime = datetime.combine(current_day + timedelta(days=1), to_time)

                # if this current_day being calculated is the same as the start time
                # and it's the first interval
                if current_day == start_call.date() and not first_interval_found:

                    # if start call datetime is not in the interval
                    if from_datetime > start_call > to_datetime:
                        continue

                    # append the standing rate
                    calculated_values.append(standing_rate)

                    # set the first interval was already calculated
                    first_interval_found = True

                    # set the from to the start call
                    from_datetime = start_call

                # if the current day being calculated is the same as the end time
                if current_day == end_call.date():
                    # if the end call is less than the current to datetime
                    # set the to as the end call
                    if end_call < to_datetime:
                        to_datetime = end_call

                # duration in minutes for the interval
                time_diff = (to_datetime - from_datetime)
                duration = int(time_diff.total_seconds() / 60)

                # calculate the interval duration with the current minute rate
                calculated_value = duration * minute_rate
                calculated_values.append(round(Decimal(calculated_value), 2))
                calculated_durations.append(duration)

        # returns all the sum of the calculated values and duration
        return sum(calculated_values), sum(calculated_durations)

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
                return pickle.loads(rates_data)

        values_fields = [
            'from_time', 'to_time', 'standing_rate', 'minute_rate']
        rates = cls.objects.values_list(*values_fields)
        if rates and use_cache:
            cache.set(const.CACHE_KEY_RATES, pickle.dumps(tuple(rates)))

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
    duration = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=8, decimal_places=2)
