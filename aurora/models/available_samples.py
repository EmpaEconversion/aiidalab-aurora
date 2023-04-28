import json
import logging
from typing import Dict, Generic, Literal, Sequence, TypeVar, Union

import pandas as pd
from pydantic import BaseModel

from aurora.schemas.battery import (BatterySample, BatterySampleJsonTypes,
                                    BatterySpecsJsonTypes)

from .pattern_observer import ObserverManager

AVAILABLE_SAMPLES_FILE = 'available_samples.json'


class AvailableSamplesModel():
    """This model represents the experimental setup of samples in the devices."""

    def __init__(self):
        self.observer_manager = ObserverManager()
        self.recorded_samples = self._load_samples_file()
        self.available_samples = self._load_samples_file()
        self.available_samples_cache = self._update_pandas_cache(
            self.available_samples)

    def suscribe_observer(self, observer):
        self.observer_manager.add_observer(observer)

    def _load_samples_file(self, source_file=AVAILABLE_SAMPLES_FILE):
        """Loads the content of the available samples file"""
        with open(source_file) as fileobj:
            battery_datalist = json.load(fileobj)

        new_available_samples = []
        for battery_data in battery_datalist:
            battery_sample = BatterySample(**battery_data)
            new_available_samples.append(battery_sample)

        return new_available_samples

    def load_samples_file(self, source_file=AVAILABLE_SAMPLES_FILE):
        """Loads the content of the available samples file"""
        self.recorded_samples = self._load_samples_file()
        self.available_samples = self._load_samples_file()
        self.available_samples_cache = self._update_pandas_cache(
            self.available_samples)
        self.observer_manager.update_all()

    def save_samples_file(self, source_file=AVAILABLE_SAMPLES_FILE):
        """Saves the content in the available samples file"""
        output_list = [sample.dict() for sample in self.available_samples]
        with open(source_file, 'w') as fileobj:
            json.dump(output_list, fileobj, default=str)
            #json.dump(output_list, fileobj, indent=2, default=str)
        self.recorded_samples = self._load_samples_file()
        self.observer_manager.update_all()

    def get_samples(self):
        """Gets the samples."""
        return self.available_samples

    def _get_highest_batteryid(self):
        """Gets the highest batteryid"""
        highest_id = 0
        for sample in self.available_samples:
            highest_id = max(highest_id, sample.battery_id)
        return highest_id

    def remove_sample_with_id(self, sample_id):
        """Remove a sample from the list based on id."""
        index_of_sample_to_remove = None

        for idx, sample in enumerate(self.available_samples):
            if sample_id == sample.battery_id:
                index_of_sample_to_remove = idx
                break

        if index_of_sample_to_remove is not None:
            del self.available_samples[index_of_sample_to_remove]
            self.available_samples_cache = self._update_pandas_cache(
                self.available_samples)
            self.observer_manager.update_all()

    def parseadd_robot_output(self, filepath, basedict):
        """Adds to the list the output from the robot."""
        import csv

        datadicts = []
        with open(filepath) as fileobj:
            reader = csv.DictReader(fileobj, delimiter=';')
            for datadict in reader:
                datadicts.append(datadict)

        unadata = datadicts[0]

        battery_idx = self._get_highest_batteryid()

        for datadict in datadicts:
            battery_idx += 1
            basedict['battery_id'] = battery_idx
            new_sample = self.parse_sample_datadict(basedict, datadict)
            self.available_samples.append(new_sample)

        self.available_samples_cache = self._update_pandas_cache(
            self.available_samples)
        self.observer_manager.update_all()

    def parse_sample_datadict(self, basedict, datadict):
        """Parses stuff."""

        # These units are all wanky...
        # Both cathode and anode should be around 30 miligrams
        weight_ag = float(datadict['Anode Weight'])
        weight_cg = float(datadict['Cathode Weight (mg)']) / (1000 * 1000)
        rate_amahg = float(datadict['Anode Practical Capacity (mAh/g)'])
        rate_cmahg = float(datadict['Cathode Practical Capacity (mAh/g)'])
        capacity_a = weight_ag * rate_amahg
        capacity_c = weight_cg * rate_cmahg
        capacity = min(capacity_a, capacity_c)
        capacity = float(int(capacity * 10)) / 10

        metadata_name = basedict['basename'] + '-' + datadict['Battery_Number']

        initdict = {
            "manufacturer": basedict['manufacturer'],
            "composition": {
                "description": basedict['description']
            },
            "form_factor": datadict['Casing Type'],
            "capacity": {
                "nominal": capacity,
                "actual": None,
                "units": "mAh"
            },
            "battery_id": basedict['battery_id'],
            "metadata": {
                "name": metadata_name,
                "creation_datetime": "2022-06-28T05:59:00+00:00",
                "creation_process": "Bought in a shop."
            }
        }

        return BatterySample(**initdict)

    def has_unsaved_changes(self):
        return not self.recorded_samples == self.available_samples

    def _update_pandas_cache(self, source_data):
        source_json = [sample.dict() for sample in self.available_samples]
        source_json = json.loads(json.dumps(source_json, default=str))
        AVAIL_SAMPLES_DF = pd.json_normalize(source_json)
        dtype_dict = {
            col: typ
            for col, typ in BatterySampleJsonTypes.items()
            if col in AVAIL_SAMPLES_DF.columns
        }
        AVAIL_SAMPLES_DF = AVAIL_SAMPLES_DF.astype(dtype=dtype_dict)
        AVAIL_SAMPLES_DF["metadata.creation_datetime"] = pd.to_datetime(
            AVAIL_SAMPLES_DF["metadata.creation_datetime"])
        return AVAIL_SAMPLES_DF

    def query_available_samples(self, query=None, project=None):
        """
        This mock function returns the available samples.
            query: a pandas query
            project (optional): list of the columns to return (if None, return all)

        Returns a pandas.DataFrame or Series
        """
        # perform query
        if query is not None:
            results = self.available_samples_cache.query(query)
        else:
            results = self.available_samples_cache
        if project and (results is not None):
            if not isinstance(project, list):
                project = [project]
            return results[project]
        else:
            return results

    def write_pd_query_from_dict(self, query_dict):
        """
        Write a pandas query from a dictionary {field: value}.
        Example:
            write_pandas_query({'manufacturer': 'BIG-MAP', 'battery_id': 98})
        returns "(`manufacturer` == 'BIG-MAP') and (`battery_id` == 98)"
        """
        query = " and ".join([
            "(`{}` == {})".format(
                k, f"{v}" if isinstance(v, (int, float)) else f"'{v}'")
            for k, v in query_dict.items() if v
        ])
        if query:
            return query
