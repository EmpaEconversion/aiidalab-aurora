from aiida.orm import QueryBuilder
from aiida_aurora.calculations.cycler import BatteryCyclerExperiment
from aiida_aurora.data.battery import BatterySampleData


def get_experiment_sample_id(eid: int) -> int:
    """docstring"""
    try:
        sample_name = get_experiment_sample_name(eid)
        return int(sample_name.split("-")[1])
    except Exception:
        return -1


def get_experiment_sample_name(eid: int) -> str:
    """docstring"""
    sample_node = get_experiment_sample_node(eid)
    return sample_node["metadata"]["name"]


def get_experiment_sample_node(eid: int) -> BatterySampleData:
    """docstring"""
    qb = QueryBuilder()
    qb.append(BatteryCyclerExperiment, filters={"id": eid}, tag="exp")
    qb.append(BatterySampleData, with_outgoing="exp")
    sample_node, = qb.first()
    return sample_node
