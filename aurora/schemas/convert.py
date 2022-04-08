# -*- coding: utf-8 -*-

from numpy import NaN
from pandas import Series, DataFrame
from . import data_schemas

def _remove_empties_from_dict(a_dict):
    new_dict = {}
    for k, v in a_dict.items():
        if isinstance(v, dict):
            v = remove_empties_from_dict(v)
        if v is not None and v is not NaN and v != "":
            new_dict[k] = v
    return new_dict

def _make_formatted_dict(my_dict, key_arr, val):
    """
    Set val at path in my_dict defined by the string (or serializable object) array key_arr
    """
    current = my_dict
    for i in range(len(key_arr)):
        key = key_arr[i]
        if key not in current:
            if i == len(key_arr)-1:
                current[key] = val
            else:
                current[key] = {}
        else:
            if type(current[key]) is not dict:
                print("Given dictionary is not compatible with key structure requested")
                raise ValueError("Dictionary key already occupied")
        current = current[key]
    # return remove_empties_from_dict(my_dict)
    return my_dict

def pd_dataframe_to_formatted_json(df, sep="."):
    """Convert a pandas.DataFrame to a list of nested dictionaries."""
    if not isinstance(df, DataFrame):
        raise TypeError('df should be a pandas.DataFrame object')
    result = []
    for _, row in df.iterrows():
        parsed_row = {}
        for idx, val in row.iteritems():
            keys = idx.split(sep)
            parsed_row = _make_formatted_dict(parsed_row, keys, val)
        result.append(parsed_row)
    return result

def pd_series_to_formatted_json(series, sep="."):
    """Convert a pandas.Series to a nested dictionary."""
    if not isinstance(series, Series):
        raise TypeError('series should be a pandas.Series object')
    parsed_series = {}
    for idx, val in series.iteritems():
        keys = idx.split(sep)
        parsed_series = _make_formatted_dict(parsed_series, keys, val)
    return parsed_series

def extract_schema_types(model, sep="."):
    """Convert a pydantic schema into a nested dictionary containing types."""
    SCHEMA_TYPES = {'string': str, 'integer': int, 'number': float}
    schema_dic = {}
    for name, sdic in model.schema()['properties'].items():
        if '$ref' in sdic:
            # print(f"  {name} is a class {sdic['$ref']}")
            sub_schema = extract_schema_types(getattr(data_schemas, sdic['$ref'].split('/')[-1])) # call extract_schema for the $ref class
            for key, value in sub_schema.items():
                schema_dic[f'{name}.{key}'] = value
        elif 'type' in sdic:
            # print(f"{name} is of type {sdic['type']}")
            schema_dic[name] = SCHEMA_TYPES[sdic['type']]
    return schema_dic