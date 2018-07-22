"""Helper functions module"""
import datetime


def map_dict_fields(source, from_fields, to_fields):
    """Change the source keys in from_fields to to_fields"""
    if not all([source, from_fields, to_fields]):
        return

    fields_mapper = list(zip(from_fields, to_fields))
    for from_field, to_field in fields_mapper:
        value = source.pop(from_field, None)
        if not value:
            continue
        source[to_field] = value


def add_list_value(source, key, item):
    """Add item to a list inside the source dict"""
    current_list = source.get(key)
    if not current_list:
        current_list = []
        source[key] = current_list
    current_list.append(item)


def last_period():
    """Get the last month and year based on today"""
    month_first_day = datetime.datetime.today().replace(day=1)
    last_month_day = month_first_day - datetime.timedelta(days=1)
    return last_month_day.year, last_month_day.month
