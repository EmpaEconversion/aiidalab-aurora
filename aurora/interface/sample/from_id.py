# -*- coding: utf-8 -*-

import ipywidgets as ipw
from IPython.display import display
from ...query import update_available_samples, query_available_samples, write_pd_query_from_dict
from ...schemas.convert import pd_series_to_formatted_json

class SampleFromId(ipw.VBox):
    
    BOX_LAYOUT_1 = {'width': '50%'}
    BOX_STYLE = {'description_width': 'initial'}
    BUTTON_STYLE = {'description_width': '30%'}
    BUTTON_LAYOUT = {'margin': '5px'}

    def __init__(self, validate_callback_f):
        
        # initialize widgets
        self.w_id_list = ipw.Select(
            rows=10,
            description="Select Battery ID:",
            style=self.BOX_STYLE, layout=self.BOX_LAYOUT_1)
        self.w_update = ipw.Button(
            description="Update",
            button_style='', tooltip="Update available samples", icon='refresh',
            style=self.BUTTON_STYLE, layout=self.BUTTON_LAYOUT)
        self.w_sample_preview = ipw.Output()
        self.w_validate = ipw.Button(
            description="Validate",
            button_style='success', tooltip="Validate the selected sample", icon='check',
            disabled=True,
            style=self.BUTTON_STYLE, layout=self.BUTTON_LAYOUT)
        
        super().__init__()
        self.children = [
            self.w_id_list,
            self.w_update,
            self.w_sample_preview,
            self.w_validate,
        ]
        
        # initialize options
        if not callable(validate_callback_f):
            raise TypeError("validate_callback_f should be a callable function")
        # self.validate_callback_f = validate_callback_f
        self.w_id_list.value = None
        self.on_update_button_clicked()
        
        # setup automations
        self.w_update.on_click(self.on_update_button_clicked)
        self.w_id_list.observe(handler=self.on_battery_id_change, names='value')
        # self.w_validate.on_click(self.on_validate_button_clicked)
        self.w_validate.on_click(lambda arg: validate_callback_f(self))


    @property
    def selected_sample_id(self):
        return self.w_id_list.value
    
    @property
    def selected_sample_dict(self):
        return pd_series_to_formatted_json(
            query_available_samples(write_pd_query_from_dict({'battery_id': self.w_id_list.value})).iloc[0])

    @staticmethod
    def _build_sample_id_options():
        """Returns a (option_string, battery_id) list."""
        table = query_available_samples(project=['battery_id', 'name']).sort_values('battery_id')
        return [("", None)] + [(f"<{row['battery_id']:5}>   \"{row['name']}\"", row['battery_id']) for index, row in table.iterrows()]

    def display_sample_preview(self):
        self.w_sample_preview.clear_output()
        if self.w_id_list.value is not None:
            with self.w_sample_preview:
                display(query_available_samples(write_pd_query_from_dict({'battery_id': self.w_id_list.value})))

    def update_validate_button_state(self):
        self.w_validate.disabled = (self.w_id_list.value is None)

    def on_battery_id_change(self, _=None):
        self.display_sample_preview()
        self.update_validate_button_state()

    def on_update_button_clicked(self, _=None):
        update_available_samples()
        self.w_id_list.options = self._build_sample_id_options()
    
    # def on_validate_button_clicked(self, _=None):
    #     # call the callback function
    #     self.validate_callback_f(self)