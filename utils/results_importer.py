from __future__ import annotations

import contextlib
import json
import re
from datetime import datetime

import numpy as np
import pandas as pd
from aiida.common import LinkType
from aiida.orm import (ArrayData, CalcJobNode, Code, Group, List, QueryBuilder,
                       Str, WorkChainNode, load_code)
from aiida_aurora.data import (BatterySampleData, CyclingSpecsData,
                               TomatoSettingsData)
from aiida_aurora.parsers import TomatoParser

from aurora.common.groups import EXPERIMENTS_GROUP_PREFIX, SAMPLES_GROUP_PREFIX
from aurora.time import TZ

# TODO Consider encapsulating in a class


def get_new_id() -> int:
    """Return the next available battery id.

    Counts `BatterySampleData` nodes and returns the value
    incremented by 1.

    Returns
    -------
    `int`
        An available battery id.
    """
    return QueryBuilder().append(BatterySampleData, ).count() + 1


def read_batch_specs(path: str) -> pd.DataFrame:
    """Fetch the batch specs from robot output.

    Parameters
    ----------
    `batch_name` : `str`
        The batch name.

    Returns
    -------
    `pd.DataFrame`
        The batch specs dataframe.
    """
    with open(f"{path}.specs.csv") as robot_output:
        specs = pd.read_csv(robot_output, sep=";")
        specs.set_index("Battery_Number", inplace=True)
    return specs


def build_sample_node(
    sample_name: str,
    specs: pd.DataFrame,
) -> BatterySampleData:
    """Build a sample node from provided specs.

    Parameters
    ----------
    `sample_name` : `str`
        The sample name in `<batch>-<#>` format.
    `specs` : `pd.DataFrame`
        A dataframe of battery specs for the batch.

    Returns
    -------
    `BatterySampleData`
        A sample node.
    """

    batch_id, battery_number = sample_name.split("-")

    df = specs.query(f"(Battery_Number == {str(battery_number)})").iloc[0]

    anode_W = df['Anode Weight'] / 1000
    cathode_W = df['Cathode Weight (mg)'] / 1000
    anode_cc_W = df['Anode Current Collector Weight (mg)'] / 1000
    cathode_cc_W = df['Cathode Current Collector Weight (mg)'] / 1000
    anode_net_W = anode_W - anode_cc_W
    cathode_net_W = cathode_W - cathode_cc_W
    anode_practical_C = df['Anode Practical Capacity (mAh/g)']
    cathode_practical_C = df['Cathode Practical Capacity (mAh/g)']
    anode_C = anode_net_W * anode_practical_C
    cathode_C = cathode_net_W * cathode_practical_C
    C = np.round(np.min((anode_C, cathode_C), axis=0), 3)

    now = datetime.now(TZ)

    sample = BatterySampleData(
        label=sample_name,
        dict={
            "id": get_new_id(),
            "specs": {
                "manufacturer": "Empa",
                "case": str(df["Casing Type"]),
                "composition": {
                    "description": "Li-based",
                    "anode": {
                        "formula": str(df["Anode Type"]),
                        "position": df["Anode Position"],
                        "diameter": {
                            "nominal": df["Anode Diameter"],
                        },
                        "weight": {
                            "total": anode_W,
                            "collector": anode_cc_W,
                            "net": anode_net_W,
                            "units": "g",
                        },
                        "capacity": {
                            "nominal": anode_practical_C,
                        },
                    },
                    "cathode": {
                        "formula": str(df["Cathode Type"]),
                        "position": df["Cathode Position"],
                        "diameter": {
                            "nominal": df["Cathode Diameter (mm)"],
                        },
                        "weight": {
                            "total": cathode_W,
                            "collector": cathode_cc_W,
                            "net": cathode_net_W,
                            "units": "g",
                        },
                        "capacity": {
                            "nominal": cathode_practical_C,
                        },
                    },
                    "electrolyte": {
                        "formula": str(df["Electrolyte"]),
                        "position": df["Electrolyte Position"],
                        "amount": df["Electrolyte Amount"],
                    },
                    "separator": {
                        "name": str(df["Separator"]),
                        "diameter": {
                            "nominal": df["Separator Diameter (mm)"],
                        },
                    },
                    "spacer": {
                        "value": df["Spacer (mm)"],
                    }
                },
                "capacity": {
                    "nominal": C,
                    "units": "mAh",
                },
            },
            "metadata": {
                "name": sample_name,
                "batch": batch_id,
                "subbatch": str(df["Subbatch"]),
                "creation_datetime": now,
                "creation_process": "ECLab->AiiDA conversion script.",
            },
        },
    )

    sample.store()

    group_label = f"{SAMPLES_GROUP_PREFIX}/all-samples"
    Group.collection.get_or_create(group_label)[0].add_nodes(sample)

    return sample


def build_protocol_order_node(protocol_name: str) -> List:
    """Build an ordered list of protocols.

    NOTE: currently only supports a single protocol.

    Parameters
    ----------
    `protocol_name` : `str`
        The name of the protocol.

    Returns
    -------
    `List`
        A list node containing the protocol name.
    """
    protocol_order = List([protocol_name])
    protocol_order.store()
    return protocol_order


def build_protocol_node(protocol_name: str) -> CyclingSpecsData:
    """Build a protocol node.

    NOTE: currently fakes the protocol. More details required
    to construct an accurate protocol node.

    Parameters
    ----------
    `protocol_name` : `str`
        The name of the protocol.

    Returns
    -------
    `CyclingSpecsData`
        A protocol node.
    """

    protocol = CyclingSpecsData(
        label=protocol_name,
        dict={
            "name":
            protocol_name,
            "method": [
                {
                    "name": "unknown",
                    "device": "worker",
                    "technique": "sequential",
                    "parameters": {
                        "time": {
                            "label": "Time:",
                            "units": "s",
                            "value": 1.0,
                            "required": True,
                            "description": "",
                            "default_value": 100.0
                        },
                        "delay": {
                            "label": "Delay:",
                            "units": "s",
                            "value": 1.0,
                            "required": True,
                            "description": "",
                            "default_value": 1.0
                        },
                    },
                    "short_name": "DUMMY_SEQUENTIAL",
                    "description": "unknown"
                },
            ],
        },
    )

    protocol.store()

    group = Group.collection.get_or_create("aurora/protocols")[0]
    group.add_nodes(protocol)

    return protocol


def build_settings_node() -> TomatoSettingsData:
    """Build a settings node.

    NOTE: currently fakes the settings. More details required
    to construct an accurate settings node.

    Returns
    -------
    `TomatoSettingsData`
        The settings node.
    """

    settings = TomatoSettingsData({
        "output": {
            "path": None,
            "prefix": None
        },
        "snapshot": None,
        "verbosity": "INFO",
        "unlock_when_done": True,
    })

    settings.store()

    return settings


def build_workchain_node(
    code: Code,
    sample: BatterySampleData,
    protocol_order: List,
    protocol: CyclingSpecsData,
    settings: TomatoSettingsData,
    group_label: Str,
) -> WorkChainNode:
    """Build a workchain node from constructed input nodes.

    Parameters
    ----------
    `code` : `Code`
        The tomato code.
    `sample` : `BatterySampleData`
        The sample node.
    `protocol_order` : `List`
        The ordered protocol list node.
    `protocol` : `CyclingSpecsData`
        The protocol node.
    `settings` : `TomatoSettingsData`
        The settings node.
    `group_label` : `Str`
        A string node representing the group label used by
        the workchain to auto-generate experiment groups.

    Returns
    -------
    `WorkChainNode`
        A workchain node.
    """

    workchain_node = WorkChainNode(label=f"Experiment run on {sample.label}")

    workchain_node.set_process_type("aiida.workflows:aurora.cycling_sequence")
    workchain_node.set_process_label("CyclingSequenceWorkChain")
    workchain_node.set_process_state("finished")

    workchain_node.base.links.add_incoming(
        code,
        link_type=LinkType.INPUT_WORK,
        link_label="tomato_code",
    )

    workchain_node.base.links.add_incoming(
        sample,
        link_type=LinkType.INPUT_WORK,
        link_label="battery_sample",
    )

    workchain_node.base.links.add_incoming(
        protocol_order,
        link_type=LinkType.INPUT_WORK,
        link_label="protocol_order",
    )

    workchain_node.base.links.add_incoming(
        protocol,
        link_type=LinkType.INPUT_WORK,
        link_label=f"protocols__{protocol.label}",
    )

    workchain_node.base.links.add_incoming(
        settings,
        link_type=LinkType.INPUT_WORK,
        link_label=f"control_settings__{protocol.label}",
    )

    workchain_node.base.links.add_incoming(
        group_label,
        link_type=LinkType.INPUT_WORK,
        link_label="group_label",
    )

    workchain_node.store()

    group = Group.collection.get_or_create("aurora/workflows")[0]
    group.add_nodes(workchain_node)

    return workchain_node


def build_cycling_node(
    code: Code,
    sample: BatterySampleData,
    protocol: CyclingSpecsData,
    settings: TomatoSettingsData,
    workchain_node: WorkChainNode,
    group_label: str,
) -> CalcJobNode:
    """Build a calcjob node.

    Parameters
    ----------
    `code` : `Code`
        The tomato code.
    `sample` : `BatterySampleData`
        The sample node.
    `protocol` : `CyclingSpecsData`
        The protocol node.
    `settings` : `TomatoSettingsData`
        The settings node.
    `workchain_node` : `WorkChainNode`
        The workchain node.
    `group_label` : `str`
        The group label node.

    Returns
    -------
    `CalcJobNode`
        A calcjob node.
    """

    cycling_node = CalcJobNode(label=f"{protocol.label} | {sample.label}")

    cycling_node.set_process_type("aiida.calculations:aurora.cycler")
    cycling_node.set_process_label("BatteryCyclerExperiment")
    cycling_node.set_process_state("finished")

    cycling_node.base.links.add_incoming(
        code,
        link_type=LinkType.INPUT_CALC,
        link_label="code",
    )

    cycling_node.base.links.add_incoming(
        sample,
        link_type=LinkType.INPUT_CALC,
        link_label="battery_sample",
    )

    cycling_node.base.links.add_incoming(
        protocol,
        link_type=LinkType.INPUT_CALC,
        link_label="protocol",
    )

    cycling_node.base.links.add_incoming(
        settings,
        link_type=LinkType.INPUT_CALC,
        link_label="control_settings",
    )

    cycling_node.base.links.add_incoming(
        workchain_node,
        link_type=LinkType.CALL_CALC,
        link_label="workchain",
    )

    cycling_node.store()

    for label in (
            "all-experiments",
            protocol.label,
            group_label,
            f"{group_label}/{protocol.label}",
    ):
        label = f"{EXPERIMENTS_GROUP_PREFIX}/{label}"
        Group.collection.get_or_create(label)[0].add_nodes(cycling_node)

    return cycling_node


def build_results_node(
    raw: dict,
    workchain_node: WorkChainNode,
    cycling_node: CalcJobNode,
    protocol_name: str,
) -> ArrayData:
    """Build a results node.

    Parameters
    ----------
    `raw` : `dict`
        A raw results dictionary.
    `workchain_node` : `WorkChainNode`
        The workchain node.
    `cycling_node` : `CalcJobNode`
        The calcjob node.
    `protocol_name` : `str`
        The protocol name.

    Returns
    -------
    `ArrayData`
        A results node.
    """

    data_node: ArrayData = TomatoParser.parse_tomato_results(raw)

    data_node.base.links.add_incoming(
        cycling_node,
        link_type=LinkType.CREATE,
        link_label="results",
    )

    data_node.store()

    data_node.base.links.add_incoming(
        workchain_node,
        link_type=LinkType.RETURN,
        link_label=f"results__{protocol_name}",
    )


def load_ec_lab_experiment_into_aiida(
    path: str,
    batch_specs: pd.DataFrame,
    c_date: str,
) -> None:
    """Load raw `.json` results into AiiDA.

    This function loads and uses the JSON results to create AiiDA
    nodes for the sample, the protocol (and order), the tomato settings,
    the workchain, and the calculation job, linking all nodes together
    as if they were executed via Aurora.

    Parameters
    ==========
    `path` : `str`
        The path to the results JSON file.
    `batch_specs` : `pd.DataFrame`
        A dataframe of the robot output for the current batch
    """

    print(f"processing {path}")

    with open(path) as ec_lab_results_file:
        raw = json.load(ec_lab_results_file)

    sample_name: str | None = None

    with contextlib.suppress(Exception):
        step = raw["metadata"]["input_schema"]["steps"][0]
        filename = step["input"]["files"][0]
        if match := re.search(r"\d{6}-\d+", filename):
            sample_name = match.group()

    if sample_name is None:
        return print("Could not detect sample name")

    sample = build_sample_node(sample_name, batch_specs)

    protocol_name = "cycling"

    protocol_order = build_protocol_order_node(protocol_name)

    protocol = build_protocol_node(protocol_name)

    settings = build_settings_node()

    code = load_code("ketchup-0.2rc2@localhost-tomato")

    group_label = Str(c_date)
    group_label.store()

    workchain_node = build_workchain_node(
        code,
        sample,
        protocol_order,
        protocol,
        settings,
        group_label,
    )

    cycling_node = build_cycling_node(
        code,
        sample,
        protocol,
        settings,
        workchain_node,
        group_label.value,
    )

    build_results_node(
        raw,
        workchain_node,
        cycling_node,
        protocol_name,
    )


def natural_sort(filenames: list[str]) -> list[str]:
    """Return filenames sorted in natural order.

    Sorter assumes a filename convention similar
    to `<date>_NMC-G-<sample#>_pruned.json`.

    If issues arise, original, unordered filenames are returned.
    """
    try:
        sorter = lambda fn: int(fn.split("-")[-1].split("_")[0])  # noqa
        return sorted(filenames, key=sorter)
    except Exception:
        return filenames
