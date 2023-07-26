import json
import logging
from typing import List, Optional, Union

import pandas as pd
from aiida_aurora.schemas.battery import (BatterySampleJsonTypes,
                                          BatterySpecsJsonTypes)
from aiida_aurora.schemas.cycling import (ElectroChemSequence,
                                          OpenCircuitVoltage)
from IPython.display import display

AVAILABLE_SAMPLES_FILE = 'available_samples.json'

STD_RECIPIES = {
    'Load fresh battery into cycler':
    ['Request the user to load a battery with the desired specs.'],
    'Synthesize - Recipe 1': ['step 1', 'step 2', 'step 3'],
    'Synthesize - Recipe 2': ['step 1', 'step 2', 'step 3'],
}

STD_PROTOCOLS = {
    "Formation cycles": {
        "Procedure": [
            "6h rest", "CCCV Charge, C/10 (CV condition: i<C/50)",
            "CC Discharge, D/10", "Repeat 3 times"
        ],
        "Cutoff conditions":
        "2.5 to 4.2 V, upper voltage to be changed depending on the chemistry",
    },
    "Power test Charge focus": {
        "Procedure": [
            "6h rest", "CC Charge (CV condition: i<C/50)", "(C/20 + D/20) x 5",
            "(C/10 + D/20) x 5", "(C/5 + D/20) x 5", "(C/2 + D/20) x 5",
            "(1C + D/20) x 5", "(2C + D/20) x 5", "(5C + D/20) x 5",
            "(C/20 + D/20) x 5"
        ],
        "Cutoff conditions":
        "2.5 to 4.2 V, upper voltage to be changed depending on the chemistry",
    },
    "Power test Discharge focus": {
        "Procedure": [
            "6h rest", "CCCV Charge (CV condition: i<C/50)",
            "(C/20 + D/20) x 5", "(C/20 + D/10) x 5", "(C/20 + D/50) x 5",
            "(C/20 + D/2) x 5", "(C/20 + 1D) x 5", "(C/20 + 2D) x 5",
            "(C/20 + 5D) x 5", "(C/20 + D/20) x 5"
        ],
        "Cutoff conditions":
        "2.5 to 4.2 V, upper voltage to be changed depending on the chemistry",
    },
}


class BatteryExperimentModel():
    """The model that controls the submission of a process for a set of batteries."""

    def __init__(self):
        self.DEFAULT_PROTOCOL = OpenCircuitVoltage

        self.list_of_observers = []
        self.list_of_observations = []

        self.available_samples = None
        self.available_specs = None
        self.available_recipies = None
        self.available_protocols = None

        self.update_available_samples()
        self.update_available_specs()
        self.update_available_recipies()
        self.update_available_protocols()

        self.selected_samples = []
        self.selected_protocol = ElectroChemSequence(method=[])
        self.add_protocol_step()  # initialize sequence with first default step

    # ----------------------------------------------------------------------#
    # METHODS RELATED TO OBSERVABLES
    # ----------------------------------------------------------------------#
    def suscribe_observer(self, observer):
        if observer not in self.list_of_observers:
            self.list_of_observers.append(observer)

    def unsuscribe_observer(self, observer):
        if observer in self.list_of_observers:
            self.list_of_observers.remove(observer)

    def update_observers(self, observators_chain=None):
        if observators_chain is not None:
            self.list_of_observations.append(observators_chain)
        for observer in self.list_of_observers:
            observer.update()

    # ----------------------------------------------------------------------#
    # METHODS RELATED TO SAMPLES
    # ----------------------------------------------------------------------#
    def reset_inputs(self):
        """Resets all inputs."""
        # Not implemented yet...
        return None

    def add_selected_samples(self, sample_ids: List[int]) -> None:
        """Add selected samples to list.

        Parameters
        ----------
        `sample_ids` : `Tuple[int]`
            The ids of the selected samples.
        """

        for sid in sample_ids:
            self.add_selected_sample(sid)

    def add_selected_sample(self, battery_sample_id, observators_chain=None):
        """Description pending."""
        for index, row in self.selected_samples.iterrows():
            if row.battery_id == battery_sample_id:
                return None

        sample_in_available = None
        for index, row in self.available_samples.iterrows():
            if row.battery_id == battery_sample_id:
                sample_in_available = row

        if sample_in_available is None:
            raise ValueError('A PROBLEM!')

        new_index = len(self.selected_samples)
        self.selected_samples.loc[new_index] = sample_in_available
        self.selected_samples = self.selected_samples.sort_values(
            by=['battery_id'])
        if observators_chain is None:
            observators_chain = ''
        observators_chain += ' -> add_selected_sample'
        self.update_observers(observators_chain)

    def remove_selected_samples(self, sample_ids: List[int]) -> None:
        """Remove selected samples from list.

        Parameters
        ----------
        `sample_ids` : `Tuple[int]`
            The ids of the selected samples.
        """

        for sid in sample_ids:
            self.remove_selected_sample(sid)

    def remove_selected_sample(self,
                               battery_sample_id,
                               observators_chain=None):
        """Description pending."""

        drop_index = None
        for index, row in self.selected_samples.iterrows():
            if row.battery_id == battery_sample_id:
                drop_index = index
                break

        if drop_index is not None:
            self.selected_samples = self.selected_samples.drop(
                index=drop_index)
            self.selected_samples = self.selected_samples.reset_index(
                drop=True)
            # Pandas needs drop = True because of reasons... should stop using pandas
            # https://stackoverflow.com/questions/12203901/pandas-crashes-on-repeated-dataframe-reset-index
        if observators_chain is None:
            observators_chain = ''
        observators_chain += ' -> remove_selected_sample'
        self.update_observers(observators_chain)

    def update_available_samples(self,
                                 source_file=AVAILABLE_SAMPLES_FILE,
                                 observators_chain=None):
        # AVAIL_SAMPLES = [BatterySample.parse_obj(dic) for dic in json.load(open('available_samples.json', 'r'))]
        # AVAIL_SAMPLES_D = {battery_id: BatterySample.parse_obj(dic) for battery_id, dic in json.load(open('available_samples_id.json', 'r')).items()}
        with open(source_file) as f:
            data = json.load(f)
        # load json and enforce data types
        AVAIL_SAMPLES_DF = pd.json_normalize(data)
        AVAIL_SAMPLES_DF = AVAIL_SAMPLES_DF.astype(
            dtype={
                col: typ
                for col, typ in BatterySampleJsonTypes.items()
                if col in AVAIL_SAMPLES_DF.columns
            })
        AVAIL_SAMPLES_DF["metadata.creation_datetime"] = pd.to_datetime(
            AVAIL_SAMPLES_DF["metadata.creation_datetime"])
        self.available_samples = AVAIL_SAMPLES_DF
        self.selected_samples = AVAIL_SAMPLES_DF[0:0]
        if observators_chain is None:
            observators_chain = ''
        observators_chain += ' -> update_available_samples'
        self.update_observers(observators_chain)

    def update_available_specs(
        self,
        observer_chain: Optional[str] = None,
    ) -> None:
        """Fetch available specs from local CSV file and store in a
        `pandas.DataFrame`. Update observers with the current state
        of the observer chain.

        NOTE: specs should be stored in and fetched from a database.

        Parameters
        ----------
        observer_chain : `Optional[str]`
            A string representation of a chain of observers,
            `None` by default.
        """

        STD_SPECS = pd.read_csv(
            'example_specs.csv',
            dtype=BatterySpecsJsonTypes,
        )
        self.available_specs = STD_SPECS

        if observer_chain is None:
            observer_chain = ''

        observer_chain += ' -> update_available_specs'

        self.update_observers(observer_chain)

    def update_available_recipies(self, observators_chain=None):
        global STD_RECIPIES
        self.available_recipies = STD_RECIPIES.copy()
        if observators_chain is None:
            observators_chain = ''
        observators_chain += ' -> update_available_recipies'
        self.update_observers(observators_chain)

    def update_available_protocols(self, observators_chain=None):
        global STD_PROTOCOLS
        self.available_protocols = STD_PROTOCOLS.copy()
        if observators_chain is None:
            observators_chain = ''
        observators_chain += ' -> update_available_protocols'
        self.update_observers(observators_chain)

    def query_available_specs(
        self,
        field: Optional[str] = None,
    ) -> pd.DataFrame:
        """Fetch available specs. If given, filter results for a
        specific spec.

        Parameters
        ----------
        `field` : `Optional[str]`
            A spec name, `None` by default. If present, filter query
            result for this spec.

        Returns
        -------
        `pandas.DataFrame`
            A dataframe of allowed specs, optionally filtered.
        """

        if field:
            return self.available_specs.get(field).unique().tolist()

        return self.available_specs

    def query_available_samples(
        self,
        query: Optional[str] = None,
        project: Optional[Union[str, List[str]]] = None,
    ) -> pd.DataFrame:
        """Fetch available samples, optionally filtered by a set of
        conditions. Return specific columns if requested.

        Parameters
        ----------
        `query` : `Optional[str]`
            A `pandas` query, `None` by default. If present, filter
            available samples by these conditions.
        `project` : `Optional[Union[str, List[str]]]`
            A list of the columns to return, `None` by default, which
            returns all columns.

        Returns
        -------
        `pandas.DataFrame`
            A dataframe of available samples, optionally filtered.
        """

        if query is not None:
            results = self.available_samples.query(query)
        else:
            results = self.available_samples
        if project and (results is not None):
            if not isinstance(project, list):
                project = [project]
            return results[project]
        else:
            return results

    def query_available_recipies(self):
        """A mock function that returns the available synthesis recipies."""
        return self.available_recipies

    def query_available_protocols(self):
        """A mock function that returns the available synthesis recipies."""
        return self.available_protocols

    def write_pd_query_from_dict(self, query_dict: dict) -> Optional[str]:
        """Convert a dictionary of query conditions to a string of
        'and'-separated `pandas.DataFrame`-compatible conditions.

        Parameters
        ----------
        `query_dict` : `dict`
            A dictionary of query conditions.

        Returns
        -------
        `Optional[str]`
            An 'and'-separated string representation of the query
            required for querying a `pandas.DataFrame` object.

        Example
        -------
        >>> query_dict = {'manufacturer': 'BIG-MAP', 'battery_id': 98}
        >>> write_pandas_query(query_dict)
        >>> "(`manufacturer` == 'BIG-MAP') and (`battery_id` == 98)"
        """

        query = " and ".join(
            [f"(`{k}` == {v})" for k, v in _process_dict(query_dict).items()])

        return query or None

    def display_query_results(self, query: dict) -> None:
        """Display query results in a pandas table."""

        pd_query = self.write_pd_query_from_dict(query)
        df = self.query_available_samples(pd_query)

        if df is None:
            return

        col = df.pop("battery_id")
        df.insert(0, col.name, col)

        display(
            df.rename(
                columns={
                    "battery_id": 'id',
                    "form_factor": 'form factor',
                    "composition.description": 'composition',
                    "capacity.nominal": 'C nominal',
                    "capacity.actual": 'C actual',
                    "capacity.units": 'C units',
                    "metadata.name": 'name',
                    "metadata.creation_datetime": 'creation date',
                    "metadata.creation_process": 'creation process',
                }).style.set_table_styles([
                    dict(
                        selector='th',
                        props=[
                            ('text-align', 'center'),
                            ("width", "100vw"),
                        ],
                    ),
                    dict(
                        selector='td',
                        props=[
                            ('text-align', 'center'),
                            ("width", "100vw"),
                        ],
                    )
                ]).hide_index())

    # ----------------------------------------------------------------------#
    # METHODS RELATED TO PROTOCOLS
    # ----------------------------------------------------------------------#
    def _count_technique_occurencies(self, technique):
        return [type(step)
                for step in self.selected_protocol.method].count(technique)
        # return [type(step) for step in self.protocol_steps_list.method].count(technique)

    def DEFAULT_STEP_NAME(self, technique):
        return f"{technique.schema()['properties']['short_name']['default']}_{self._count_technique_occurencies(technique) + 1}"

    def add_protocol_step(self, protocol=None):
        name = self.DEFAULT_STEP_NAME(self.DEFAULT_PROTOCOL)
        logging.debug(f"Adding protocol step {name}")
        if protocol is None:
            protocol = self.DEFAULT_PROTOCOL(name=name)
        self.selected_protocol.add_step(protocol)
        self.update_observers()

    def remove_protocol_step(self, protocol_index):
        if self.selected_protocol.n_steps > 1:
            self.selected_protocol.remove_step(protocol_index)
            self.update_observers()

    def move_protocol_step_up(self, protocol_index):
        self.selected_protocol.move_step_backward(protocol_index)
        self.update_observers()

    def move_protocol_step_down(self, protocol_index):
        self.selected_protocol.move_step_forward(protocol_index)
        self.update_observers()

    def load_protocol(self, filepath):
        """Loads the protocol from a file."""
        if filepath is None:
            return

        with open(filepath) as fileobj:
            json_data = json.load(fileobj)

        self.selected_protocol = ElectroChemSequence(**json_data)
        self.update_observers()

    def save_protocol(self, filepath):
        """Saves the protocol from a file."""
        if filepath is None:
            return

        try:
            json_data = json.dumps(self.selected_protocol.dict(), indent=2)
        except Exception as err:
            json_data = str(err)

        with open(filepath, 'w') as fileobj:
            fileobj.write(str(json_data))


def _process_dict(query_dict: dict) -> dict:
    """Process query dictionary, wrapping all strings in quotes.

    Parameters
    ----------
    `query_dict` : `dict`
        Dictionary containing query key|value pairs.

    Returns
    -------
    `dict`
        The processed dictionary, with strings wrapped in quotes.
    """
    return {
        k: [_cast(v_) for v_ in v] if isinstance(v, list) else _cast(v)
        for k, v in query_dict.items() if v is not None
    }


def _cast(v: Union[int, float, str]) -> Union[int, float, str]:
    """Return `int|float` as is; surround in quotes if `str`.

    Parameters
    ----------
    `v` : `Union[int, float, str]`
        The value to cast.

    Returns
    -------
    `Union[int, float, str]`
        The casted value.
    """
    return f"'{v}'" if isinstance(v, str) else v
