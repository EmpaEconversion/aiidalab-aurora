# -*- coding: utf-8 -*-
"""
Sample obtained from a synthesis recipe.
NOTE: This is a mock interface. NOT IMPLEMENTED YET.
"""

import ipywidgets as ipw
# from IPython.display import display
from aurora.query import update_available_specs, query_available_specs, update_available_recipies, query_available_recipies
from aurora.schemas.battery import BatterySpecs
from aurora.schemas.utils import dict_to_formatted_json

class SampleFromRecipe(ipw.VBox):

    # BOX_LAYOUT_1 = {'width': '40%'}
    BOX_LAYOUT_2 = {'width': '100%'}
    BOX_STYLE = {'description_width': '25%'}
    BUTTON_STYLE = {'description_width': '30%'}
    BUTTON_LAYOUT = {'margin': '5px'}
    OUTPUT_LAYOUT = {'width': '100%', 'margin': '5px', 'padding': '5px', 'border': 'solid 2px'}  #'max_height': '500px'
    MAIN_LAYOUT = {'width': '100%', 'padding': '10px', 'border': 'solid blue 2px'}

    def __init__(self, experiment_model, validate_callback_f):

        self.experiment_model = experiment_model

        # initialize widgets
        self.w_specs_label = ipw.HTML(value="<h2>Battery Specifications <span style='color: #ffffff; background-color: #ff0000;'>**NOT IMPLEMENTED**</span></h2>")
        self.w_specs_manufacturer = ipw.Dropdown(
            description="Manufacturer:",
            placeholder="Enter manufacturer",
            layout=self.BOX_LAYOUT_2, style=self.BOX_STYLE)
        self.w_specs_composition = ipw.Dropdown(
            description="Composition:",
            placeholder="Enter composition",
            layout=self.BOX_LAYOUT_2, style=self.BOX_STYLE)
        self.w_specs_capacity = ipw.Dropdown(
            description="Nominal capacity:",
            placeholder="Enter nominal capacity",
            layout=self.BOX_LAYOUT_2, style=self.BOX_STYLE)
        self.w_specs_form_factor = ipw.Dropdown(
            description="Form factor:",
            placeholder="Enter form factor",
            layout=self.BOX_LAYOUT_2, style=self.BOX_STYLE)

        self.w_recipe_label = ipw.HTML(value="<h2>Recipe Specifications</h2>")
        self.w_recipe_select = ipw.Select(
            rows=10, value=None,
            description="Select Recipe:",
            style=self.BOX_STYLE, layout=self.BOX_LAYOUT_2)
        self.w_recipe_preview = ipw.Output(
            layout=self.OUTPUT_LAYOUT)
        self.w_sample_metadata_name = ipw.Text(
            description="Sample name:",
            placeholder="Enter a name for this sample",
            layout=self.BOX_LAYOUT_2, style=self.BOX_STYLE)
        self.w_sample_metadata_creation_process = ipw.Textarea(
            description="Description:",
            placeholder="Describe the creation process",
            layout=self.BOX_LAYOUT_2, style=self.BOX_STYLE)

        self.w_update = ipw.Button(
            description="Update",
            button_style='', tooltip="Update available specs and recipies", icon='refresh',
            style=self.BUTTON_STYLE, layout=self.BUTTON_LAYOUT)
        self.w_reset = ipw.Button(
            description="Clear",
            button_style='danger', tooltip="Clear fields", icon='times',
            style=self.BUTTON_STYLE, layout=self.BUTTON_LAYOUT)

        self.w_validate = ipw.Button(
            description="Validate",
            button_style='success', tooltip="Validate the selected sample", icon='check',
            disabled=True,
            style=self.BUTTON_STYLE, layout=self.BUTTON_LAYOUT)
        # self.w_cookit = ipw.Button(
        #     description="Launch Recipy",
        #     button_style='info', tooltip="Cook it!", icon='blender',
        #     disabled=False,
        #     style=self.BUTTON_STYLE)

        # initialize widgets
        super().__init__()
        self.children = [
            ipw.VBox([
                self.w_specs_label,
                ipw.GridBox([
                    self.w_specs_manufacturer,
                    self.w_specs_composition,
                    self.w_specs_capacity,
                    self.w_specs_form_factor,
                ], layout=ipw.Layout(grid_template_columns="repeat(2, 45%)")),
                self.w_recipe_label,
                ipw.GridBox([
                    self.w_recipe_select,
                    self.w_recipe_preview,
                    self.w_sample_metadata_name,
                    self.w_sample_metadata_creation_process,
                ], layout=ipw.Layout(grid_template_columns="repeat(2, 45%)")),
                ipw.HBox([self.w_update, self.w_reset], layout={'justify_content': 'center', 'margin': '5px'}),
            ], layout=self.MAIN_LAYOUT),
            self.w_validate,
            # self.w_cookit,
        ]

        # initialize options
        self.on_update_button_clicked()
        self.display_recipe_preview()

        # setup automations
        self.w_update.on_click(self.on_update_button_clicked)
        self.w_reset.on_click(self.on_reset_button_clicked)
        self.w_recipe_select.observe(self.on_recipe_value_change, names='value')
        self.w_sample_metadata_name.observe(self.update_validate_button_state, names='value')
        self.w_validate.on_click(lambda arg: self.on_validate_button_clicked(validate_callback_f))


    @property
    def selected_specs_dict(self):
        return dict_to_formatted_json({
            'manufacturer': self.w_specs_manufacturer.value,
            'composition.description': self.w_specs_composition.value,
            'capacity.nominal': self.w_specs_capacity.value,
            'capacity.units': 'mAh',
            'form_factor': self.w_specs_form_factor.value,
        })

    @property
    def selected_specs(self):
        "The selected battery specs returned as a `aurora.schemas.battery.BatterySpecs` object."
        return BatterySpecs.parse_obj(self.selected_specs_dict)
    
    @property
    def selected_recipe_dict(self):
        return dict_to_formatted_json({
            'recipe': self.w_recipe_select.value,
            'metadata.name': self.w_sample_metadata_name.value,
            'metadata.creation_process': self.w_sample_metadata_creation_process.value,
        })

    #@staticmethod
    def _build_recipies_options(self):
        """Returns a (name, description) list."""
        dic = self.experiment_model.query_available_recipies()
        return [("", None)] + [(name, descr) for name, descr in dic.items()]

    def display_recipe_preview(self):
        self.w_recipe_preview.clear_output()
        with self.w_recipe_preview:
            if self.w_recipe_select.value:
                print(', '.join(self.w_recipe_select.value))

    def update_validate_button_state(self, _=None):
        self.w_validate.disabled = (self.w_recipe_select.value is None) or (len(self.w_sample_metadata_name.value) == 0)

    def on_recipe_value_change(self, _=None):
        self.update_validate_button_state()
        self.display_recipe_preview()

    def on_update_button_clicked(self, _=None):
        self.experiment_model.update_available_specs()
        self.experiment_model.update_available_recipies()
        self.w_specs_manufacturer.options = self.experiment_model.query_available_specs('manufacturer')
        self.w_specs_composition.options = self.experiment_model.query_available_specs('composition.description')
        self.w_specs_capacity.options = self.experiment_model.query_available_specs('capacity.nominal')
        self.w_specs_form_factor.options = self.experiment_model.query_available_specs('form_factor')
        self.w_recipe_select.options = self._build_recipies_options()

    def on_reset_button_clicked(self, _=None):
        self.w_specs_manufacturer.value = None
        self.w_specs_composition.value = None
        self.w_specs_form_factor.value = None
        self.w_specs_capacity.value = None
        self.w_recipe_select.value = None
        self.w_sample_metadata_name.value = ''
        self.w_sample_metadata_creation_process.value = ''

    def on_validate_button_clicked(self, callback_function):
        # call the validation callback function
        return callback_function(self)