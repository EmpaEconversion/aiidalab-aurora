"""
Sample selected from a list of samples and their IDs.
TODO: implement creation and labeling of sample nodes. Store them in a group, retrieve a node if it was already created.
"""
import json

import ipywidgets as ipw
from IPython.display import display

#from aurora.query import update_available_samples, query_available_samples, write_pd_query_from_dict
from aurora.schemas.battery import BatterySample
from aurora.schemas.utils import (dict_to_formatted_json,
                                  remove_empties_from_dict_decorator)


class SampleFromId(ipw.VBox):

    BOX_LAYOUT_1 = {'width': '40%'}
    BOX_STYLE_1 = {'description_width': '15%'}
    BOX_STYLE_2 = {'description_width': 'initial'}
    BUTTON_STYLE = {'description_width': '30%'}
    BUTTON_LAYOUT = {'margin': '5px'}
    MAIN_LAYOUT = {
        'width': '100%',
        'padding': '10px',
        'border': 'solid blue 2px'
    }

    def __init__(self, experiment_model, validate_callback_f):

        self.experiment_model = experiment_model

        # initialize widgets
        self.w_header_label = ipw.HTML(value="<h2>Battery Selection</h2>")

        self.w_visualize_info = ipw.Output(
            layout={'border': '1px solid black'})

        self.w_update = ipw.Button(description="Update",
                                   button_style='',
                                   tooltip="Update available samples",
                                   icon='refresh',
                                   style=self.BUTTON_STYLE,
                                   layout=self.BUTTON_LAYOUT)
        self.w_select = ipw.Button(description="Select",
                                   button_style='',
                                   tooltip="Select chosen sample",
                                   icon='fa-arrow-right',
                                   style=self.BUTTON_STYLE,
                                   layout=self.BUTTON_LAYOUT)
        self.w_unselect = ipw.Button(description="Unselect",
                                     button_style='',
                                     tooltip="Unselect chosen sample",
                                     icon='fa-arrow-left',
                                     style=self.BUTTON_STYLE,
                                     layout=self.BUTTON_LAYOUT)

        self.w_id_list = ipw.Select(rows=10,
                                    description="Battery ID:",
                                    style=self.BOX_STYLE_1,
                                    layout=self.BOX_LAYOUT_1)
        self.w_selected_list = ipw.Select(rows=10,
                                          description="Selected ID:",
                                          style=self.BOX_STYLE_1,
                                          layout=self.BOX_LAYOUT_1)

        self.w_sample_preview = ipw.Output()
        self.w_sample_node_label = ipw.Text(  # TODO: this is not used yet - create a default or retrieve it from a node
            description="AiiDA Sample node label:",
            placeholder="Enter a name for the BatterySampleData node",
            layout=self.BOX_LAYOUT_1,
            style=self.BOX_STYLE_2)
        self.w_validate = ipw.Button(description="Validate",
                                     button_style='success',
                                     tooltip="Validate the selected sample",
                                     icon='check',
                                     disabled=True,
                                     style=self.BUTTON_STYLE,
                                     layout=self.BUTTON_LAYOUT)

        super().__init__()
        self.children = [
            self.w_header_label,
            ipw.VBox([
                self.w_visualize_info,
                ipw.HBox([
                    self.w_id_list,
                    ipw.VBox([self.w_update, self.w_select, self.w_unselect]),
                    self.w_selected_list
                ]),
                self.w_sample_preview,
                self.w_sample_node_label,
            ],
                     layout=self.MAIN_LAYOUT),
            self.w_validate,
        ]

        # initialize options
        if not callable(validate_callback_f):
            raise TypeError(
                "validate_callback_f should be a callable function")
        # self.validate_callback_f = validate_callback_f
        self.w_id_list.value = None
        self.w_selected_list.value = None
        self.on_update_button_clicked()

        # setup automations
        self.w_update.on_click(self.on_update_button_clicked)
        self.w_select.on_click(self.on_select_button_clicked)
        self.w_unselect.on_click(self.on_unselect_button_clicked)

        self.w_id_list.observe(handler=self.on_battery_id_change,
                               names='value')
        self.w_validate.on_click(
            lambda arg: self.on_validate_button_clicked(validate_callback_f))

    @property
    def selected_sample_id(self):
        return self.w_id_list.value

    @property
    @remove_empties_from_dict_decorator
    def selected_sample_dict(self):
        return dict_to_formatted_json(
            self.experiment_model.query_available_samples(
                self.experiment_model.write_pd_query_from_dict(
                    {'battery_id': self.w_id_list.value})).iloc[0])

    @property
    def selected_sample(self):
        "The selected battery sample returned as a `aurora.schemas.battery.BatterySample` object."
        return BatterySample.parse_obj(self.selected_sample_dict)

    def display_sample_preview(self):
        self.w_sample_preview.clear_output()
        if self.w_id_list.value is not None:
            with self.w_sample_preview:
                display(
                    self.experiment_model.query_available_samples(
                        self.experiment_model.write_pd_query_from_dict(
                            {'battery_id': self.w_id_list.value})))

    def update_validate_button_state(self):
        self.w_validate.disabled = (self.w_id_list.value is None)

    def on_battery_id_change(self, _=None):
        self.display_sample_preview()
        self.update_validate_button_state()

    def on_update_button_clicked(self, _=None):
        self.experiment_model.update_available_samples()
        self.w_id_list.options = self._build_sample_id_options()

    def on_select_button_clicked(self, _=None):
        sample_id = self.w_id_list.value
        if sample_id is not None:
            self.experiment_model.add_selected_sample(sample_id)
        self.update_lists()

    def on_unselect_button_clicked(self, _=None):
        sample_id = self.w_selected_list.value
        if sample_id is not None:
            self.experiment_model.remove_selected_sample(sample_id)
        self.update_lists()

    def on_validate_button_clicked(self, callback_function):
        # call the validation callback function
        return callback_function(self)

    def update_lists(self):
        """Updates the lists."""
        self.w_id_list.options = self._build_sample_id_options()
        self.w_selected_list.options = self._uptate_selected_list()

    ############################################################
    # This should go to control
    ############################################################

    #@staticmethod
    def _build_sample_id_options(self):
        """Returns a (option_string, battery_id) list."""
        # table = query_available_samples(project=['battery_id', 'metadata.name']).sort_values('battery_id')
        table = self.experiment_model.query_available_samples().sort_values(
            'battery_id')

        def row_label(row):
            # return f"<{row['battery_id']:8}>   \"{row['metadata.name']}\""
            return f"{row['battery_id']:8}   [{row['manufacturer'].split()[0]}]  ({row['capacity.nominal']} {row['capacity.units']})  {row['metadata.name']} ({row['composition.description']})"

        return [("", None)] + [(row_label(row), row['battery_id'])
                               for index, row in table.iterrows()]

    def _uptate_selected_list(self):
        """Returns a (option_string, battery_id) list."""
        table = self.experiment_model.selected_samples

        def row_label(row):
            return f"{row['battery_id']:8}   [{row['manufacturer'].split()[0]}]  ({row['capacity.nominal']} {row['capacity.units']})  {row['metadata.name']} ({row['composition.description']})"

        return [("", None)] + [(row_label(row), row['battery_id'])
                               for index, row in table.iterrows()]
