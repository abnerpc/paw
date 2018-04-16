import datetime
from decimal import Decimal
from unittest.mock import Mock

from pawapp.models import CallEvent, ConnectionRate


def test_calculate_bill():
    event_data = [
        ('start', datetime.datetime(2018,4,5,10,20)),
        ('end', datetime.datetime(2018,4,5,15,55)),
    ]
    rates_data = [
        (datetime.time(10,00), datetime.time(20,00), Decimal('0.4'), Decimal('0.02')),
    ]

    values_list_mock = Mock(**{'values_list.return_value': event_data})
    CallEvent.objects.filter = Mock(return_value=values_list_mock)
    ConnectionRate.current_rates = Mock(return_value=rates_data)
    total_value, total_duration = CallEvent.calculate_call('1')

    assert total_value == Decimal('7.1')
    assert total_duration == 335


def test_second_calculate_bill():
    event_data = [
        ('start', datetime.datetime(2018,4,5,21,57,13)),
        ('end', datetime.datetime(2018,4,5,22,10,56)),
    ]
    rates_data = [
        (datetime.time(6,00), datetime.time(22,00), Decimal('0.36'), Decimal('0.09')),
        (datetime.time(22,00), datetime.time(6,00), Decimal('0.36'), Decimal('0.0')),
    ]

    values_list_mock = Mock(**{'values_list.return_value': event_data})
    CallEvent.objects.filter = Mock(return_value=values_list_mock)
    ConnectionRate.current_rates = Mock(return_value=rates_data)
    total_value, total_duration = CallEvent.calculate_call('1')

    assert total_value == Decimal('0.54')
    assert total_duration == 12


def test_third_calculate_bill():
    event_data = [
        ('start', datetime.datetime(2018,4,4,21,57,13)),
        ('end', datetime.datetime(2018,4,5,22,10,56)),
    ]
    rates_data = [
        (datetime.time(6,00), datetime.time(22,00), Decimal('1.23'), Decimal('0.09')),
        (datetime.time(22,00), datetime.time(6,00), Decimal('0.36'), Decimal('0.01')),
    ]

    values_list_mock = Mock(**{'values_list.return_value': event_data})
    CallEvent.objects.filter = Mock(return_value=values_list_mock)
    ConnectionRate.current_rates = Mock(return_value=rates_data)
    total_value, total_duration = CallEvent.calculate_call('1')

    assert total_value == Decimal('92.71')
    assert total_duration == 1452

