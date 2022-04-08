# -*- coding: utf-8 -*-

import ipywidgets as ipw
from IPython.display import display
# from ..query import (update_available_samples, update_available_specs, update_available_recipies,
#     query_available_samples, query_available_specs, query_available_recipies,
#     write_pd_query_from_dict)
from .sample import SampleFromId, SampleFromSpecs, SampleFromRecipe
from ..schemas.data_schemas import BatterySample, BatterySpecs

class MainPanel(ipw.VBox):
    
    _SAMPLE_INPUT_LABELS = ['Select from ID', 'Select from Specs', 'Make from Recipe']
    _SAMPLE_INPUT_METHODS = ['id', 'specs', 'recipe']
    w_header = ipw.HTML(value="<h1>Aurora</h1>")

    def return_selected_sample(self, sample_widget_obj):
        self.selected_battery_sample = BatterySample.parse_obj(sample_widget_obj.selected_sample_dict)
        self.post_sample_selection()
    
    def return_selected_specs_recipe(self, sample_widget_obj):
        self.selected_battery_specs = BatterySpecs.parse_obj(sample_widget_obj.selected_specs_dict)
        self.selected_recipe = sample_widget_obj.selected_recipe_dict
    
    def post_sample_selection(self):
        print('POST')
        self.w_main_accordion.selected_index = 1
    
    def reset_sample_selection(self, _=None):
        self.selected_battery_sample = None
        self.selected_battery_specs = None
        self.selected_recipe = None
    
    @property
    def sample_selection_method(self):
        if self.w_sample_selection_tab.selected_index is not None:
            return self._SAMPLE_INPUT_METHODS[self.w_sample_selection_tab.selected_index]
    
    def __init__(self):
        
        # initialize variables
        self.reset_sample_selection()

        # Sample selection
        self.w_sample_from_id = SampleFromId(self.return_selected_sample)
        self.w_sample_from_specs = SampleFromSpecs(self.return_selected_sample)
        self.w_sample_from_recipe = SampleFromRecipe(self.return_selected_specs_recipe)

        self.w_sample_selection_tab = ipw.Tab(
            children=[self.w_sample_from_id, self.w_sample_from_specs, self.w_sample_from_recipe],
            selected_index=None)
        for i, title in enumerate(self._SAMPLE_INPUT_LABELS):
            self.w_sample_selection_tab.set_title(i, title)

        # Cycling
        self.w_test = ipw.Label('This is the Test part')
        
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