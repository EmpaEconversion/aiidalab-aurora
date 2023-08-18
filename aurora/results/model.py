from datetime import datetime, timedelta
from typing import Dict, List

import pandas as pd
from aiida.orm import Group, QueryBuilder
from aiida_aurora.calculations import BatteryCyclerExperiment


class ResultsModel:
    """
    docstring
    """

    def __init__(self) -> None:
        """docstring"""
        self.experiments = pd.DataFrame()
        self.results: Dict[int, dict] = {}

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
    def get_groups() -> List[str]:
        """docstring"""
        qb = QueryBuilder()
        qb.append(Group, filters={'label': {'like': '%Jobs'}})
        return [group.label for group in qb.all(flat=True)]


def query_jobs(
    group: str,
    last_days: int,
) -> List[BatteryCyclerExperiment]:
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
