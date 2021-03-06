"""Django models module."""
from datetime import datetime, timedelta
from decimal import Decimal

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404

from . import const
from . import exceptions
from . import cache


class CallEvent(models.Model):
    """Model representing the call events ocurred."""

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
        """Datetime call_timestamp value.

        Returns:
            datetime: Call_timestamp value.

        """
        call_ts = self.call_timestamp
        return datetime.strptime(call_ts, const.TIMESTAMP_FORMAT)

    @classmethod
    def save_call(cls, save_bill=False, **data):
        """Save or update CallEvent.

        Args:
            save_bill (bool, optional): Should save the bill for this call
                event.
            **data: Arbitrary keyword arguments.

        Returns:
            CallEvent: Instance created or updated.

        """
        # save or update call event data
        call_type = data.pop('call_type')
        call_id = data.pop('call_id')
        event, _ = cls.objects.update_or_create(
            call_type=call_type,
            call_id=call_id,
            defaults=data
        )

        if save_bill:

            # calculate the values for the current call
            call_value, call_duration = cls.calculate_call(call_id)

            # get the calls related
            start_call = cls.objects.get(
                call_id=call_id, call_type=const.CALL_TYPE_START
            )
            end_call = cls.objects.get(
                call_id=call_id, call_type=const.CALL_TYPE_END
            )

            # save bill values
            Bill.save_by_calls(
                start_call,
                end_call,
                call_duration,
                call_value
            )

        return event

    @classmethod
    def interval_by_call_id(cls, call_id):
        """Return call timestamp interval.

        Args:
            call_id (int): Call event Id

        Returns:
            dict: Start and end datetime

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
        """Calculated the call value and duration charged.

        Args:
            call_id (int): Call event Id.

        Returns:
            tuple: Two values representing the total value and
                duration calculated.

        Raises:
            InvalidCallPairException: Raises if start or end calls are missing.
            InvalidCallIntervalException: Raises if end datetime is less than
                start datetime.
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
        map_interval_values = ConnectionRate.mapped_rates_interval(
            start_call, end_call
        )
        if not map_interval_values:
            raise exceptions.RatesNotFoundException()

        # hold the calculated values and durations
        calculated_values, calculated_durations = [], []

        def calculate_values(from_datetime, to_datetime, minute_rate):
            """Calculate and hold values"""
            # calculate duration for the interval
            time_diff = (to_datetime - from_datetime)
            duration = int(time_diff.total_seconds())
            calculated_durations.append(duration)

            # calculate the interval duration with the current minute rate
            calculated_value = int(duration / 60) * minute_rate
            calculated_values.append(round(Decimal(calculated_value), 2))

        # navigate each values:
        # from_datetime, to_datetime, standing_rate and minute_rate
        for from_dt, to_dt, standing_rate, minute_rate in map_interval_values:

            if not calculated_values:

                if not from_dt < start_call < to_dt:
                    continue

                # append the standing rate
                calculated_values.append(standing_rate)

                from_dt = start_call

            if from_dt.date() == end_call.date():

                if from_dt < end_call < to_dt:
                    calculate_values(from_dt, end_call, minute_rate)
                    break

            calculate_values(from_dt, to_dt, minute_rate)

        # returns all the sum of the calculated values and durations
        return sum(calculated_values), sum(calculated_durations)

    class Meta:
        unique_together = ('call_type', 'call_id')


class ConnectionRate(models.Model):
    """Model representing the connection rate calls."""

    from_time = models.TimeField()
    to_time = models.TimeField()
    standing_rate = models.DecimalField(max_digits=8, decimal_places=2)
    minute_rate = models.DecimalField(max_digits=8, decimal_places=2)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'from {} to {}'.format(self.from_time, self.to_time)

    @classmethod
    def current_rates(cls, use_cache=True):
        """Current rates available for calculation.

        Args:
            use_cache (bool): Should use the cache.

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
        """List of mapped datetime and values intervals.

        This method is responsible to calculate the range of intervals between
        the start and end datetime with respective values.

        Args:
            start_datetime (datetime): Start datetime object.
            end_datetime (datetime): End datetime object.

        Returns:
            list: List of intervals.

        """
        # get the current rates
        rates = cls.current_rates()
        if not rates:
            return []

        # build values interval based on start and end calls datetime
        map_interval_values = set()

        current_day = start_datetime.date()
        while current_day <= end_datetime.date():

            for from_time, to_time, standing_rate, minute_rate in rates:

                from_datetime = datetime.combine(current_day, from_time)
                to_datetime = datetime.combine(current_day, to_time)

                # if time is not inverse, add and continue
                if to_time > from_time:
                    map_interval_values.add((
                        from_datetime,
                        to_datetime,
                        standing_rate,
                        minute_rate
                    ))
                    continue

                # if time is inverse, add datetime for the day before and after
                # current day
                yesterday = current_day + timedelta(days=-1)
                yesterday_datetime = datetime.combine(yesterday, from_time)
                tomorrow = current_day + timedelta(days=1)
                tomorrow_datetime = datetime.combine(tomorrow, to_time)
                map_interval_values.add(
                    (
                        yesterday_datetime,
                        to_datetime,
                        standing_rate,
                        minute_rate
                    )
                )
                map_interval_values.add(
                    (
                        from_datetime,
                        tomorrow_datetime,
                        standing_rate,
                        minute_rate
                    )
                )

            current_day += timedelta(days=1)

        # sort set by the datetime values
        map_interval_values = sorted(
            map_interval_values, key=lambda v: (v[0], v[1])
        )

        return map_interval_values


@receiver(post_save, sender=ConnectionRate)
def postsave_connectionrate_handler(sender, **kwargs):
    """Clean cache for ConnectionRate"""
    cache.clean_value(const.CACHE_KEY_RATES)


class Bill(models.Model):
    """Model representing the phone bill."""
    phone_number = models.CharField(max_length=const.PHONE_NUMBER_MAX_LENGTH)
    year = models.PositiveSmallIntegerField()
    month = models.PositiveSmallIntegerField()
    total_duration = models.PositiveIntegerField()
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)

    @classmethod
    def save_by_calls(cls, start_call, end_call, duration, amount):
        """Save Bill and Item based on the start and end calls.

        Args:
            start_call (CallEvent): CallEvent object representing the start
                call.
            end_call (CallEvent): CallEvent object representing the end call.
            duration (int): Call duration.
            amount (float): Call value.
        """

        # get related bill or create a new one
        bill, _ = cls.objects.get_or_create(
            phone_number=start_call.source_number,
            year=end_call.call_timestamp_datetime.year,
            month=end_call.call_timestamp_datetime.month,
            defaults={'total_duration': 0, 'total_amount': 0}
        )

        # save bill item
        BillItem.objects.create(
            bill=bill,
            phone_number=start_call.destination_number,
            from_timestamp=start_call.call_timestamp,
            to_timestamp=end_call.call_timestamp,
            duration=duration,
            amount=amount
        )

        # update bill adding current call duration and amount
        bill.total_duration += duration
        bill.total_amount += amount
        bill.save()

    @classmethod
    def data_by_number_period(cls, phone_number, month, year):
        """Return bill data by phone_number, month and year.

        Args:
            phone_number (str): Phone number
            month (str): Month
            year (str): Year

        """
        query = {
            'phone_number': phone_number,
            'month': month,
            'year': year
        }

        bill = get_object_or_404(cls, **query)

        data = {
            'subscriber': phone_number,
            'period': '{}/{}'.format(month, year),
        }
        calls = []
        for billitem in bill.billitem_set.all():
            str_date, str_time = billitem.from_date_and_time
            call = {
                'destination': billitem.phone_number,
                'start_date': str_date,
                'start_time': str_time,
                'duration': billitem.repr_duration,
                'price': '{0:.2f}'.format(billitem.amount)
            }
            calls.append(call)

        data['calls'] = calls
        return data

    class Meta:
        unique_together = ('phone_number', 'year', 'month')


class BillItem(models.Model):
    """Model representing the item of a Bill."""
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=const.PHONE_NUMBER_MAX_LENGTH)
    from_timestamp = models.CharField(max_length=20)
    to_timestamp = models.CharField(max_length=20)
    duration = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=8, decimal_places=2)

    @property
    def repr_duration(self):
        """Represent duration value."""
        return str(timedelta(seconds=self.duration))

    @property
    def from_date_and_time(self):
        """From_timestamp field splited as date and time values."""
        values = self.from_timestamp.split('T')
        if len(values) != 2:
            return ['', '']
        return values
