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

PARAMS_LAYOUT = {
    "flex": "1",
    "width": "auto",
    "padding": "5px",
    "margin": "10px",
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

    DEFAULT_PROTOCOL = OpenCircuitVoltage

    _TECHNIQUES_OPTIONS = {
        f'{Technique.schema()["properties"]["short_name"]["default"]}  ({Technique.schema()["properties"]["technique"]["default"]})':
        Technique
        for Technique in get_args(ElectroChemPayloads)
    }

    def __init__(self, protocols_model: ProtocolsModel):
        """`ProtocolsManager` constructor.

        Parameters
        ----------
        `protocols_model` : `ProtocolsModel`
            The manager's local protocols model.
        """

        self.protocols_model = protocols_model

        self.protocol = ElectroChemSequence(method=[])

        self.name_label = ipw.Label(value="Protocol name:")

        self.name = ipw.Text(
            layout={
                "width": "auto",
                "margin": "0 2px",
            },
            placeholder="Enter protocol name",
        )

        self.name_warning = ipw.Output()

        self.sequence_label = ipw.Label(value="Sequence:")

        self.technique_list = ipw.Select(
            layout={
                "width": "auto",
                "margin": "0 2px",
            },
            rows=10,
            value=None,
            description="",
        )

        self.technique_action_info = ipw.HTML()

        self.add_technique()
        self._update_technique_list_options()

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
            options=self._TECHNIQUES_OPTIONS,
            value=type(self.selected_technique),
        )

        self.technique_parameters = TechniqueParametersWidget(
            self.selected_technique,
            layout=PARAMS_LAYOUT,
        )

        self.save_technique_button = ipw.Button(
            layout=BUTTON_LAYOUT,
            button_style="success",
            icon="check",
            tooltip="Save technique",
        )

        self.discard_technique_button = ipw.Button(
            layout=BUTTON_LAYOUT,
            button_style="danger",
            icon="fa-trash",
            tooltip="Discard technique",
        )

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
                                self.name_warning,
                                self.sequence_label,
                                self.technique_list,
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
                                        self.discard_technique_button,
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
    def selected_technique(self) -> CyclingTechnique:
        "The step that is currently selected."
        return self.protocol.method[self.technique_list.index]

    @selected_technique.setter
    def selected_technique(self, technique: CyclingTechnique) -> None:
        """docstring"""
        self.protocol.method[self.technique_list.index] = technique

    def on_name_change(self, change: dict) -> None:
        """docstring"""
        self.protocol.name = change["new"]
        self.save_button.disabled = not self.protocol.name
        self.reset_info_messages()

    def update(self):
        """Receive updates from the model"""
        self._update_technique_list_options()
        self._build_technique_parameters()

    def get_default_technique_name(self, technique: CyclingTechnique) -> str:
        """docstring"""
        name = technique.schema()["properties"]["short_name"]["default"]
        index = self._count_technique_occurrences(technique) + 1
        return f"{name}_{index}"

    def add_technique(self, _=None):
        """docstring"""
        name = self.get_default_technique_name(self.DEFAULT_PROTOCOL)
        self.protocol.add_step(self.DEFAULT_PROTOCOL(name=name))
        self._update_technique_list_options(self.protocol.n_steps - 1)

    def remove_technique(self, _=None):
        """docstring"""
        self.protocol.remove_step(self.technique_list.index)
        self._update_technique_list_options()

    def move_technique_up(self, _=None):
        """docstring"""
        self.protocol.move_step_backward(self.technique_list.index)
        self._update_technique_list_options(
            new_index=self.technique_list.index - 1)

    def move_technique_down(self, _=None):
        """docstring"""
        self.protocol.move_step_forward(self.technique_list.index)
        self._update_technique_list_options(
            new_index=self.technique_list.index + 1)

    def save_technique(self, _=None):
        """Save label/parameters of the selected step from the
        widget into technique object."""
        self.selected_technique = self.technique_name.value()
        self.selected_technique.name = self.technique_parameters.tech_name

        for name, val in self.technique_parameters.selected_parameters.items():
            self.selected_technique.parameters[name].value = val

        self._update_technique_list_options()
        self.technique_action_info.value = "Saved step!"

    def discard_technique(self, _=None):
        """Discard parameters of the selected step and reload them
        from the technique object."""
        self._build_technique_parameters()
        self.technique_action_info.value = "Discarded step!"

    def reset_info_messages(self) -> None:
        """docstring"""
        self.technique_action_info.value = ""
        self.name_warning.clear_output()

    def add_protocol(self, _=None) -> None:
        """docstring"""
        self.reset_info_messages()
        if self.protocol.name in self.protocols_model:
            with self.name_warning:
                print(f"Protocol {self.protocol.name} already exists.")
            return
        self.protocols_model.add(self.protocol, save=False)

    def _count_technique_occurrences(self, technique):
        techniques = [type(step) for step in self.protocol.method]
        return techniques.count(technique)

    def _update_technique_list_options(self, new_index=None):
        """docstring"""

        self.reset_info_messages()

        self.technique_list.options = [
            f"[{i + 1}] - {technique.name}"
            for i, technique in enumerate(self.protocol.method)
        ]

        old_index = new_index if new_index is not None else self.technique_list.index

        if (old_index is None) or (old_index < 0):
            self.technique_list.index = 0
        elif old_index >= self.protocol.n_steps:
            self.technique_list.index = self.protocol.n_steps - 1
        else:
            self.technique_list.index = old_index

    def toggle_remove_button(self, change: dict) -> None:
        """docstring"""
        self.remove_button.disabled = len(change["new"]) == 1

    def _build_technique_parameters(self, _=None):
        """Build the list of properties of the current step."""
        self.technique_name.value = type(self.selected_technique)
        self._build_parameters()

    def _build_parameters(self, _=None):
        """Build widget of parameters for the given technique."""
        self.reset_info_messages()

        if isinstance(
                self.technique_name.value,
                type(self.selected_technique),
        ):
            self.technique_parameters.__init__(
                self.selected_technique,
                layout=PARAMS_LAYOUT,
            )
        else:
            technique = self.technique_name.value()
            technique_name = self.technique_name.value
            technique.name = self.get_default_technique_name(technique_name)
            self.technique_parameters.__init__(
                technique,
                layout=PARAMS_LAYOUT,
            )

    def _set_event_listeners(self) -> None:
        """Set event listeners"""

        self.name.observe(self.on_name_change, "value")
        self.technique_list.observe(self.toggle_remove_button, "options")
        self.technique_list.observe(self._build_technique_parameters, "index")

        self.add_button.on_click(self.add_technique)
        self.remove_button.on_click(self.remove_technique)
        self.up_button.on_click(self.move_technique_up)
        self.down_button.on_click(self.move_technique_down)

        self.technique_name.observe(self._build_parameters, "value")

        self.save_technique_button.on_click(self.save_technique)
        self.discard_technique_button.on_click(self.discard_technique)

        self.save_button.on_click(self.add_protocol)
