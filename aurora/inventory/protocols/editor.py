from typing import get_args

import ipywidgets as ipw
from aiida_aurora.schemas.cycling import (CyclingTechnique,
                                          ElectroChemPayloads,
                                          ElectroChemSequence,
                                          OpenCircuitVoltage)

from aurora.common.models import ProtocolsModel

from .techniques import TechniqueParametersWidget

BOX_LAYOUT = {
    "width": "auto",
}

BOX_STYLE = {
    "description_width": "initial",
}

BUTTON_LAYOUT = {
    "margin": "5px",
    "width": "40%",
}

BUTTON_LAYOUT = {
    "width": "fit-content",
}


class ProtocolEditor(ipw.Accordion):
    """An editor to create new or edit existing cycling protocols."""

    def __init__(self, protocols_model: ProtocolsModel):
        """`ProtocolsManager` constructor.

        Parameters
        ----------
        `protocols_model` : `ProtocolsModel`
            The manager's local protocols model.
        """

        self.edit = False

        self.protocols_model = protocols_model

        self.protocol = ElectroChemSequence(method=[])

        self.warning_notice = ipw.Output()

        self.name_label = ipw.Label(value="Protocol name:")

        self.name = ipw.Text(
            layout={
                "width": "auto",
                "margin": "0 2px",
            },
            placeholder="Enter protocol name",
        )

        self.sequence_label = ipw.Label(value="Sequence:")

        self.sequence = ipw.Select(
            layout={
                "width": "auto",
                "margin": "0 2px",
            },
            rows=10,
            value=None,
            description="",
        )

        self.technique_action_info = ipw.HTML()

        self.add_button = ipw.Button(
            layout=BUTTON_LAYOUT,
            button_style="warning",
            icon="plus",
            tooltip="Add step",
        )

        self.remove_button = ipw.Button(
            layout=BUTTON_LAYOUT,
            button_style="danger",
            icon="minus",
            tooltip="Remove step",
            disabled=True,
        )

        self.up_button = ipw.Button(
            layout=BUTTON_LAYOUT,
            icon="arrow-up",
            tooltip="Move step up",
        )

        self.down_button = ipw.Button(
            layout=BUTTON_LAYOUT,
            icon="arrow-down",
            tooltip="Move step down",
        )

        self.save_button = ipw.Button(
            layout=BUTTON_LAYOUT,
            button_style="success",
            icon="check",
            tooltip="Save protocol",
            disabled=True,
        )

        self.technique_name = ipw.Dropdown(
            layout=BOX_LAYOUT,
            style=BOX_STYLE,
            description="Technique:",
            options=self._get_technique_options(),
            value=type(self.default_technique),
        )

        self.save_technique_button = ipw.Button(
            layout=BUTTON_LAYOUT,
            button_style="success",
            icon="check",
            tooltip="Save technique",
        )

        self.reset_technique_button = ipw.Button(
            layout=BUTTON_LAYOUT,
            button_style="warning",
            icon="refresh",
            tooltip="Reset technique",
        )

        self._set_event_listeners()

        self.add_technique()

        self.technique_parameters = TechniqueParametersWidget(
            self.selected_technique)

        # initialize widgets
        super().__init__(
            layout={},
            children=[
                ipw.HBox(
                    layout={
                        "width": "auto",
                    },
                    children=[
                        ipw.VBox(
                            layout={
                                "flex": "1",
                                "margin": "0 5px 0 0",
                            },
                            children=[
                                self.name_label,
                                self.name,
                                self.sequence_label,
                                self.sequence,
                                ipw.HBox(
                                    layout={},
                                    children=[
                                        self.save_button,
                                        self.add_button,
                                        self.remove_button,
                                        self.up_button,
                                        self.down_button,
                                    ],
                                ),
                                self.warning_notice,
                            ],
                        ),
                        ipw.VBox(
                            layout={
                                "width": "420px",
                                "border": "solid darkgrey 1px",
                                "padding": "5px",
                            },
                            children=[
                                self.technique_name,
                                self.technique_parameters,
                                ipw.HBox(
                                    layout={"align_items": "center"},
                                    children=[
                                        self.save_technique_button,
                                        self.reset_technique_button,
                                        self.technique_action_info,
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
            ],
            selected_index=None,
        )

        self.set_title(0, "Create custom protocol")

        self._set_event_listeners()

    @property
    def default_technique(self) -> OpenCircuitVoltage:
        """docstring"""
        name = self.get_default_technique_name(OpenCircuitVoltage)
        return OpenCircuitVoltage(name=name)

    @property
    def selected_technique(self) -> CyclingTechnique:
        "The step that is currently selected."
        return self.protocol.method[self.sequence.index]

    @selected_technique.setter
    def selected_technique(self, technique: CyclingTechnique) -> None:
        """docstring"""
        self.protocol.method[self.sequence.index] = technique

    def load_protocol(self, protocol: ElectroChemSequence) -> None:
        """docstring"""
        self.edit = True
        self.name.value = protocol.name
        self.protocol = protocol
        old_index = self.sequence.index
        self._update_technique_list_options()
        self.selected_index = 0
        self.sequence.notify_change({
            "type": "change",
            "name": "index",
            "old": old_index,
            "new": 0,
        })

    def on_name_change(self, change: dict) -> None:
        """docstring"""
        self.protocol.name = change["new"]
        self.save_button.disabled = not self.protocol.name
        self.reset_info_messages()

    def get_default_technique_name(self, technique: CyclingTechnique) -> str:
        """docstring"""
        return technique.schema()["properties"]["short_name"]["default"]

    def add_technique(self, _=None):
        """docstring"""
        self.protocol.add_step(self.default_technique)
        self._update_technique_list_options(self.protocol.n_steps - 1)

    def remove_technique(self, _=None):
        """docstring"""
        if self.protocol.n_steps == 1:
            return
        index = self.sequence.index
        self.protocol.remove_step(index)
        self._update_technique_list_options(max(index - 1, 0))

    def move_technique_up(self, _=None):
        """docstring"""
        index = self.sequence.index
        self.protocol.move_step_backward(index)
        self._update_technique_list_options(max(index - 1, 0))

    def move_technique_down(self, _=None):
        """docstring"""
        index = self.sequence.index
        self.protocol.move_step_forward(index)
        limit = self.protocol.n_steps
        self._update_technique_list_options(min(index + 1, limit))

    def save_technique(self, _=None):
        """Save label/parameters of the selected step from the
        widget into technique object."""
        tech_class: type = self.technique_name.value
        self.selected_technique = tech_class()
        self.selected_technique.name = self.technique_parameters.tech_name

        for name, val in self.technique_parameters.selected_parameters.items():
            self.selected_technique.parameters[name].value = val

        self._update_technique_list_options(self.sequence.index)
        self.technique_action_info.value = "Technique saved!"

    def reset_technique(self, _=None):
        """Reset changes to selected step parameters."""
        self._build_selected_technique()

    def reset_info_messages(self) -> None:
        """docstring"""
        self.technique_action_info.value = ""
        self.warning_notice.clear_output()

    def reset(self) -> None:
        """docstring"""
        self.name.value = ""
        self.protocol.method = []
        self.add_technique()
        self.technique_name.value = type(self.default_technique)

    def save_protocol(self, _=None) -> None:
        """docstring"""

        self.reset_info_messages()

        if self.edit:
            self.protocols_model.update(self.protocol, save=False)
            self.edit = False
        else:
            if self.protocol.name in self.protocols_model:
                with self.warning_notice:
                    print(f"Protocol {self.protocol.name} already exists")
                return
            self.protocols_model.add(self.protocol, save=False)

        self.reset()

    def _update_technique_list_options(self, new_index=None):
        """docstring"""
        self.reset_info_messages()
        self.update_options()
        self.set_sequence_index(new_index)

    def update_options(self):
        """docstring"""
        self.sequence.unobserve(self._build_selected_technique, "index")
        self.sequence.options = [
            f"[{i}] - {technique.name}"
            for i, technique in enumerate(self.protocol.method, 1)
        ]
        self.sequence.observe(self._build_selected_technique, "index")

    def set_sequence_index(self, new) -> None:
        """docstring"""

        old = new if new is not None else self.sequence.index

        if (old is None) or (old < 0):
            self.sequence.index = 0
        elif old >= self.protocol.n_steps:
            self.sequence.index = self.protocol.n_steps - 1
        else:
            self.sequence.index = old

    def toggle_remove_button(self, change: dict) -> None:
        """docstring"""
        self.remove_button.disabled = len(change["new"]) == 1

    def _build_selected_technique(self, _=None):
        """Build the list of properties of the current step."""
        self.technique_name.unobserve(self._build_default_technique, "value")
        self.technique_name.value = type(self.selected_technique)
        self.technique_name.observe(self._build_default_technique, "value")
        self._build_parameters(self.selected_technique)

    def _build_default_technique(self, _=None):
        """Build widget of parameters for the given technique."""
        tech_class: type = self.technique_name.value
        technique = tech_class()
        technique_name = self.technique_name.value
        technique.name = self.get_default_technique_name(technique_name)
        self._build_parameters(technique)

    def _build_parameters(self, technique):
        """Build widget of parameters for the given technique."""
        self.reset_info_messages()
        self.technique_parameters.__init__(technique)

    def _get_technique_options(self) -> dict[str, CyclingTechnique]:
        """docstring"""

        options: dict[str, CyclingTechnique] = {}

        for technique in get_args(ElectroChemPayloads):
            properties = technique.schema()["properties"]
            short_name = properties["short_name"]["default"]
            long_name = properties["technique"]["default"]
            key = f"{short_name} ({long_name})"
            options[key] = technique

        return options

    def _set_event_listeners(self) -> None:
        """Set event listeners"""

        self.name.observe(self.on_name_change, "value")

        self.sequence.observe(self.toggle_remove_button, "options")
        self.sequence.observe(self._build_selected_technique, "index")

        self.add_button.on_click(self.add_technique)
        self.remove_button.on_click(self.remove_technique)
        self.up_button.on_click(self.move_technique_up)
        self.down_button.on_click(self.move_technique_down)

        self.technique_name.observe(self._build_default_technique, "value")

        self.save_technique_button.on_click(self.save_technique)
        self.reset_technique_button.on_click(self.reset_technique)

        self.save_button.on_click(self.save_protocol)
