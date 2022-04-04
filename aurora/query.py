# -*- coding: utf-8 -*-

import pandas as pd
import json
from .schemas.data_schemas import BatterySpecsJsonTypes, BatterySampleJsonTypes

def load_available_specs():
    STD_SPECS = pd.read_csv('sample_specs.csv', dtype=BatterySpecsJsonTypes)
    return STD_SPECS

def load_available_samples():
    # AVAIL_SAMPLES = [BatterySample.parse_obj(dic) for dic in json.load(open('available_samples.json', 'r'))]
    # AVAIL_SAMPLES_D = {battery_id: BatterySample.parse_obj(dic) for battery_id, dic in json.load(open('available_samples_id.json', 'r')).items()}
    with open('available_samples.json', 'r') as f:
        data = json.load(f)
    # load json and enforce data types
    AVAIL_SAMPLES_DF = pd.json_normalize(data).astype(dtype=BatterySampleJsonTypes)
    AVAIL_SAMPLES_DF["metadata.creation_datetime"] = pd.to_datetime(AVAIL_SAMPLES_DF["metadata.creation_datetime"])
    return AVAIL_SAMPLES_DF

STD_RECIPIES = {
    'Margherita': ['pomodoro', 'mozzarella'],
    'Capricciosa': ['pomodoro', 'mozzarella', 'funghi', 'prosciutto', 'carciofini', 'olive nere'],
    'Quattro formaggi': ['mozzarella', 'gorgonzola', 'parmigiano', 'fontina'],
    'Vegetariana': ['pomodoro', 'mozzarella', 'funghi', 'zucchine', 'melanzane', 'peperoni']
}

def load_available_recipies():
    return STD_RECIPIES

def update_available_samples():
    global available_samples
    available_samples = load_available_samples()

def update_available_specs():
    global available_specs
    available_specs = load_available_specs()

def update_available_recipies():
    global available_recipies
    available_specs = load_available_recipies()

def query_available_specs(field: str = None):
    """
    This mock function returns a pandas.DataFrame of allowed specs.
        field (optional): name of a field to query [manufacturer, composition, capacity, form_factor]
    """
    global available_specs
    
    if field:
        return available_specs.get(field).unique().tolist()
    else:
        return available_specs

def query_available_samples(query=None, project=None):
    """
    This mock function returns the available samples.
        query: a pandas query
        project (optional): list of the columns to return (if None, return all)
    
    Returns a pandas.DataFrame or Series
    """
    global available_samples
    
    # perform query
    if query is not None:
        results = available_samples.query(query)
    else:
        results = available_samples
    if project and (results is not None):
        if not isinstance(project, list):
            project = [project]
        return results[project]
    else:
        return results

def query_available_recipies():
    """A mock function that returns the available synthesis recipies."""
    return STD_RECIPIES

def write_pd_query_from_dict(query_dict):
    """
    Write a pandas query from a dictionary {field: value}.
    Example: 
        write_pandas_query({'manufacturer': 'BIG-MAP', 'battery_id': 98})
    returns "(`manufacturer` == 'BIG-MAP') and (`battery_id` == 98)"
    """
    query = " and ".join(["(`{}` == {})".format(k, f"{v}" if isinstance(v, (int, float)) else f"'{v}'") for k, v in query_dict.items() if v])
    if query:
        return query