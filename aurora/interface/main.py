# -*- coding: utf-8 -*-

import pandas as pd
import ipywidgets as ipw
from IPython.display import display
from .sample import SampleFromId, SampleFromSpecs, SampleFromRecipe
from .cycling import CyclingStandard, CyclingCustom
from ..schemas.data_schemas import BatterySample, BatterySpecs
from ..schemas.convert import _remove_empties_from_dict

class MainPanel(ipw.VBox):

    _SAMPLE_INPUT_LABELS = ['Select from ID', 'Select from Specs', 'Make from Recipe']
    _SAMPLE_INPUT_METHODS = ['id', 'specs', 'recipe']
    _TEST_METHOD_LABELS = ['Standardized', 'Customized']
    w_header = ipw.HTML(value="<h2>Aurora</h2>")
    _SAMPLE_BOX_LAYOUT = {'width': '90%', 'border': 'solid blue 2px', 'align_content': 'center', 'margin': '5px', 'padding': '5px'}

    # SAMPLE SELECTION
    def return_selected_sample(self, sample_widget_obj):
        self.selected_battery_sample = BatterySample.parse_obj(_remove_empties_from_dict(sample_widget_obj.selected_sample_dict))
        self.post_sample_selection()

    def return_selected_specs_recipe(self, sample_widget_obj):
        self.selected_battery_specs = BatterySpecs.parse_obj(_remove_empties_from_dict(sample_widget_obj.selected_specs_dict))
        self.selected_recipe = sample_widget_obj.selected_recipe_dict

    def switch_to_recipe(self, specs_widget_obj):
        "Switch Sample tab to sample-from-recipe, copying over the selected specs"
        self.w_sample_selection_tab.selected_index = 2
        self.w_sample_from_recipe.w_specs_manufacturer.value = specs_widget_obj.w_specs_manufacturer.value
        self.w_sample_from_recipe.w_specs_composition.value = specs_widget_obj.w_specs_composition.value
        self.w_sample_from_recipe.w_specs_form_factor.value = specs_widget_obj.w_specs_form_factor.value
        self.w_sample_from_recipe.w_specs_capacity.value = specs_widget_obj.w_specs_capacity.value

    def post_sample_selection(self):
        "Switch to cycling accordion tab"
        self.w_main_accordion.selected_index = 1
        self.display_tested_sample_preview()

    def reset_sample_selection(self, _=None):
        self.selected_battery_sample = None
        self.selected_battery_specs = None
        self.selected_recipe = None
        self.selected_cycling_protocol = None

    def display_tested_sample_preview(self):
        self.w_test_sample.clear_output()
        if self.selected_battery_sample is not None:
            with self.w_test_sample:
                # display(query_available_samples(write_pd_query_from_dict({'battery_id': self.w_select_sample_id.value})))
                display(pd.json_normalize(self.selected_battery_sample.dict()).iloc[0])

    @property
    def sample_selection_method(self):
        if self.w_sample_selection_tab.selected_index is not None:
            return self._SAMPLE_INPUT_METHODS[self.w_sample_selection_tab.selected_index]

    # CYCLING
    def return_selected_protocol(self, cycling_widget_obj):
        self.selected_cycling_protocol = cycling_widget_obj.protocol_steps_list
        self.post_protocol_selection()

    def post_protocol_selection(self):
        "Close accordion, submit job to AiiDA"
        if self.selected_battery_sample is None:
            raise ValueError("A Battery sample was not selected!")
        self.w_main_accordion.selected_index = None
        print(f"Battery Sample:\n  {self.selected_battery_sample}\nCycling Protocol:\n  {self.selected_cycling_protocol}\nSubmitting to AiiDA...")

    # MAIN
    def __init__(self):
        
        # initialize variables
        self.reset_sample_selection()

        # Sample selection
        self.w_sample_from_id = SampleFromId(validate_callback_f=self.return_selected_sample)
        self.w_sample_from_specs = SampleFromSpecs(validate_callback_f=self.return_selected_sample, recipe_callback_f=self.switch_to_recipe)
        self.w_sample_from_recipe = SampleFromRecipe(validate_callback_f=self.return_selected_specs_recipe)

        self.w_sample_selection_tab = ipw.Tab(
            children=[self.w_sample_from_id, self.w_sample_from_specs, self.w_sample_from_recipe],
            selected_index=None)
        for i, title in enumerate(self._SAMPLE_INPUT_LABELS):
            self.w_sample_selection_tab.set_title(i, title)

        # Cycling
        self.w_test_sample_label = ipw.HTML("Selected sample:")
        self.w_test_sample = ipw.Output(layout=self._SAMPLE_BOX_LAYOUT)
        self.w_test_standard = CyclingStandard(lambda x: x)
        self.w_test_custom = CyclingCustom(validate_callback_f=self.return_selected_protocol)
        self.w_test_method_tab = ipw.Tab(
            children=[self.w_test_standard, self.w_test_custom],
            selected_index=0)
        for i, title in enumerate(self._TEST_METHOD_LABELS):
            self.w_test_method_tab.set_title(i, title)
        self.w_test = ipw.VBox([
            self.w_test_sample_label,
            self.w_test_sample,
            self.w_test_method_tab])

        # MAIN ACCORDION
        self.w_main_accordion = ipw.Accordion(children=[self.w_sample_selection_tab, self.w_test])
        self.w_main_accordion.set_title(0, 'Sample selection')
        self.w_main_accordion.set_title(1, 'Cycling Protocol')

        super().__init__()
        self.children = [
            self.w_header,
            self.w_main_accordion,
        ]

        # setup automations
        # reset selected sample/specs/recipe when the user selects another input tab
        self.w_sample_selection_tab.observe(self.reset_sample_selection, names='selected_index')