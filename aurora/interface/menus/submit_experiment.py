import json

import ipywidgets as ipw
import pandas as pd
from IPython.display import display

from aurora import __version__
from aurora.engine import submit_experiment
from aurora.interface.cycling import CyclingCustom, CyclingStandard
from aurora.interface.menus.utils import get_header_box
from aurora.interface.sample import (SampleFromId, SampleFromRecipe,
                                     SampleFromSpecs)
from aurora.interface.tomato import TomatoSettings
from aurora.models import AvailableSamplesModel, BatteryExperimentModel
from aurora.schemas.battery import BatterySample
from aurora.schemas.utils import dict_to_formatted_json

CODE_NAME = "ketchup-0.2rc2"


class MainPanel(ipw.VBox):
    _SECTION_TITLE = "Submit Experiment"

    _ACCORDION_STEPS = [
        'Sample Selection',
        'Cycling Protocol',
        'Job Settings',
        'Submit Job',
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

    _METHOD_LABELS = [
        'Standardized',
        'Customized',
    ]

    _SAMPLE_BOX_LAYOUT = {
        'width': '90%',
        'border': 'solid blue 2px',
        'align_content': 'center',
        'margin': '5px',
        'padding': '5px',
    }

    _SUBMISSION_INPUT_LAYOUT = {
        'width': '90%',
        'border': 'solid blue 1px',
        'margin': '5px',
        'padding': '5px',
        'max_height': '500px',
        'overflow': 'scroll',
    }

    _SUBMISSION_OUTPUT_LAYOUT = {
        'width': '90%',
        'border': 'solid red 1px',
        'margin': '5px',
        'padding': '5px',
        'max_height': '500px',
        'overflow': 'scroll',
    }

    _BOX_LAYOUT = {'width': '100%'}

    _BOX_STYLE = {'description_width': '25%'}

    _BUTTON_LAYOUT = {'margin': '5px'}

    _BUTTON_STYLE = {'description_width': '30%'}

    w_header = ipw.HTML(value=f"<h2>Aurora</h2>\n Version {__version__}")

    w_submission_output = ipw.Output(layout=_SUBMISSION_OUTPUT_LAYOUT)

    def __init__(self, experiment_model=None):

        if experiment_model is None:
            experiment_model = BatteryExperimentModel()

        self.experiment_model = experiment_model

        self.available_samples_model = AvailableSamplesModel()

        self.reset_all_inputs()

        self.w_header_box = get_header_box(self._SECTION_TITLE)

        # Sample selection
        self.w_sample_from_id = SampleFromId(
            experiment_model=experiment_model,
            validate_callback_f=self.return_selected_sample)
        self.w_sample_from_specs = SampleFromSpecs(
            experiment_model=experiment_model,
            validate_callback_f=self.return_selected_sample,
            recipe_callback_f=self.switch_to_recipe)
        self.w_sample_from_recipe = SampleFromRecipe(
            experiment_model=experiment_model,
            validate_callback_f=self.return_selected_specs_recipe)

        self.w_sample_selection_tab = ipw.Tab(
            children=[
                self.w_sample_from_id,
                self.w_sample_from_specs,
                self.w_sample_from_recipe,
            ],
            selected_index=0,
        )
        for i, title in enumerate(self._SAMPLE_INPUT_LABELS):
            self.w_sample_selection_tab.set_title(i, title)

        # Method selection
        self.w_test_sample_label = ipw.HTML("Selected sample:")
        self.w_test_sample_preview = ipw.Output(layout=self._SAMPLE_BOX_LAYOUT)
        self.w_test_standard = CyclingStandard(lambda x: x)
        self.w_test_custom = CyclingCustom(
            experiment_model=experiment_model,
            validate_callback_f=self.return_selected_protocol)
        self.w_test_method_tab = ipw.Tab(
            children=[self.w_test_standard, self.w_test_custom],
            selected_index=1)
        for i, title in enumerate(self._METHOD_LABELS):
            self.w_test_method_tab.set_title(i, title)

        self.w_test_tab = ipw.VBox([
            self.w_test_sample_label,
            self.w_test_sample_preview,
            self.w_test_method_tab,
        ])

        # Settings selection
        self.w_settings_tab = TomatoSettings(
            validate_callback_f=self.return_selected_settings)

        # Submit
        self.w_job_preview = ipw.Output(
            layout=self._SUBMISSION_INPUT_LAYOUT
        )  # TODO: write better preview of the job inputs
        self.w_code = ipw.Dropdown(
            description="Select code:",
            options=[CODE_NAME],  # TODO: get codes
            value=CODE_NAME)
        self.w_submit_button = ipw.Button(description="SUBMIT",
                                          button_style="success",
                                          tooltip="Submit the experiment",
                                          icon="play",
                                          disabled=True,
                                          style=self._BUTTON_STYLE,
                                          layout=self._BUTTON_LAYOUT)

        self.w_submit_tab = ipw.VBox([
            self.w_job_preview,
            self.w_code,
            self.w_submit_button,
        ])

        # Reset
        self.w_reset_button = ipw.Button(description="RESET",
                                         button_style="danger",
                                         tooltip="Start over",
                                         icon="times",
                                         style=self._BUTTON_STYLE,
                                         layout=self._BUTTON_LAYOUT)

        ########################################################################
        # MAIN ACCORDION
        self.w_main_accordion = ipw.Accordion(children=[
            self.w_sample_selection_tab,
            self.w_test_tab,
            self.w_settings_tab,
            self.w_submit_tab,
        ])
        for i, title in enumerate(self._ACCORDION_STEPS):
            self.w_main_accordion.set_title(i, title)

        super().__init__()
        self.children = [
            self.w_header_box, self.w_main_accordion, self.w_reset_button,
            self.w_submission_output
        ]

        # setup automations
        # reset selected sample/specs/recipe when the user selects another sample input tab
        self.w_sample_selection_tab.observe(self.reset_sample_selection,
                                            names='selected_index')
        # trigger presubmission checks when we are in the "Submit Job" accordion tab
        self.w_main_accordion.observe(self.presubmission_checks_preview,
                                      names='selected_index')

        self.w_submit_button.on_click(self.submit_job)
        self.w_reset_button.on_click(self.reset)

    #######################################################################################
    # FAKE TRAITLES
    # these are the properties shared between widgets
    # TODO: replace them with Traitlets defined for each widget, that are connected through `dlink` in this class
    # (see Quantum Espresso app for an example)
    #######################################################################################
    @property
    def selected_battery_sample(self):
        "The Battery Sample selected. Used by a BatteryCyclerExperiment."
        return self._selected_battery_sample

    @property
    def selected_battery_specs(self):
        "The Battery Specs selected. Used by an hypothetical BuildBatteryCalcJob."
        return self._selected_battery_specs

    @property
    def selected_recipe(self):
        "The Battery Recipe selected. Used by an hypothetical BuildBatteryCalcJob."
        return self._selected_battery_recipe

    @property
    def selected_cycling_protocol(self):
        "The Cycling Specs selected. Used by a BatteryCyclerExperiment."
        return self.experiment_model.selected_protocol
        # return self._selected_cycling_protocol

    @property
    def selected_tomato_settings(self):
        "The Tomato Settings selected. Used by a BatteryCyclerExperiment."
        return self._selected_tomato_settings

    @property
    def selected_monitor_job_settings(self):
        "The Tomato Monitor Settings selected. Used by a TomatoMonitorCalcjob."
        return self._selected_monitor_job_settings

    @property
    def calcjob_node_label(self):
        "The label assigned the submitted BatteryCyclerExperiment CalcJob."
        return self._calcjob_node_label

    #######################################################################################
    # SAMPLE SELECTION
    #######################################################################################
    def return_selected_sample(self, sample_widget_obj):
        "Store the selected sample in `self.selected_battery_sample` and call post action."
        self._selected_battery_sample = sample_widget_obj.selected_sample
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

    def display_tested_sample_preview(self):
        "Display sample properties in the Method tab."
        self.w_test_sample_preview.clear_output()
        if self.selected_battery_sample is not None:
            with self.w_test_sample_preview:
                # display(query_available_samples(write_pd_query_from_dict({'battery_id': self.w_select_sample_id.value})))
                display(
                    pd.json_normalize(
                        self.selected_battery_sample.dict()).iloc[0])

    def post_sample_selection(self):
        "Switch to method accordion tab"
        self.w_main_accordion.selected_index = 1
        self.display_tested_sample_preview()

    @property
    def sample_selection_method(self):
        if self.w_sample_selection_tab.selected_index is not None:
            return self._SAMPLE_INPUT_METHODS[
                self.w_sample_selection_tab.selected_index]

    #######################################################################################
    # METHOD SELECTION
    #######################################################################################
    def return_selected_protocol(self, cycling_widget_obj):
        self.experiment_model.selected_protocol = cycling_widget_obj.protocol_steps_list
        self._selected_cycling_protocol = cycling_widget_obj.protocol_steps_list
        self.post_protocol_selection()

    def post_protocol_selection(self):
        "Switch to Tomato settings accordion tab."
        if self.selected_battery_sample is None:
            raise ValueError("A Battery sample was not selected!")
        # self.w_settings_tab.set_default_calcjob_node_label(self.selected_battery_sample_node.label, self.selected_cycling_protocol_node.label)  # TODO: uncomment this
        self.w_main_accordion.selected_index = 2

    #######################################################################################
    # TOMATO SETTINGS SELECTION
    #######################################################################################
    def return_selected_settings(self, settings_widget_obj):
        self._selected_tomato_settings = settings_widget_obj.selected_tomato_settings
        self._selected_monitor_job_settings = settings_widget_obj.selected_monitor_job_settings
        self._calcjob_node_label = settings_widget_obj.calcjob_node_label
        self.post_settings_selection()

    def post_settings_selection(self):
        "Switch to jobs submission accordion tab."
        self.w_main_accordion.selected_index = 3

    #######################################################################################
    # SUBMIT JOB
    #######################################################################################

    def presubmission_checks_preview(self, dummy=None):
        "Verify that all the input is there and display preview. If so, enable submission button."
        if self.w_main_accordion.selected_index == 3:
            self.w_job_preview.clear_output()
            with self.w_job_preview:
                try:
                    if self.selected_battery_sample is None:
                        raise ValueError("A Battery sample was not selected!")
                    if self.selected_cycling_protocol is None:
                        raise ValueError(
                            "A Cycling protocol was not selected!")
                    if self.selected_tomato_settings is None or self.selected_monitor_job_settings is None:
                        raise ValueError("Tomato settings were not selected!")

                    output_battery_sample = f'{self.selected_battery_sample}'
                    output_cycling_protocol = json.dumps(
                        self.selected_cycling_protocol.dict(), indent=2)
                    output_tomato_settings = f'{self.selected_tomato_settings}'
                    output_monitor_job_settings = f'{self.selected_monitor_job_settings}'

                    print(f"Battery Sample:\n{output_battery_sample}\n")
                    print(f"Cycling Protocol:\n{output_cycling_protocol}\n")
                    print(f"Tomato Settings:\n{output_tomato_settings}\n")
                    print(
                        f"Monitor Job Settings:{output_monitor_job_settings}\n"
                    )

                except ValueError as err:
                    self.w_submit_button.disabled = True
                    print(f"❌ {err}")
                else:
                    self.w_submit_button.disabled = False
                    print("✅ All good!")

    @w_submission_output.capture()
    def submit_job(self, dummy=None):
        self.w_submit_button.disabed = True
        for index, battery_sample in self.experiment_model.selected_samples.iterrows(
        ):
            json_stuff = dict_to_formatted_json(battery_sample)
            json_stuff['capacity'].pop('actual', None)
            current_battery = BatterySample.parse_obj(json_stuff)

            self.process = submit_experiment(
                sample=current_battery,
                method=self.selected_cycling_protocol,
                tomato_settings=self.selected_tomato_settings,
                monitor_job_settings=self.selected_monitor_job_settings,
                code_name=self.w_code.value,
                sample_node_label="",
                method_node_label="",
                calcjob_node_label="")

        self.w_main_accordion.selected_index = None

    #######################################################################################
    # RESET
    #######################################################################################

    def reset_sample_selection(self, dummy=None):
        "Reset sample data."
        self._selected_battery_sample = None
        self._selected_battery_specs = None
        self._selected_recipe = None

    def reset_all_inputs(self, dummy=None):
        "Reset all the selected inputs."
        self.experiment_model.reset_inputs()
        self._selected_battery_sample = None
        self._selected_battery_specs = None
        self._selected_recipe = None
        self._selected_cycling_protocol = None
        self._selected_tomato_settings = None
        self._selected_monitor_job_settings = None
        self._calcjob_node_label = None

    def reset(self, dummy=None):
        "Reset the interface."
        # TODO: properly reinitialize each widget
        self.reset_all_inputs()
        self.w_submission_output.clear_output()
        self.w_main_accordion.selected_index = 0
