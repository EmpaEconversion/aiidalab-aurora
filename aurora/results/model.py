from __future__ import annotations

from datetime import datetime, timedelta
from json import load

import pandas as pd
from aiida.orm import Group, QueryBuilder
from aiida_aurora.calculations import BatteryCyclerExperiment
from aiida_aurora.data.battery import BatterySampleData
from traitlets import HasTraits, Unicode


class ResultsModel(HasTraits):
    """
    docstring
    """

    weights_file = Unicode("")

    def __init__(self) -> None:
        """docstring"""
        self.experiments = pd.DataFrame()
        self.results: dict[int, dict] = {}

    def get_weights(self, eid: int) -> dict[str, float]:
        """docstring"""
        sample_node = get_experiment_sample_node(eid)
        try:
            return get_weights_from_node(sample_node)
        except Exception:
            try:
                sample_name = sample_node['metadata']['name']
                return get_weights_from_file(sample_name, self.weights_file)
            except Exception:
                return {
                    "anode_mass": 1.,
                    "cathode_mass": 1.,
                }

    def update_experiments(self, group: str, last_days=999) -> None:
        """docstring"""

        if experiments := query_jobs(group, last_days):
            df = pd.DataFrame(experiments).sort_values('id')
            ctime = df['ctime'].dt.strftime('%Y-%m-%d %H:%m:%S')
            df['ctime'] = ctime
        else:
            df = pd.DataFrame()

        self.experiments = df

    @staticmethod
    def get_groups() -> list[str]:
        """docstring"""
        qb = QueryBuilder()
        qb.append(Group, filters={'label': {'like': '%Jobs'}})
        return [group.label for group in qb.all(flat=True)]


def query_jobs(
    group: str,
    last_days: int,
) -> list[BatteryCyclerExperiment]:
    """docstring"""

    qb = QueryBuilder()

    qb.append(Group, filters={'label': group}, tag='g')

    qb.append(
        BatteryCyclerExperiment,
        with_group='g',
        tag='jobs',
        project=[
            'id',
            'label',
            'ctime',
            'attributes.process_label',
            'attributes.state',
            'attributes.status',
            'extras.monitored',
        ],
    )

    qb.add_filter(
        'jobs',
        {
            'ctime': {
                '>=': datetime.now() - timedelta(days=last_days)
            },
        },
    )

    qb.add_filter('jobs', {'attributes.process_state': 'finished'})

    qb.order_by({'jobs': {'ctime': 'desc'}})

    return [query['jobs'] for query in qb.dict()]


def get_experiment_sample_node(eid: int) -> BatterySampleData:
    """docstring"""
    qb = QueryBuilder()
    qb.append(BatteryCyclerExperiment, filters={"id": eid}, tag="exp")
    qb.append(BatterySampleData, with_outgoing="exp")
    sample_node, = qb.first()
    return sample_node


def get_weights_from_node(sample_node: BatterySampleData) -> dict[str, float]:
    """docstring"""
    raw = sample_node.attributes
    return {
        "anode_mass": raw['anode_weight']['net'],
        "cathode_mass": raw['cathode_weight']['net'],
    }


def get_weights_from_file(sample_name: str, filename: str) -> dict[str, float]:
    """docstring"""
    with open(filename) as weights_file:
        weights = load(weights_file)
        return weights[sample_name]
