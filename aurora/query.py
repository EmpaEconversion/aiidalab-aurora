# -*- coding: utf-8 -*-

import pandas as pd
import json
from .schemas.battery import BatterySpecsJsonTypes, BatterySampleJsonTypes

AVAILABLE_SAMPLES_FILE = 'available_samples_peter.json'

def load_available_specs():
    STD_SPECS = pd.read_csv('sample_specs.csv', dtype=BatterySpecsJsonTypes)
    return STD_SPECS

def load_available_samples():
    # AVAIL_SAMPLES = [BatterySample.parse_obj(dic) for dic in json.load(open('available_samples.json', 'r'))]
    # AVAIL_SAMPLES_D = {battery_id: BatterySample.parse_obj(dic) for battery_id, dic in json.load(open('available_samples_id.json', 'r')).items()}
    with open(AVAILABLE_SAMPLES_FILE, 'r') as f:
        data = json.load(f)
    # load json and enforce data types
    AVAIL_SAMPLES_DF = pd.json_normalize(data)
    AVAIL_SAMPLES_DF = AVAIL_SAMPLES_DF.astype(dtype={col: typ for col, typ in BatterySampleJsonTypes.items() if col in AVAIL_SAMPLES_DF.columns})
    AVAIL_SAMPLES_DF["metadata.creation_datetime"] = pd.to_datetime(AVAIL_SAMPLES_DF["metadata.creation_datetime"])
    return AVAIL_SAMPLES_DF

STD_RECIPIES = {
    'Load fresh battery into cycler': ['Request the user to load a battery with the desired specs.'],
    'Synthesize - Recipe 1': ['step 1', 'step 2', 'step 3'],
    'Synthesize - Recipe 2': ['step 1', 'step 2', 'step 3'],
}

def load_available_recipies():
    global STD_RECIPIES
    return STD_RECIPIES.copy()

def update_available_samples():
    global available_samples
    available_samples = load_available_samples()

def update_available_specs():
    global available_specs
    available_specs = load_available_specs()

def update_available_recipies():
    global available_recipies
    available_recipies = load_available_recipies()

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
    global available_recipies
    return available_recipies

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


STD_PROTOCOLS = {
    "Formation cycles": {
        "Procedure": [
            "6h rest",
            "CCCV Charge, C/10 (CV condition: i<C/50)",
            "CC Discharge, D/10",
            "Repeat 3 times"],
        "Cutoff conditions": "2.5 to 4.2 V, upper voltage to be changed depending on the chemistry",},
    "Power test Charge focus": {
        "Procedure": [
            "6h rest",
            "CC Charge (CV condition: i<C/50)",
            "(C/20 + D/20) x 5",
            "(C/10 + D/20) x 5",
            "(C/5 + D/20) x 5",
            "(C/2 + D/20) x 5",
            "(1C + D/20) x 5",
            "(2C + D/20) x 5",
            "(5C + D/20) x 5",
            "(C/20 + D/20) x 5"],
        "Cutoff conditions": "2.5 to 4.2 V, upper voltage to be changed depending on the chemistry",},
    "Power test Discharge focus": {
        "Procedure": [
            "6h rest",
            "CCCV Charge (CV condition: i<C/50)",
            "(C/20 + D/20) x 5",
            "(C/20 + D/10) x 5",
            "(C/20 + D/50) x 5",
            "(C/20 + D/2) x 5",
            "(C/20 + 1D) x 5",
            "(C/20 + 2D) x 5",
            "(C/20 + 5D) x 5",
            "(C/20 + D/20) x 5"],
        "Cutoff conditions": "2.5 to 4.2 V, upper voltage to be changed depending on the chemistry",},
}

def load_available_protocols():
    global STD_PROTOCOLS
    return STD_PROTOCOLS.copy()

def update_available_protocols():
    global available_protocols
    available_protocols = load_available_protocols()
    
def query_available_protocols():
    """A mock function that returns the available synthesis recipies."""
    global available_protocols
    return available_protocols