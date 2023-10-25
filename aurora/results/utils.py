from aiida.orm import QueryBuilder
from aiida_aurora.calculations.cycler import BatteryCyclerExperiment
from aiida_aurora.data.battery import BatterySampleData


def get_experiment_sample_node(eid: int) -> BatterySampleData:
    """docstring"""
    qb = QueryBuilder()
    qb.append(BatteryCyclerExperiment, filters={"id": eid}, tag="exp")
    qb.append(BatterySampleData, with_outgoing="exp")
    sample_node, = qb.first()
    return sample_node
