from typing import Callable, List, Tuple

import ipywidgets as ipw
from aiida_aurora.schemas.cycling import (ElectroChemPayloads,
                                          ElectroChemSequence)

from aurora.common.models.battery_experiment import BatteryExperimentModel


class ProtocolSelector(ipw.VBox):
    """
    docstring
    """

    LABEL_LAYOUT = {
        'margin': '0 auto',
    }

    CONTROLS_LAYOUT = {
        'width': '80px',
    }

    BUTTON_LAYOUT = {
        'width': '35px',
        'margin': '5px auto',
    }

    BOX_STYLE = {
        'description_width': '5%',
    }

    BOX_LAYOUT = {
        'flex': '1',
    }

    def __init__(
        self,
        experiment_model: BatteryExperimentModel,
        validate_callback_f: Callable,
    ) -> None:
        """docstring"""

        if not callable(validate_callback_f):
            raise TypeError(
                "validate_callback_f should be a callable function")

        self.experiment_model = experiment_model

        selection_container = self._build_selection_container()

        self.w_validate = ipw.Button(
            style={
                'description_width': '30%',
            },
            layout={
                'margin': '5px',
            },
            description="Validate",
            button_style='success',
            tooltip="Validate the selected sample",
            icon='check',
            disabled=True,
        )

        self.reset_button = ipw.Button(
            layout={},
            style={},
            description="Reset",
            button_style='danger',
            tooltip="Clear selection",
            icon='times',
        )

        super().__init__(
            layout={},
            children=[
                selection_container,
                ipw.HBox(
                    layout={
                        "align_items": "center",
                    },
                    children=[
                        self.w_validate,
                        self.reset_button,
                    ],
                ),
            ],
        )

        self._initialize_selectors()

        self._set_event_listeners(validate_callback_f)

    @property
    def selected_protocols(self) -> List[ElectroChemSequence]:
        """docstring"""
        ids = get_ids(self.w_selected_list.options)
        return self.experiment_model.query_available_protocols(ids)

    #########
    # widgets
    #########

    def _build_selection_container(self) -> ipw.HBox:
        """docstring"""

        selection_section = self._build_selection_section()

        deselection_section = self._build_selected_section()

        self.selection_details = ipw.Tab(layout={
            "width": "50%",
            "max_height": "338px",
        })

        return ipw.HBox(
            layout={
                'width': 'auto',
                'margin': '2px',
                'padding': '10px',
                'border': 'solid darkgrey 1px'
            },
            children=[
                ipw.VBox(
                    layout={
                        "width": "50%",
                    },
                    children=[
                        selection_section,
                        deselection_section,
                    ],
                ),
                self.selection_details,
            ],
        )

    def _build_selection_section(self) -> ipw.VBox:
        """docstring"""

        w_selection_label = ipw.HTML(
            value="Protocol:",
            layout=self.LABEL_LAYOUT,
        )

        selection_controls = self._build_selection_controls()

        self.w_protocol_list = ipw.SelectMultiple(
            rows=10,
            style=self.BOX_STYLE,
            layout=self.BOX_LAYOUT,
        )

        return ipw.VBox(
            layout={},
            children=[
                ipw.HBox(
                    layout={},
                    children=[
                        ipw.VBox(
                            layout=self.CONTROLS_LAYOUT,
                            children=[
                                w_selection_label,
                                selection_controls,
                            ],
                        ),
                        self.w_protocol_list,
                    ],
                ),
            ],
        )

    def _build_selection_controls(self) -> ipw.VBox:
        """docstring"""

        self.w_update = ipw.Button(
            description="",
            button_style='',
            tooltip="Update available samples",
            icon='refresh',
            layout=self.BUTTON_LAYOUT,
        )

        self.w_select = ipw.Button(
            description="",
            button_style='',
            tooltip="Select chosen sample",
            icon='fa-angle-down',
            layout=self.BUTTON_LAYOUT,
        )

        self.w_select_all = ipw.Button(
            description="",
            button_style='',
            tooltip="Select all samples",
            icon='fa-angle-double-down',
            layout=self.BUTTON_LAYOUT,
        )

        return ipw.VBox(
            layout={},
            children=[
                self.w_update,
                self.w_select,
                self.w_select_all,
            ],
        )

    def _build_selected_section(self) -> ipw.VBox:
        """docstring"""

        w_selected_label = ipw.HTML(
            value="Selected ID:",
            layout=self.LABEL_LAYOUT,
        )

        deselection_controls = self._build_deselection_controls()

        self.w_selected_list = ipw.SelectMultiple(
            rows=10,
            style=self.BOX_STYLE,
            layout=self.BOX_LAYOUT,
        )

        return ipw.VBox(
            layout={},
            children=[
                ipw.HBox(
                    layout={},
                    children=[
                        ipw.VBox(
                            layout=self.CONTROLS_LAYOUT,
                            children=[
                                w_selected_label,
                                deselection_controls,
                            ],
                        ),
                        self.w_selected_list,
                    ],
                ),
            ],
        )

    def _build_deselection_controls(self) -> ipw.VBox:
        """docstring"""

        self.w_deselect = ipw.Button(
            description="",
            button_style='',
            tooltip="Deselect chosen sample",
            icon='fa-angle-up',
            layout=self.BUTTON_LAYOUT,
        )

        self.w_deselect_all = ipw.Button(
            description="",
            button_style='',
            tooltip="Deselect all samples",
            icon='fa-angle-double-up',
            layout=self.BUTTON_LAYOUT,
        )

        return ipw.VBox(
            layout={},
            children=[
                self.w_deselect_all,
                self.w_deselect,
            ],
        )

    ###########################
    # TODO migrate to presenter
    ###########################

    def update_protocol_options(self) -> None:
        """docstring"""
        self.on_deselect_all_button_click()
        self.experiment_model.update_available_protocols()
        self._build_protocol_options()

    def on_update_button_click(self, _=None) -> None:
        """docstring"""
        self.update_protocol_options()

    def on_select_list_click(self, change: dict) -> None:
        """docstring"""
        self.reset_selection_details()
        self.add_selection_detail_tabs(change["new"])

    def on_select_button_click(self, _=None) -> None:
        """docstring"""
        if indices := self.w_protocol_list.value:
            self.experiment_model.add_selected_protocols(indices)
        self.update_selected_list_options()

    def on_select_all_button_click(self, _=None) -> None:
        """docstring"""
        if indices := get_ids(self.w_protocol_list.options):
            self.experiment_model.add_selected_protocols(indices)
        self.update_selected_list_options()

    def on_selected_list_change(self, _=None) -> None:
        """docstring"""
        self.update_validate_button_state()

    def on_deselect_button_click(self, _=None) -> None:
        """docstring"""
        if indices := self.w_selected_list.value:
            self.experiment_model.remove_selected_protocols(indices)
        self.update_selected_list_options()

    def on_deselect_all_button_click(self, _=None) -> None:
        """docstring"""
        if indices := get_ids(self.w_selected_list.options):
            self.experiment_model.remove_selected_protocols(indices)
        self.update_selected_list_options()

    def on_validate_button_click(self, callback_function: Callable):
        """docstring"""
        return callback_function(self)

    def update_validate_button_state(self) -> None:
        """docstring"""
        self.w_validate.disabled = not self.w_selected_list.options

    def update_selected_list_options(self) -> None:
        """docstring"""
        selected_protocols = self.experiment_model.selected_protocols.items()
        options = [(p.name, i) for i, p in selected_protocols]
        self.w_selected_list.options = options

    def reset_selection_details(self) -> None:
        """docstring"""
        self.selection_details.children = []
        self.selection_details.selected_index = None

    def add_selection_detail_tabs(self, indices: List[int]) -> None:
        """docstring"""

        if not indices:
            return

        protocols = self.experiment_model.query_available_protocols(indices)

        for protocol in protocols:

            output = ipw.Output()

            self.selection_details.children += (output, )
            index = len(self.selection_details.children) - 1
            self.selection_details.set_title(index, protocol.name)

            self.display_protocol_details(output, protocol)

        self.selection_details.selected_index = 0

    def display_protocol_details(
        self,
        output: ipw.Output,
        protocol: ElectroChemPayloads,
    ) -> None:
        """docstring"""
        with output:
            for step in protocol.method:
                print(f"{step.name} ({step.technique})")
                for label, param in step.parameters:
                    default = param.default_value
                    value = default if param.value is None else param.value
                    units = "" if value is None else param.units
                    print(f"{label} = {value} {units}")
                print()

    def reset(self, _=None) -> None:
        """docstring"""
        self.w_protocol_list.value = []
        self.w_selected_list.options = []
        self.experiment_model.reset_selected_protocols()

    def _build_protocol_options(self) -> None:
        """docstring"""
        available_protocols = self.experiment_model.query_available_protocols()
        options = [(p.name, i) for i, p in enumerate(available_protocols)]
        self.w_protocol_list.options = options

    def _initialize_selectors(self) -> None:
        """docstring"""
        self.w_protocol_list.value = []
        self.w_selected_list.value = []
        self.on_update_button_click()

    def _set_event_listeners(self, validate_callback_f) -> None:
        """docstring"""

        self.w_update.on_click(self.on_update_button_click)
        self.w_select.on_click(self.on_select_button_click)
        self.w_select_all.on_click(self.on_select_all_button_click)
        self.w_deselect.on_click(self.on_deselect_button_click)
        self.w_deselect_all.on_click(self.on_deselect_all_button_click)

        self.w_protocol_list.observe(
            names="value",
            handler=self.on_select_list_click,
        )

        self.w_selected_list.observe(
            names='options',
            handler=self.on_selected_list_change,
        )

        self.w_validate.on_click(
            lambda arg: self.on_validate_button_click(validate_callback_f))

        self.reset_button.on_click(self.reset)


def get_ids(options: Tuple[Tuple[str, int], ...]) -> List[int]:
    """Extract indices from option tuples.

    Parameters
    ----------
    options : `Tuple[Tuple[str, int], ...]`
        A tuple of `ipywidgets.SelectMultiple` option tuples.

    Returns
    -------
    `List[int]`
        A list of option indices.
    """
    return [i for _, i in options]
