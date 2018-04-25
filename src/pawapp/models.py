from datetime import datetime, timedelta
from decimal import Decimal

from django.db import models

from . import const
from . import exceptions
from . import cache


class CallEvent(models.Model):
    """Model representing the call events ocurred"""

    call_type = models.CharField(max_length=5, choices=const.CALL_TYPE_CHOICES)
    call_timestamp = models.CharField(max_length=20)
    call_id = models.CharField(
        db_index=True, max_length=const.CALL_ID_MAX_LENGTH)
    source_number = models.CharField(
        max_length=const.PHONE_NUMBER_MAX_LENGTH, blank=True, null=True)
    destination_number = models.CharField(
        max_length=const.PHONE_NUMBER_MAX_LENGTH, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def call_timestamp_datetime(self):
        call_ts = self.call_timestamp
        return datetime.strptime(call_ts, const.TIMESTAMP_FORMAT)

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
            call_value, call_duration = cls.calculate_call(call_id)
            # save bill values

        return event

    @classmethod
    def interval_by_call_id(cls, call_id):
        """
        Return call timestamp interval as datetime

        Args:
            call_id (int): Call event Id

        Returns:
            dict: Dictionary with start and end datetime
        """
        interval_values = {}
        call_events = cls.objects.filter(call_id=call_id).values_list(
            'call_type', 'call_timestamp')
        if call_events:
            interval_values = dict(call_events)
            for field in ['start', 'end']:
                call_ts = interval_values.get(field)
                if call_ts:
                    interval_values[field] = datetime.strptime(
                        call_ts, const.TIMESTAMP_FORMAT)
        return interval_values

    @classmethod
    def calculate_call(cls, call_id):
        """
        Calculated the call value and duration charged

        Args:
            call_id (int): Call event Id being calculated

        Returns:
            decimal, decimal: Two values representing the total value and duration calculated
        """
        # get start and end events for this call
        call_events = cls.interval_by_call_id(call_id)

        # start and end being calculated
        start_call = call_events.get('start')
        end_call = call_events.get('end')

        # check if the values are valid
        if not start_call or not end_call:
            raise exceptions.InvalidCallPairException()
        if end_call <= start_call:
            raise exceptions.InvalidCallIntervalException()

        # build values maps based on start and end calls datetime
        map_interval_values = ConnectionRate.mapped_rates_interval(start_call, end_call)
        if not map_interval_values:
            raise exceptions.RatesNotFoundException()

        # hold the calculated values and durations
        calculated_values, calculated_durations = [], []

        def calculate_values(from_datetime, to_datetime, minute_rate):
            """Calculate and hold values"""
            # duration in minutes for the interval
            time_diff = (to_datetime - from_datetime)
            duration = int(time_diff.total_seconds() / 60)

            # calculate the interval duration with the current minute rate
            calculated_value = duration * minute_rate
            calculated_values.append(round(Decimal(calculated_value), 2))
            calculated_durations.append(duration)

        first_found = last_found = False
        for from_datetime, to_datetime, standing_rate, minute_rate in map_interval_values:

            if not first_found:

                if not from_datetime < start_call < to_datetime:
                    continue

                first_found = True

                # append the standing rate
                calculated_values.append(standing_rate)

                from_datetime = start_call

            if from_datetime.date() == end_call.date():

                if from_datetime < end_call < to_datetime:
                    to_datetime = end_call
                    last_found = True

            calculate_values(from_datetime, to_datetime, minute_rate)
            if last_found:
                break

        # returns all the sum of the calculated values and durations
        return sum(calculated_values), sum(calculated_durations)

    class Meta:
        unique_together = ('call_type', 'call_id')


class ConnectionRate(models.Model):
    """Model representing the connection rate calls"""

    from_time = models.TimeField()
    to_time = models.TimeField()
    standing_rate = models.DecimalField(max_digits=8, decimal_places=2)
    minute_rate = models.DecimalField(max_digits=8, decimal_places=2)

    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def current_rates(cls, use_cache=True):
        """
        Current rates available for calculation

        Args:
            use_cache (bool): Should use the cache

        Returns:
            list: List with dict object with the fields:
            from_time, to_time, stangind and minute rates
        """
        data = None
        if use_cache:
            data = cache.get_value(const.CACHE_KEY_RATES)

        if not data:
            values_fields = [
                'from_time', 'to_time', 'standing_rate', 'minute_rate']
            rates = cls.objects.values_list(*values_fields)
            if rates:
                data = tuple(rates)
                if use_cache:
                    cache.set_value(const.CACHE_KEY_RATES, data)

        return data

    @classmethod
    def mapped_rates_interval(cls, start_datetime, end_datetime):
        """
        List of mapped datetime and values intervals

        This method is responsible to calculate the range of intervals between
        the start and end datetime with respective values.

        Args:
            start_datetime (datetime): Start datetime object
            end_datetime (datetime): End datetime object

        Returns:
            list: List of intervals
        """
        # get the current rates
        rates = cls.current_rates()
        if not rates:
            return []

        # build values maps based on start and end calls datetime
        map_interval_values = []

        def add_map_interval_values(first_date, second_date, first_value, second_value):
            """Verify if the values exists and add to the map"""
            values = (first_date, second_date, first_value, second_value)
            if values not in map_interval_values:
                map_interval_values.append(values)

        # calculate range of days
        duration_days = end_datetime.date() - start_datetime.date()
        duration_days = duration_days.days + 1

        # loop over the range adding values to the map
        for days in range(duration_days):

            current_day = start_datetime.date() + timedelta(days=days)
            for from_time, to_time, standing_rate, minute_rate in rates:
                if to_time <= from_time:
                    yesterday = current_day + timedelta(days=-1)
                    tomorrow = current_day + timedelta(days=1)
                    add_map_interval_values(
                        datetime.combine(yesterday, from_time),
                        datetime.combine(current_day, to_time),
                        standing_rate,
                        minute_rate
                    )
                    add_map_interval_values(
                        datetime.combine(current_day, from_time),
                        datetime.combine(tomorrow, to_time),
                        standing_rate,
                        minute_rate
                    )
                else:
                    add_map_interval_values(
                        datetime.combine(current_day, from_time),
                        datetime.combine(current_day, to_time),
                        standing_rate,
                        minute_rate
                    )
        # sort the maps by the datetime values
        map_interval_values.sort(key=lambda v: (v[0], v[1]))

        return map_interval_values


class Bill(models.Model):
    """Model representing the phone bill"""
    phone_number = models.CharField(max_length=const.PHONE_NUMBER_MAX_LENGTH)
    year = models.PositiveSmallIntegerField()
    month = models.PositiveSmallIntegerField()
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        unique_together = ('phone_number', 'year', 'month')


class BillItem(models.Model):
    """Model representing the item of a Bill"""
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=const.PHONE_NUMBER_MAX_LENGTH)
    from_time = models.DateTimeField()
    to_time = models.DateTimeField()
    duration = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=8, decimal_places=2)
