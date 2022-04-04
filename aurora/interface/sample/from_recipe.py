# -*- coding: utf-8 -*-

import ipywidgets as ipw
from IPython.display import display
from ...query import update_available_recipies, query_available_recipies
    # write_pd_query_from_dict)
# from ...schemas.convert import pd_series_to_formatted_json

class SampleFromRecipe(ipw.HBox):

    BOX_LAYOUT_1 = {'width': '40%'}
    BOX_STYLE = {'description_width': 'initial'}
    BUTTON_STYLE = {'description_width': '30%'}
    BUTTON_LAYOUT = {'margin': '5px'}

    w_recipe_select = ipw.Select(
        rows=10, value=None,
        description="Select Recipe:",
        style=BOX_STYLE, layout=BOX_LAYOUT_1)
    w_recipe_preview = ipw.Label(
        value='', fontfamily='italic',
        layout=BUTTON_LAYOUT)

    w_update = ipw.Button(
        description="Update",
        button_style='', tooltip="Update available recipies", icon='refresh',
        style=BUTTON_STYLE, layout=BUTTON_LAYOUT)

    def sample_recipe_select_eventhandler(self, _=None):
        self.w_recipe_preview.value = ', '.join(self.w_recipe_select.value)

    def on_update_button_clicked(self, _=None):
        update_available_recipies()
        self.w_recipe_select.options = query_available_recipies()

    def __init__(self):
        # initialize options
        self.on_update_button_clicked()
        self.sample_recipe_select_eventhandler()

        # setup automations
        self.w_recipe_select.observe(self.sample_recipe_select_eventhandler, names='value')

        # initialize widgets
        super().__init__()
        self.children = [
            self.w_recipe_select,
            self.w_recipe_preview,
        ]