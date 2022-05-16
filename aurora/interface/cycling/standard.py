# -*- coding: utf-8 -*-

import ipywidgets as ipw
from ...query import update_available_protocols, query_available_protocols

class CyclingStandard(ipw.VBox):

    # BOX_LAYOUT_1 = {'width': '40%'}
    BOX_LAYOUT_2 = {'width': '40%'}
    BOX_STYLE = {'description_width': 'initial'}
    BUTTON_STYLE = {'description_width': '30%'}
    BUTTON_LAYOUT = {'margin': '5px'}
    OUTPUT_LAYOUT = {'width': '100%', 'margin': '5px', 'padding': '5px', 'border': 'solid 2px'}  #'max_height': '500px'
    MAIN_LAYOUT = {'width': '100%', 'padding': '10px', 'border': 'solid red 2px'}

    def __init__(self, validate_callback_f):

        # initialize widgets
        self.w_protocol_label = ipw.HTML(value="<h2>BIG-MAP WP8 Standardized Protocols</h2>")
        self.w_protocol_select = ipw.Select(
            rows=10, value=None,
            description="Select Protocol:",
            style=self.BOX_STYLE, layout=self.BOX_LAYOUT_2)
        self.w_protocol_preview = ipw.Output(
            layout=self.OUTPUT_LAYOUT)
        self.w_protocol_parameters = ipw.Label("[...additional parameters...]")

        self.w_validate = ipw.Button(
            description="Submit",
            button_style='success', tooltip="Submit the selected test", icon='play',
            disabled=False,
            style=self.BUTTON_STYLE, layout=self.BUTTON_LAYOUT)

        # initialize widgets
        super().__init__()
        self.children = [
            self.w_protocol_label,
            ipw.VBox([
                ipw.HBox([
                    self.w_protocol_select,
                    self.w_protocol_preview,
                    # self.w_sample_metadata_name,
                    # self.w_sample_metadata_creation_process,
                ]), #, layout=ipw.Layout(grid_template_columns='25% 75%')),
                # ipw.HBox([self.w_update, self.w_reset], layout={'justify_content': 'center', 'margin': '5px'}),
                self.w_protocol_parameters,
            ], layout=self.MAIN_LAYOUT),
            self.w_validate,
            # self.w_cookit,
        ]

        # initialize options
        self.on_update_button_clicked()
        self.display_protocol_preview()

        # setup automations
        # self.w_update.on_click(self.on_update_button_clicked)
        # self.w_reset.on_click(self.on_reset_button_clicked)
        self.w_protocol_select.observe(self.on_protocol_value_change, names='value')
        # self.w_sample_metadata_name.observe(self.update_validate_button_state, names='value')
        # self.w_validate.on_click(lambda arg: self.on_validate_button_clicked(validate_callback_f))


#     @property
#     def selected_specs_dict(self):
#         return dict_to_formatted_json({
#             'manufacturer': self.w_specs_manufacturer.value,
#             'composition.description': self.w_specs_composition.value,
#             'capacity.nominal': self.w_specs_capacity.value,
#             'capacity.units': 'mAh',
#             'form_factor': self.w_specs_form_factor.value,
#         })
    
#     @property
#     def selected_recipe_dict(self):
#         return dict_to_formatted_json({
#             'recipe': self.w_recipe_select.value,
#             'metadata.name': self.w_sample_metadata_name.value,
#             'metadata.creation_process': self.w_sample_metadata_creation_process.value,
#         })

    def _build_protocols_options(self):
        """Returns a (name, description) list."""
        # dic = query_available_recipies()
        # return [("", None)] + [(name, descr) for name, descr in dic.items()]
        return self._available_protocols.keys()

    def display_protocol_preview(self):
        self.w_protocol_preview.clear_output()
        with self.w_protocol_preview:
            if self.w_protocol_select.value:
                print(f"Protocol:  {self.w_protocol_select.value}")
                print(f"Procedure:", "\n  ".join(self._available_protocols[self.w_protocol_select.value]['Procedure']))
                print(f"Cutoff conditions: {self._available_protocols[self.w_protocol_select.value]['Cutoff conditions']}")

#     def update_validate_button_state(self, _=None):
#         self.w_validate.disabled = (self.w_recipe_select.value is None) or (len(self.w_sample_metadata_name.value) == 0)

    def on_protocol_value_change(self, _=None):
        # self.update_validate_button_state()
        self.display_protocol_preview()

    def on_update_button_clicked(self, _=None):
#         update_available_specs()
        update_available_protocols()
        self._available_protocols = query_available_protocols()
#         self.w_specs_manufacturer.options = query_available_specs('manufacturer')
#         self.w_specs_composition.options = query_available_specs('composition.description')
#         self.w_specs_capacity.options = query_available_specs('capacity.nominal')
#         self.w_specs_form_factor.options = query_available_specs('form_factor')
        self.w_protocol_select.options = self._build_protocols_options()

#     def on_reset_button_clicked(self, _=None):
#         self.w_specs_manufacturer.value = None
#         self.w_specs_composition.value = None
#         self.w_specs_form_factor.value = None
#         self.w_specs_capacity.value = None
#         self.w_recipe_select.value = None
#         self.w_sample_metadata_name.value = ''
#         self.w_sample_metadata_creation_process.value = ''

#     def on_validate_button_clicked(self, callback_function):
#         # call the validation callback function
#         return callback_function(self)