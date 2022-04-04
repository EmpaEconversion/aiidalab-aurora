# -*- coding: utf-8 -*-

import ipywidgets as ipw
from IPython.display import display
# from ..query import (update_available_samples, update_available_specs, update_available_recipies,
#     query_available_samples, query_available_specs, query_available_recipies,
#     write_pd_query_from_dict)
from .sample import SampleFromId, SampleFromSpecs, SampleFromRecipe
from ..schemas.data_schemas import BatterySample

class MainPanel(ipw.VBox):
    
    _SAMPLE_INPUT_TAB_LIST = ['from ID', 'from Specs', 'Make from Recipe']
    w_header = ipw.HTML(value="<h1>Aurora app</h1>")

    def return_selected_sample(self, sample_widget_obj):
        self.selected_battery_sample = BatterySample.parse_obj(sample_widget_obj.selected_sample_dict)
        self.post_sample_selection()
    
    def post_sample_selection(self):
        print('POST')
        self.w_main_accordion.selected_index = 1
    
    def __init__(self):
        
        self.selected_battery_sample = None
        self.w_sample_from_id = SampleFromId(self.return_selected_sample)
        self.w_sample_from_specs = SampleFromSpecs(self.return_selected_sample)
        self.w_sample_from_recipe = SampleFromRecipe()
        self.w_sample_input_tab = ipw.Tab(children=[self.w_sample_from_id, self.w_sample_from_specs, self.w_sample_from_recipe])
        for i, title in enumerate(self._SAMPLE_INPUT_TAB_LIST):
            self.w_sample_input_tab.set_title(i, title)

        self.w_test = ipw.Label('This is the Test part')
        
        self.w_main_accordion = ipw.Accordion(children=[self.w_sample_input_tab, self.w_test])
        self.w_main_accordion.set_title(0, 'Sample selection')
        self.w_main_accordion.set_title(1, 'Cycling Protocol')

        super().__init__()
        self.children = [
            self.w_header,
            self.w_main_accordion,
        ]

w_main = MainPanel()
w_main