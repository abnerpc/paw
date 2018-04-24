"""Module to test models"""
import datetime
from decimal import Decimal

import pytest
from unittest.mock import Mock

from pawapp.models import CallEvent, ConnectionRate
from pawapp.exceptions import (
    InvalidCallPairException, InvalidCallIntervalException, RatesNotFoundException
)


@pytest.mark.parametrize('call_data,rates_data,expected_value,expected_duration', [
    (
        [
            ('start', datetime.datetime(2018, 4, 5, 10, 20)),
            ('end', datetime.datetime(2018, 4, 5, 15, 55)),
        ],
        [
            (datetime.time(10, 00), datetime.time(20, 00), Decimal('0.4'), Decimal('0.02'))
        ],
        Decimal('7.1'),
        335
    ),
    (
        [
            ('start', datetime.datetime(2018, 4, 5, 21, 57, 13)),
            ('end', datetime.datetime(2018, 4, 5, 22, 10, 56)),
        ],
        [
            (datetime.time(6, 00), datetime.time(22, 00), Decimal('0.36'), Decimal('0.09')),
            (datetime.time(22, 00), datetime.time(6, 00), Decimal('0.36'), Decimal('0.0')),
        ],
        Decimal('0.54'),
        12
    ),
    (
        [
            ('start', datetime.datetime(2018, 4, 4, 21, 57, 13)),
            ('end', datetime.datetime(2018, 4, 5, 22, 10, 56)),
        ],
        [
            (datetime.time(6, 00), datetime.time(22, 00), Decimal('1.23'), Decimal('0.09')),
            (datetime.time(22, 00), datetime.time(6, 00), Decimal('0.36'), Decimal('0.01')),
        ],
        Decimal('92.71'),
        1452
    ),
    (
        [
            ('start', datetime.datetime(2018, 4, 17, 14, 30, 13)),
            ('end', datetime.datetime(2018, 4, 19, 3, 23, 56)),
        ],
        [
            (datetime.time(9, 30), datetime.time(15, 40), Decimal('5.67'), Decimal('0.76')),
            (datetime.time(15, 40), datetime.time(1, 00), Decimal('4.54'), Decimal('0.98')),
            (datetime.time(1, 00), datetime.time(9, 30), Decimal('3.22'), Decimal('1.2')),
        ],
        Decimal('2220.51'),
        2212
    ),
    (
        [
            ('start', datetime.datetime(2018, 4, 5, 10, 20, 10)),
            ('end', datetime.datetime(2018, 4, 5, 15, 55, 50)),
        ],
        [
            (datetime.time(6, 00), datetime.time(22, 00), Decimal('6.78'), Decimal('0.78')),
            (datetime.time(22, 00), datetime.time(6, 00), Decimal('2.67'), Decimal('0.08')),
        ],
        Decimal('268.08'),
        335
    ),
    (
        [
            ('start', datetime.datetime(2018, 4, 5, 10, 20, 10)),
            ('end', datetime.datetime(2018, 4, 6, 15, 55, 50)),
        ],
        [
            (datetime.time(13, 00), datetime.time(14, 00), Decimal('5.64'), Decimal('2.87')),
            (datetime.time(14, 00), datetime.time(13, 00), Decimal('4.23'), Decimal('1.32')),
        ],
        Decimal('2531.91'),
        1774
    ),
    (
        [
            ('start', datetime.datetime(2018, 4, 17, 23, 57, 10)),
            ('end', datetime.datetime(2018, 4, 18, 2, 55, 50)),
        ],
        [
            (datetime.time(0, 00), datetime.time(1, 00), Decimal('3.54'), Decimal('6.56')),
            (datetime.time(1, 00), datetime.time(0, 00), Decimal('6.76'), Decimal('4.53')),
        ],
        Decimal('930.37'),
        177
    ),
    (
        [
            ('start', datetime.datetime(2018, 4, 18, 3, 44, 10)),
            ('end', datetime.datetime(2018, 4, 18, 7, 22, 50)),
        ],
        [
            (datetime.time(0, 00), datetime.time(0, 00), Decimal('3.42'), Decimal('0.2')),
        ],
        Decimal('47.02'),
        218
    ),
])
def test_calculate_call_values(call_data, rates_data, expected_value, expected_duration):
    """Test method calculate_call from CallEvent model"""
    values_list_mock = Mock(**{'values_list.return_value': call_data})
    CallEvent.objects.filter = Mock(return_value=values_list_mock)
    ConnectionRate.current_rates = Mock(return_value=rates_data)

    total_value, total_duration = CallEvent.calculate_call('1')

    assert total_value == expected_value
    assert total_duration == expected_duration


@pytest.mark.parametrize('values_list', [
    [], ['test'], ['1', '2', '3']
])
def test_calculate_call_invalid_pair_of_calls(values_list):
    """Test method calculate_call with invalid call pairs"""
    values_list_mock = Mock(**{'values_list.return_value': values_list})
    CallEvent.objects.filter = Mock(return_value=values_list_mock)

    with pytest.raises(InvalidCallPairException):
        CallEvent.calculate_call('1')


@pytest.mark.parametrize('start_datetime,end_datetime', [
    (datetime.datetime(2018, 2, 3, 10, 50, 56), datetime.datetime(2018, 2, 3, 5, 7, 3)),
    (datetime.datetime(2018, 2, 2, 10, 50, 56), datetime.datetime(2018, 2, 1, 14, 7, 3)),
    (datetime.datetime(2018, 4, 5, 6, 34, 23), datetime.datetime(2018, 4, 5, 6, 34, 23)),
    (datetime.datetime(2018, 2, 3, 10, 50, 56), datetime.datetime(2018, 2, 3, 10, 50, 55)),
])
def test_calculate_call_invalid_call_interval(start_datetime, end_datetime):
    """Test method calculate_call with invalid pair interval"""
    values_list = [('start', start_datetime), ('end', end_datetime)]
    values_list_mock = Mock(**{'values_list.return_value': values_list})
    CallEvent.objects.filter = Mock(return_value=values_list_mock)

    with pytest.raises(InvalidCallIntervalException):
        CallEvent.calculate_call('1')


def test_calculate_call_with_rates_not_found():
    """Test method calculate_call with no rates found"""
    values_list = [('start', 1), ('end', 2)]
    values_list_mock = Mock(**{'values_list.return_value': values_list})
    CallEvent.objects.filter = Mock(return_value=values_list_mock)
    ConnectionRate.current_rates = Mock(return_value=[])

    with pytest.raises(RatesNotFoundException):
        CallEvent.calculate_call('1')
