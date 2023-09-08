from typing import Dict, List, Optional

from aiida.engine import submit
from aiida.manage.configuration import load_profile
from aiida.orm import Dict as AiiDADict
from aiida.orm import List as AiiDAList
from aiida.orm import QueryBuilder, load_code, load_group
from aiida_aurora.data import (BatterySampleData, CyclingSpecsData,
                               TomatoSettingsData)
from aiida_aurora.schemas.battery import BatterySample
from aiida_aurora.schemas.cycling import ElectroChemSequence
from aiida_aurora.schemas.dgbowl import Tomato_0p2
from aiida_aurora.workflows import CyclingSequenceWorkChain

load_profile()

SAMPLES_GROUP = load_group("BatterySamples")
PROTOCOLS_GROUP = load_group("CyclingSpecs")
WORKFLOWS_GROUP = load_group("WorkChains")


def submit_experiment(
    sample: BatterySample,
    protocols: List[ElectroChemSequence],
    settings: List[Tomato_0p2],
    monitors: List[dict],
    code_name: str,
    sample_node_label="",
    protocol_node_label="",
    workchain_node_label="",
) -> CyclingSequenceWorkChain:
    """
    sample : `aiida_aurora.schemas.battery.BatterySample`
    method : `aiida_aurora.schemas.cycling.ElectroChemSequence`
    tomato_settings : `aiida_aurora.schemas.dgbowl_schemas.Tomato_0p2`
    """

    inputs = get_inputs(
        sample,
        sample_node_label,
        code_name,
        protocols,
        settings,
        monitors,
        protocol_node_label,
    )

    return submit_job(inputs, workchain_node_label)


def get_inputs(
    sample: BatterySample,
    sample_node_label: str,
    code_name: str,
    protocols: List[ElectroChemSequence],
    settings: List[Tomato_0p2],
    monitors: List[dict],
    protocol_node_label: str,
) -> dict:
    """Prepare input dictionaries for workflow."""

    inputs = {
        "battery_sample": build_sample_node(sample, sample_node_label),
        "tomato_code": load_code(code_name),
        "protocol_order": AiiDAList(),
        "protocols": {},
        "control_settings": {},
        "monitor_settings": {},
    }

    # push cycler locking (if requested) to final workflow step
    if any(not ts.unlock_when_done for ts in settings):
        for ts in settings:
            ts.unlock_when_done = True
        settings[-1].unlock_when_done = False

    for protocol, settings, protocol_monitors in zip(
            protocols,
            settings,
            monitors,
    ):

        step = protocol.name

        inputs["protocol_order"].append(step)

        inputs["protocols"][step] = build_protocol_node(
            protocol,
            protocol_node_label,
        )

        inputs["control_settings"][step] = build_settings_node(settings)

        inputs["monitor_settings"][step] = build_monitors_input(
            protocol,
            protocol_monitors,
        )

    return inputs


def build_sample_node(
    sample: BatterySample,
    sample_node_label: str,
) -> BatterySampleData:
    """Construct an AiiDA data node from battery sample data."""
    if existing := fetch_sample_if_existing(sample.battery_id):
        return existing
    sample_node = BatterySampleData(sample.dict())
    label = f"{sample.metadata.name} <{sample.battery_id}>"
    sample_node.label = sample_node_label or label
    sample_node.store()
    SAMPLES_GROUP.add_nodes(sample_node)
    return sample_node


def fetch_sample_if_existing(bid: int) -> Optional[BatterySampleData]:
    """Return protocol if already exists."""
    qb = QueryBuilder()
    qb.append(BatterySampleData, filters={"attributes.battery_id": bid})
    return qb.first(flat=True)


def build_protocol_node(
    protocol: ElectroChemSequence,
    protocol_node_label: str,
) -> CyclingSpecsData:
    """Construct an AiiDA data node from cycling protocol data."""
    if existing := fetch_protocol_if_existing(protocol.name):
        return existing
    protocol_node = CyclingSpecsData(protocol.dict())
    protocol_node.label = protocol_node_label or protocol.name
    protocol_node.store()
    PROTOCOLS_GROUP.add_nodes(protocol_node)
    return protocol_node


def fetch_protocol_if_existing(name: str) -> Optional[CyclingSpecsData]:
    """Return protocol if already exists."""
    qb = QueryBuilder()
    qb.append(CyclingSpecsData, filters={"attributes.name": name})
    return qb.first(flat=True)


def build_settings_node(settings: Tomato_0p2) -> TomatoSettingsData:
    """Construct an AiiDA data node from tomato settings data."""
    settings_node = TomatoSettingsData(settings.dict())
    settings_node.store()
    return settings_node


def build_monitors_input(
    protocol: ElectroChemSequence,
    protocol_monitors: Dict[str, dict],
) -> dict:
    """Construct a dictionary of `Dict` monitors for the protocol."""

    monitors: Dict[str, dict] = {}

    for label, monitor_settings in protocol_monitors.items():
        refresh_rate = monitor_settings.pop("refresh_rate", 600)
        monitor_name = f"{protocol.name}_{label}"
        monitors[monitor_name] = AiiDADict(
            dict={
                "entry_point": "aurora.monitors.capacity_threshold",
                "minimum_poll_interval": refresh_rate,
                "kwargs": {
                    "settings": monitor_settings,
                    "filename": "snapshot.json",
                },
            })

    return monitors


def submit_job(
    inputs: dict,
    workchain_node_label: str,
) -> CyclingSequenceWorkChain:
    """docstring"""
    workchain = submit(CyclingSequenceWorkChain, **inputs)
    sample_name = inputs["battery_sample"].label
    label = f"Experiment run on {sample_name}"
    workchain.label = workchain_node_label or label
    print(f"Workflow <{workchain.pk}> submitted to AiiDA...")
    WORKFLOWS_GROUP.add_nodes(workchain)
    return workchain
