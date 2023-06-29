from datetime import datetime, timedelta
from typing import Dict, List

import pandas as pd
from aiida.orm import Group, QueryBuilder
from aiida_aurora.calculations import BatteryCyclerExperiment


class ResultsModel():
    """
    docstring
    """

    def __init__(self) -> None:
        """docstring"""
        self.experiments = pd.DataFrame()
        self.results: Dict[int, dict] = {}

    def update_experiments(self, last_days=0, group='pre_update') -> None:
        """docstring"""
        query = query_jobs(last_days, group)
        self.experiments = pd.DataFrame(query).sort_values('id')
        ctime = self.experiments['ctime'].dt.strftime('%Y-%m-%d %H:%m:%S')
        self.experiments['ctime'] = ctime


def query_jobs(last_days: int, group: Group) -> List[BatteryCyclerExperiment]:
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

    if last_days:
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
