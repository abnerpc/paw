import pytest

from pawapp.helpers import map_dict_fields


@pytest.mark.parametrize('data,from_fields,to_fields,expected', [
    ({'id': 1}, ['id'], ['to_id'], {'to_id': 1}),
    ({'id': 2}, ['ids'], ['to_ids'], {'id': 2}),
    (
        {'id': 1, 'field_1': 1, 'field_2': '2', 'field_3': [1, 2, 3]},
        ['id', 'field_1', 'field_3'],
        ['new_id', 'new_field_1', 'new_field_3'],
        {
            'new_id': 1,
            'new_field_1': 1,
            'field_2': '2',
            'new_field_3': [1, 2, 3]
        },
    )
])
def test_map_dict_fields(data, from_fields, to_fields, expected):
    map_dict_fields(data, from_fields, to_fields)
    for key, value in expected.items():
        assert key in data
        assert data[key] == value
