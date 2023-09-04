import re
from copy import deepcopy
from typing import Dict, Optional

import ipywidgets as ipw
from aiida_aurora.schemas.battery import BatterySample
from aiida_aurora.schemas.dgbowl import Tomato_0p2
from aiida_aurora.schemas.utils import dict_to_formatted_json
from IPython.display import display

from aurora.common.models import AvailableSamplesModel, BatteryExperimentModel
from aurora.engine import submit_experiment

from .protocols import CyclingCustom, ProtocolSelector
from .samples import SampleFromId, SampleFromRecipe, SampleFromSpecs
from .tomato import TomatoSettings

CODE_NAME = "ketchup-0.2rc2"


class ExperimentBuilder(ipw.VBox):
    """Aurora's main widgets panel."""

    _SECTION_TITLE = "Submit Experiment"

    _ACCORDION_STEPS = [
        'Select samples',
        'Select protocols',
        'Configure tomato/monitoring',
        'Review input',
    ]

    _SAMPLE_INPUT_LABELS = [
        'Select from ID',
        'Select from Specs',
        'Make from Recipe',
    ]

    _SAMPLE_INPUT_METHODS = [
        'id',
        'specs',
        'recipe',
    ]

    _PROTOCOL_TAB_LABELS = [
        'Select',
        'Create',
    ]

    _SAMPLE_BOX_LAYOUT = {
        'border': 'solid darkgrey 1px',
        'align_content': 'center',
        'margin': '5px 0',
        'padding': '5px',
    }

    _SUBMISSION_INPUT_LAYOUT = {
        'margin': '5px',
        'padding': '5px',
    }

    _SUBMISSION_OUTPUT_LAYOUT = {
        'border': 'solid darkgrey 1px',
        'padding': '5px',
        'max_height': '500px',
        'overflow': 'scroll',
    }

    _BUTTON_LAYOUT = {'margin': '5px'}

    _BUTTON_STYLE = {'description_width': '30%'}

    w_submission_output = ipw.Output(layout=_SUBMISSION_OUTPUT_LAYOUT)

    def __init__(
        self,
        experiment_model: Optional[BatteryExperimentModel] = None,
    ) -> None:
        """Initialize main panel and set up automation.

        Parameters
        ----------
        `experiment_model` : `Optional[BatteryExperimentModel]`, optional
            The experiment model, by default None
        """

        if experiment_model is None:
            experiment_model = BatteryExperimentModel()

        self.experiment_model = experiment_model

        self.available_samples_model = AvailableSamplesModel()

        self.reset_all_inputs()

        self._build_widgets()

        self._subscribe_observables()

    def _build_sample_selection_section(self) -> None:
        """Build the sample selection section."""

        self.w_sample_from_id = SampleFromId(
            experiment_model=self.experiment_model,
            validate_callback_f=self.return_selected_samples,
        )

        self.w_sample_from_specs = SampleFromSpecs(
            experiment_model=self.experiment_model,
            validate_callback_f=self.return_selected_samples,
            recipe_callback_f=self.switch_to_recipe,
        )

        self.w_sample_from_recipe = SampleFromRecipe(
            experiment_model=self.experiment_model,
            validate_callback_f=self.return_selected_specs_recipe,
        )

        self.w_sample_selection_tab = ipw.Tab(
            children=[
                self.w_sample_from_id,
                # self.w_sample_from_specs,
                # self.w_sample_from_recipe,
            ],
            selected_index=0,
        )

        for i, title in enumerate(self._SAMPLE_INPUT_LABELS):
            self.w_sample_selection_tab.set_title(i, title)

    def _build_cycling_protocol_section(self) -> None:
        """Build the cycling protocol section."""

        self.protocol_selector = ProtocolSelector(
            experiment_model=self.experiment_model,
            validate_callback_f=self.confirm_protocols_selection,
        )

        self.protocol_creator = CyclingCustom(
            experiment_model=self.experiment_model,
            validate_callback_f=self.save_protocol_and_refresh_selector,
        )

        self.w_protocols_tab = ipw.Tab(
            children=[
                self.protocol_selector,
                self.protocol_creator,
            ],
            selected_index=0,
        )

        for i, title in enumerate(self._PROTOCOL_TAB_LABELS):
            self.w_protocols_tab.set_title(i, title)

    def _build_job_settings_section(self) -> None:
        """Build the job settings section."""
        self.w_settings_tab = TomatoSettings(
            experiment_model=self.experiment_model,
            validate_callback_f=self.return_selected_settings,
        )

    def _build_input_preview_section(self) -> None:
        """Build the job submission section."""

        self.input_preview = ipw.Output(layout={"margin": "0 0 10px"})

        self.protocols_preview = ipw.Tab(layout={
            "min_height": "350px",
            "max_height": "350px",
        })

        self.settings_preview = ipw.Output(
            layout={
                "flex": "1",
                "margin": "2px",
                "border": "solid darkgrey 1px",
                "overflow_y": "auto",
            })

        self.monitors_preview = ipw.Output(
            layout={
                "flex": "1",
                "margin": "2px",
                "border": "solid darkgrey 1px",
                "overflow_y": "auto",
            })

        self.valid_input_confirmation = ipw.HTML()

        self.input_preview_section = ipw.VBox(
            layout={},
            children=[
                self.input_preview,
                self.valid_input_confirmation,
            ],
        )

    def _build_accordion(self) -> None:
        """Combine the sections in the main accordion widget."""

        self.w_main_accordion = ipw.Accordion(
            layout={},
            children=[
                self.w_sample_selection_tab,
                self.w_protocols_tab,
                self.w_settings_tab,
                self.input_preview_section,
            ],
            selected_index=None,
        )

        for i, title in enumerate(self._ACCORDION_STEPS):
            self.w_main_accordion.set_title(i, title)

    def _build_submission_section(self) -> ipw.HBox:
        """Build submission controls widgets."""

        self.w_code = ipw.Dropdown(
            layout={},
            description="Select code:",
            options=[CODE_NAME],  # TODO: get codes
            value=CODE_NAME,
        )

        self.w_submit_button = ipw.Button(
            description="Submit",
            button_style="success",
            tooltip="Submit the experiment",
            icon="play",
            disabled=True,
            style=self._BUTTON_STYLE,
            layout=self._BUTTON_LAYOUT,
        )

        self.w_reset_button = ipw.Button(
            description="Reset",
            button_style="danger",
            tooltip="Start over",
            icon="times",
            style=self._BUTTON_STYLE,
            layout=self._BUTTON_LAYOUT,
        )

        self.submission_controls = ipw.HBox(
            layout={
                "align_items": "center",
            },
            children=[
                self.w_code,
                self.w_submit_button,
                self.w_reset_button,
            ],
        )

    def _build_widgets(self) -> None:
        """Build panel widgets."""

        self._build_sample_selection_section()

        self._build_cycling_protocol_section()

        self._build_job_settings_section()

        self._build_input_preview_section()

        self._build_accordion()

        self._build_submission_section()

        super().__init__(
            layout={},
            children=[
                self.w_main_accordion,
                self.submission_controls,
                self.w_submission_output,
            ],
        )

    def _subscribe_observables(self) -> None:
        """Set up observables."""

        # reset selected sample/specs/recipe when the user selects another sample input tab
        self.w_sample_selection_tab.observe(
            self.reset_sample_selection,
            names='selected_index',
        )

        self.protocols_preview.observe(
            names="selected_index",
            handler=self.display_settings_and_monitors,
        )

        # trigger presubmission checks when we are in the "Submit Job" accordion tab
        self.w_main_accordion.observe(
            self.presubmission_checks_preview,
            names='selected_index',
        )

        self.w_submit_button.on_click(self.submit_job)
        self.w_reset_button.on_click(self.reset)

    #######################################################################################
    # FAKE TRAITLES
    # these are the properties shared between widgets
    # TODO: replace them with Traitlets defined for each widget, that are connected through `dlink` in this class
    # (see Quantum Espresso app for an example)
    #######################################################################################
    @property
    def selected_battery_samples(self):
        "The Battery Samples selected. Used by a BatteryCyclerExperiment."
        return self._selected_battery_samples

    @property
    def selected_battery_specs(self):
        "The Battery Specs selected. Used by an hypothetical BuildBatteryCalcJob."
        return self._selected_battery_specs

    @property
    def selected_recipe(self):
        "The Battery Recipe selected. Used by an hypothetical BuildBatteryCalcJob."
        return self._selected_battery_recipe

    @property
    def selected_cycling_protocols(self):
        "The Cycling Specs selected. Used by a BatteryCyclerExperiment."
        return list(self.experiment_model.selected_protocols.values())
        # return self._selected_cycling_protocol

    @property
    def selected_tomato_settings(self) -> Dict[str, Tomato_0p2]:
        "The Tomato Settings selected. Used by a BatteryCyclerExperiment."
        return deepcopy(self._selected_tomato_settings)

    @property
    def selected_monitor_settings(self) -> Dict[str, dict]:
        "The Tomato Monitor Settings selected. Used by a job monitor."
        return deepcopy(self._selected_monitor_settings)

    @property
    def workchain_node_label(self):
        """The label assigned to the submitted workchain node. The
        label used in the workflow as a prefix for each submitted
        protocol calculation node."""
        return self._workchain_node_label

    #######################################################################################
    # SAMPLE SELECTION
    #######################################################################################
    def return_selected_samples(self, sample_widget_obj):
        "Store the selected sample in `self.selected_battery_sample` and call post action."
        self._selected_battery_samples = sample_widget_obj.selected_samples
        self.post_sample_selection()

    def return_selected_specs_recipe(self, sample_widget_obj):
        "Store the selected specs & recipe in `self.selected_battery_specs` & `self.selected_recipe` and call post action (TODO)."
        self._selected_battery_specs = sample_widget_obj.selected_specs
        self._selected_recipe = sample_widget_obj.selected_recipe_dict  # this is a dict, for the moment - we need a schema
        # TODO: call post action

    def switch_to_recipe(self, specs_widget_obj):
        "Switch Sample tab to sample-from-recipe, copying over the selected specs"
        self.w_sample_selection_tab.selected_index = 2
        self.w_sample_from_recipe.w_specs_manufacturer.value = specs_widget_obj.w_specs_manufacturer.value
        self.w_sample_from_recipe.w_specs_composition.value = specs_widget_obj.w_specs_composition.value
        self.w_sample_from_recipe.w_specs_form_factor.value = specs_widget_obj.w_specs_form_factor.value
        self.w_sample_from_recipe.w_specs_capacity.value = specs_widget_obj.w_specs_capacity.value

    def post_sample_selection(self):
        "Switch to method accordion tab"
        self.w_main_accordion.selected_index = 1

    @property
    def sample_selection_method(self):
        if self.w_sample_selection_tab.selected_index is not None:
            return self._SAMPLE_INPUT_METHODS[
                self.w_sample_selection_tab.selected_index]

    #######################################################################################
    # METHOD SELECTION
    #######################################################################################
    def save_protocol_and_refresh_selector(self, custom: CyclingCustom):
        custom.reset_info_messages()
        name: str = custom.protocol_name.value

        # invalid name check
        if not re.match(r"^[\w_]+$", name):
            with custom.protocol_name_warning:
                print("Only alphanumeric characters and underscores allowed")
            return

        # existing name check
        available_protocols = self.experiment_model.available_protocols
        if any(protocol.name == name for protocol in available_protocols):
            with custom.protocol_name_warning:
                print("Protocol name already exists.\nPlease choose another.")
            return

        new_protocol = self.experiment_model.selected_protocol
        new_protocol.set_name(name)
        self.experiment_model.save_protocol()
        custom.w_save_info.value = "Saved!"

        self.protocol_selector.update_protocol_options()

    def confirm_protocols_selection(self, _=None):
        "Switch to Tomato settings accordion tab."
        self.w_settings_tab.update_protocol_options()
        self.w_main_accordion.selected_index = 2

    #######################################################################################
    # TOMATO SETTINGS SELECTION
    #######################################################################################
    def return_selected_settings(self, settings_widget: TomatoSettings):
        self._selected_tomato_settings = deepcopy(settings_widget.settings)
        self._selected_monitor_settings = deepcopy(settings_widget.monitors)
        self._workchain_node_label = settings_widget.workchain_node_label
        settings_widget.reset_controls()
        self.post_settings_selection()

    def post_settings_selection(self):
        "Switch to jobs submission accordion tab."
        self.w_main_accordion.selected_index = 3

    #######################################################################################
    # SUBMIT JOB
    #######################################################################################

    def display_samples_preview(self) -> None:
        """docstring"""

        samples = ipw.Output(
            layout={
                "max_height": "300px",
                "overflow_y": "scroll",
                "align_items": "center",
            })

        display(
            ipw.VBox(
                layout={},
                children=[
                    ipw.HTML("<h3 style='margin: 0'>Samples</h3>"),
                    samples,
                ],
            ))

        with samples:
            self.experiment_model.display_query_results({
                'battery_id': [
                    sample.battery_id
                    for sample in self.selected_battery_samples
                ]
            })

    def display_protocols_preview(self) -> None:
        """docstring"""

        self.protocols_preview.children = []
        self.protocols_preview.selected_index = None

        self.settings_preview.clear_output()
        self.monitors_preview.clear_output()

        display(
            ipw.HBox(
                layout={
                    "margin": "0 0 10px",
                    "grid_gap": "5px",
                },
                children=[
                    ipw.VBox(
                        layout={
                            "width": "50%",
                        },
                        children=[
                            ipw.HTML("<h3>Protocols</h3>"),
                            self.protocols_preview,
                        ],
                    ),
                    ipw.VBox(
                        layout={
                            "width": "50%",
                            "grid_gap": "5px",
                        },
                        children=[
                            ipw.VBox(
                                layout={
                                    "flex": "1",
                                },
                                children=[
                                    ipw.HTML("<h3>Settings</h3>"),
                                    self.settings_preview,
                                ],
                            ),
                            ipw.VBox(
                                layout={
                                    "flex": "1",
                                },
                                children=[
                                    ipw.HTML("<h3>Monitors</h3>"),
                                    self.monitors_preview,
                                ],
                            ),
                        ],
                    )
                ],
            ))

        for protocol in self.selected_cycling_protocols:

            output = ipw.Output()

            self.protocols_preview.children += (output, )
            index = len(self.protocols_preview.children) - 1
            self.protocols_preview.set_title(index, protocol.name)

            with output:
                for step in protocol.method:
                    print(f"{step.name} ({step.technique})")
                    for label, param in step.parameters:
                        default = param.default_value
                        value = default if param.value is None else param.value
                        units = "" if value is None else param.units
                        print(f"{label} = {value} {units}")
                    print()

        self.protocols_preview.selected_index = 0

    def display_settings_and_monitors(self, change: dict) -> None:
        """docstring"""

        if (index := change["new"]) is None:
            return

        protocol = list(self.selected_cycling_protocols)[index]
        settings = self.selected_tomato_settings.get(protocol.name)
        monitors = self.selected_monitor_settings.get(protocol.name)

        if settings is None or monitors is None:
            return

        self.settings_preview.clear_output()
        with self.settings_preview:
            for key, value in settings.dict().items():
                if isinstance(value, dict):
                    for k, v in value.items():
                        print(f"{k}: {v}")
                else:
                    print(f"{key}: {value}")

        self.monitors_preview.clear_output()
        with self.monitors_preview:
            for monitor, monitor_settings in monitors.items():
                print(f"name: {monitor}")
                for key, value in monitor_settings.items():
                    print(f"{key} = {value}")
            print()

    def presubmission_checks_preview(self, _=None) -> None:
        """
        Verify that all the input is there and display preview.
        If so, enable submission button.
        """

        if self.w_main_accordion.selected_index != 3:
            return

        self.input_preview.clear_output()

        with self.input_preview:

            if not self.selected_battery_samples:
                notice = "No battery samples selected!"
                return self.signal_missing_input(notice)

            self.display_samples_preview()

            if not self.selected_cycling_protocols:
                notice = "No cycling protocols selected!"
                return self.signal_missing_input(notice)

            self.display_protocols_preview()

            if not self.selected_tomato_settings or \
               not self.selected_monitor_settings:
                notice = "No protocol settings selected!"
                return self.signal_missing_input(notice)

        self.valid_input_confirmation.value = "✅ All good!"
        self.w_submit_button.disabled = False

    def signal_missing_input(self, message: str) -> None:
        """docstring"""
        self.valid_input_confirmation.value = f"❌ {message}"

    @w_submission_output.capture()
    def submit_job(self, dummy=None):

        for index, battery_sample in self.experiment_model.selected_samples.iterrows(
        ):
            json_stuff = dict_to_formatted_json(battery_sample)
            json_stuff['capacity'].pop('actual', None)
            current_battery = BatterySample.parse_obj(json_stuff)

            self.process = submit_experiment(
                sample=current_battery,
                protocols=self.selected_cycling_protocols,
                settings=list(self.selected_tomato_settings.values()),
                monitors=list(self.selected_monitor_settings.values()),
                code_name=self.w_code.value,
                sample_node_label="",
                protocol_node_label="",
                workchain_node_label="")

        self.w_main_accordion.selected_index = None

    #######################################################################################
    # RESET
    #######################################################################################

    def reset_sample_selection(self, dummy=None):
        "Reset sample data."
        self._selected_battery_samples = []
        self._selected_battery_specs = None
        self._selected_recipe = None

    def reset_all_inputs(self, dummy=None):
        "Reset all the selected inputs."
        self.reset_sample_selection()
        self._selected_cycling_protocol = None
        self._selected_tomato_settings = {}
        self._selected_monitor_settings = {}
        self._workchain_node_label = None

    def reset(self, dummy=None):
        "Reset the interface."
        # TODO: properly reinitialize each widget
        self.reset_all_inputs()
        self.w_sample_from_id.reset()
        self.protocol_selector.reset()
        self.w_settings_tab.reset()
        self.w_submission_output.clear_output()
        self.w_main_accordion.selected_index = None
