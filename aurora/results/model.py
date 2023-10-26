from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd
from aiida.orm import Group, QueryBuilder
from aiida_aurora.calculations import BatteryCyclerExperiment
from traitlets import HasTraits, Unicode

from aurora.common.groups import EXPERIMENTS_GROUP_PREFIX
from aurora.time import TZ

from .utils import get_experiment_sample_id, get_experiment_sample_node


class ResultsModel(HasTraits):
    """
    docstring
    """

    weights_file = Unicode("")

    def __init__(self) -> None:
        """docstring"""
        self.experiments = pd.DataFrame()
        self.results: dict[int, dict] = {}
        self.weights: dict[int, dict[str, float]] = {}

    def get_weights(self, eid: int) -> dict[str, float]:
        """docstring"""

        defaults = {
            "anode_mass": 1.,
            "cathode_mass": 1.,
        }

        if self.weights:
            try:
                return self.fetch_weights_from_file(eid)
            except Exception:
                return defaults

        try:
            return fetch_weights_from_node(eid)
        except Exception:
            return defaults

    def fetch_weights(self, filename: str) -> None:
        """docstring"""

        self.weights_file = filename

        with open(self.weights_file) as robot_output_csv:
            robot_output = pd.read_csv(robot_output_csv, sep=";")

        sample_id = robot_output["Battery_Number"].rename("sample_id")

        anode_net_weight = extract_weights_from_robot_output(
            robot_output,
            "anode_mass",
            "Anode Weight",
            "Anode Current Collector Weight (mg)",
        )

        cathode_net_weight = extract_weights_from_robot_output(
            robot_output,
            "cathode_mass",
            "Cathode Weight (mg)",
            "Cathode Current Collector Weight (mg)",
        )

        self.weights = pd.concat(
            [
                anode_net_weight,
                cathode_net_weight,
            ],
            axis=1,
        ).reindex(sample_id).to_dict("index")

    def fetch_weights_from_file(self, eid: int) -> dict[str, float]:
        """docstring"""
        sample_id = get_experiment_sample_id(eid)
        return self.weights[sample_id]

    def reset_weights(self) -> None:
        """docstring"""
        self.weights.clear()
        self.weights_file = ""

    def update_experiments(self, group: str, last_days: int) -> None:
        """docstring"""

        group_label = f"{EXPERIMENTS_GROUP_PREFIX}/{group}"
        if experiments := query_jobs(group_label, last_days):
            df = pd.DataFrame(experiments).sort_values("id")
            ctime = df["ctime"].dt.strftime(r"%Y-%m-%d %H:%m:%S")
            df["ctime"] = ctime
        else:
            df = pd.DataFrame()

        self.experiments = df

    @staticmethod
    def get_groups() -> list[str]:
        """docstring"""
        return [
            "all-experiments",
            *[
                group.label.removeprefix(f"{EXPERIMENTS_GROUP_PREFIX}/")
                for group in Group.collection.find({
                    "label": {
                        "and": [
                            {
                                "like": f"{EXPERIMENTS_GROUP_PREFIX}/%"
                            },
                            {
                                "!like": r"%all-experiments"
                            },
                        ],
                    },
                })
            ],
        ]

    # TODO move to AiiDA service
    @staticmethod
    def create_new_group(label: str, members: list[int]) -> None:
        """docstring"""

        nodes = QueryBuilder().append(
            BatteryCyclerExperiment,
            filters={
                "id": {
                    "in": members,
                },
            },
        ).all(flat=True)

        label = f"{EXPERIMENTS_GROUP_PREFIX}/{label}"
        group = Group.collection.get_or_create(label)[0]
        group.add_nodes(nodes)


def query_jobs(
    group: str,
    last_days: int,
) -> list[BatteryCyclerExperiment]:
    """docstring"""

    qb = QueryBuilder()

    qb.append(Group, filters={"label": group}, tag="g")

    qb.append(
        BatteryCyclerExperiment,
        with_group="g",
        tag="jobs",
        project=[
            "id",
            "label",
            "ctime",
            "attributes.process_label",
            "attributes.state",
            "attributes.status",
            "extras.monitored",
        ],
    )

    qb.add_filter(
        "jobs",
        {
            "ctime": {
                ">=": datetime.now(TZ).date() - timedelta(days=last_days)
            },
        },
    )

    qb.add_filter("jobs", {"attributes.process_state": "finished"})

    qb.order_by({"jobs": {"ctime": "desc"}})

    return [query["jobs"] for query in qb.dict()]


def fetch_weights_from_node(eid: int) -> dict[str, float]:
    """docstring"""
    node = get_experiment_sample_node(eid)
    composition = node.attributes["specs"]["composition"]
    return {
        "anode_mass": composition["anode"]["weight"]["net"],
        "cathode_mass": composition["cathode"]["weight"]["net"],
    }


def extract_weights_from_robot_output(
    robot_output: pd.DataFrame,
    series_name: str,
    weight_field: str,
    cc_weight_field: str,
) -> pd.Series:
    """docstring"""
    weight = robot_output[weight_field]
    cc_weight = robot_output[cc_weight_field]
    net_weight = (weight - cc_weight) / 1000  # in grams
    return pd.Series(name=series_name, data=net_weight)
