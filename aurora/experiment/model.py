from __future__ import annotations

from copy import deepcopy

from aiida import orm
from aiida.engine import submit
from aiida_aurora.data import (BatterySampleData, CyclingSpecsData,
                               TomatoSettingsData)
from aiida_aurora.schemas.battery import BatterySample
from aiida_aurora.schemas.cycling import ElectroChemSequence
from aiida_aurora.schemas.dgbowl import Tomato_0p2
from aiida_aurora.workflows import CyclingSequenceWorkChain
from traitlets import HasTraits

from aurora.common.groups import SAMPLES_GROUP_PREFIX
from aurora.experiment.builder.model import ExperimentBuilderModel

# TODO improve validation/node-storing order


class ExperimentModel(HasTraits):
    """docstring"""

    def __init__(
        self,
        builder: ExperimentBuilderModel,
    ) -> None:
        """`ExperimentModel` constructor.

        Parameters
        ----------
        `builder` : `ExperimentBuilderModel`
            The experiment builder.
        """
        self.builder = builder

    def get_codes(self) -> list[str]:
        """docstring"""
        return orm.QueryBuilder().append(
            orm.Code,
            filters={
                "attributes.input_plugin": "aurora.cycler",
            },
            project=["label"],
        ).all(flat=True)

    # TODO make async!
    def submit(
        self,
        code_name: str,
        unlock_when_done=False,
        group_label="",
    ) -> CyclingSequenceWorkChain:
        """docstring"""

        for sample in self.builder.get_samples():

            inputs = self.__build_inputs(
                sample,
                code_name,
                self.builder.get_protocols(),
                unlock_when_done,
            )
            inputs.update({"group_label": orm.Str(group_label)})

            self.__submit(inputs)

    ###########
    # PRIVATE #
    ###########

    def __build_inputs(
        self,
        sample: BatterySample,
        code_name: str,
        protocols: list[ElectroChemSequence],
        unlock_when_done,
    ) -> dict:
        """Prepare input dictionaries for workflow."""

        inputs = {
            "battery_sample": self.__build_sample_node(sample),
            "tomato_code": orm.load_code(code_name),
            "protocol_order": orm.List(),
            "protocols": {},
            "control_settings": {},
            "monitor_settings": {},
        }

        for i, protocol in enumerate(protocols):

            is_last_step = i == len(protocols) - 1

            step = protocol.name

            inputs["protocol_order"].append(step)

            inputs["protocols"][step] = self.__build_protocol_node(protocol)

            settings = self.builder.get_settings(step)
            settings.update({
                "unlock_when_done":
                unlock_when_done if is_last_step else True
            })
            settings_node = self.__build_settings_node(settings)
            inputs["control_settings"][step] = settings_node

            monitors = self.builder.get_monitors(step)
            monitors_node = self.__build_monitors_input(deepcopy(monitors))
            inputs["monitor_settings"][step] = monitors_node

        return inputs

    def __build_sample_node(self, sample: BatterySample) -> BatterySampleData:
        """Construct an AiiDA data node from battery sample data."""
        sample_node = BatterySampleData(sample.dict())
        sample_node.label = f"{sample.metadata.name} <{sample.id}>"
        sample_node.store()
        self.__add_sample_to_groups(sample.metadata.groups, sample_node)
        return sample_node

    def __add_sample_to_groups(
        self,
        groups: set[str],
        sample: BatterySampleData,
    ) -> None:
        """docstring"""
        for label in groups:
            label = f"{SAMPLES_GROUP_PREFIX}/{label}"
            orm.Group.collection.get_or_create(label)[0].add_nodes(sample)

    def __build_protocol_node(
        self,
        protocol: ElectroChemSequence,
    ) -> CyclingSpecsData:
        """Construct an AiiDA data node from cycling protocol data."""
        protocol_node = CyclingSpecsData(protocol.dict())
        protocol_node.label = protocol.name
        protocol_node.store()
        group = orm.Group.collection.get_or_create("aurora/protocols")[0]
        group.add_nodes(protocol_node)
        return protocol_node

    def __build_settings_node(self, settings: dict) -> TomatoSettingsData:
        """Construct an AiiDA data node from tomato settings data."""
        validated = Tomato_0p2.parse_obj(settings).dict()
        settings_node = TomatoSettingsData(validated)
        settings_node.store()
        return settings_node

    def __build_monitors_input(
        self,
        protocol_monitors: dict[str, dict],
    ) -> dict:
        """Construct a dictionary of `orm.Dict` monitors for the protocol."""

        monitors: dict[str, dict] = {}

        for label, monitor_settings in protocol_monitors.items():
            refresh_rate = monitor_settings.pop("refresh_rate", 600)
            monitors[label] = orm.Dict(
                label="monitor_settings",
                dict={
                    "entry_point": "aurora.monitors.capacity_threshold",
                    "minimum_poll_interval": refresh_rate,
                    "kwargs": {
                        "settings": monitor_settings,
                        "filename": "snapshot.json",
                    },
                },
            )

        return monitors

    def __submit(self, inputs: dict) -> CyclingSequenceWorkChain:
        """docstring"""
        workchain = submit(CyclingSequenceWorkChain, **inputs)
        sample_name = inputs["battery_sample"].label
        workchain.label = f"Experiment run on {sample_name}"
        print(f"Workflow <{workchain.pk}> submitted to AiiDA...")
        group = orm.Group.collection.get_or_create("aurora/workflows")[0]
        group.add_nodes(workchain)
        return workchain
