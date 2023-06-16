"""
Sample selected from a list of samples and their IDs.
TODO: implement creation and labeling of sample nodes. Store them in a group, retrieve a node if it was already created.
"""
from typing import Callable

import ipywidgets as ipw
# from aurora.query import update_available_samples, query_available_samples, write_pd_query_from_dict
from aiida_aurora.schemas.battery import BatterySample
from aiida_aurora.schemas.utils import (dict_to_formatted_json,
                                        remove_empties_from_dict_decorator)

from aurora.models.battery_experiment import BatteryExperimentModel


class SampleFromId(ipw.VBox):

    BOX_LAYOUT_1 = {'width': '40%'}
    BOX_LAYOUT_2 = {'width': '100%'}
    BOX_STYLE_1 = {'description_width': '25%'}
    BOX_STYLE_2 = {'description_width': 'initial'}
    BUTTON_STYLE = {'description_width': '30%'}
    BUTTON_LAYOUT = {'margin': '5px'}

    SAMPLE_BOX_STYLE = {'description_width': '5%'}

    SAMPLE_BOX_LAYOUT = {
        'flex': '1',
    }

    SAMPLE_CONTROLS_LAYOUT = {
        'width': '80px',
    }

    SAMPLE_LABEL_LAYOUT = {'margin': '0 auto'}

    SAMPLE_BUTTON_LAYOUT = {
        'width': '35px',
        'margin': '5px auto',
    }

    VALIDATE_BUTTON_STYLE = {'description_width': '30%'}

    VALIDATE_BUTTON_STYLE = {'description_width': '30%'}

    VALIDATE_BUTTON_LAYOUT = {
        'margin': '5px',
    }

    MAIN_LAYOUT = {
        'width': '100%',
        'padding': '10px',
        'border': 'solid blue 2px'
    }

    def __init__(
        self,
        experiment_model: BatteryExperimentModel,
        validate_callback_f: Callable,
    ) -> None:

        self.experiment_model = experiment_model

        # initialize widgets
        self.w_header_label = ipw.HTML(value="<h2>Battery Selection</h2>")

        # selection

        self.w_selection_label = ipw.HTML(
            value="Battery ID:",
            layout=self.SAMPLE_LABEL_LAYOUT,
        )

        self.w_update = ipw.Button(
            description="",
            button_style='',
            tooltip="Update available samples",
            icon='refresh',
            layout=self.SAMPLE_BUTTON_LAYOUT,
        )

        self.w_select = ipw.Button(
            description="",
            button_style='',
            tooltip="Select chosen sample",
            icon='fa-angle-down',
            layout=self.SAMPLE_BUTTON_LAYOUT,
        )

        self.w_select_all = ipw.Button(
            description="",
            button_style='',
            tooltip="Select all samples",
            icon='fa-angle-double-down',
            layout=self.SAMPLE_BUTTON_LAYOUT,
        )

        self.w_selection_controls = ipw.VBox(
            layout={},
            children=[
                self.w_update,
                self.w_select,
                self.w_select_all,
            ],
        )

        self.w_sample_list = ipw.SelectMultiple(
            rows=10,
            style=self.SAMPLE_BOX_STYLE,
            layout=self.SAMPLE_BOX_LAYOUT,
        )

        # selected

        self.w_selected_label = ipw.HTML(
            value="Selected ID:",
            layout=self.SAMPLE_LABEL_LAYOUT,
        )

        self.w_deselect = ipw.Button(
            description="",
            button_style='',
            tooltip="Deselect chosen sample",
            icon='fa-angle-up',
            layout=self.SAMPLE_BUTTON_LAYOUT,
        )

        self.w_deselect_all = ipw.Button(
            description="",
            button_style='',
            tooltip="Deselect all samples",
            icon='fa-angle-double-up',
            layout=self.SAMPLE_BUTTON_LAYOUT,
        )

        self.w_deselection_controls = ipw.VBox(
            layout={},
            children=[
                self.w_deselect_all,
                self.w_deselect,
            ],
        )

        self.w_selected_list = ipw.SelectMultiple(
            rows=10,
            style=self.SAMPLE_BOX_STYLE,
            layout=self.SAMPLE_BOX_LAYOUT,
        )

        self.w_selection_preview = ipw.Output()
        self.w_selected_preview = ipw.Output()

        self.w_validate = ipw.Button(
            description="Validate",
            button_style='success',
            tooltip="Validate the selected sample",
            icon='check',
            disabled=True,
            style=self.VALIDATE_BUTTON_STYLE,
            layout=self.VALIDATE_BUTTON_LAYOUT,
        )

        super().__init__(
            layout={},
            children=[
                self.w_header_label,
                ipw.VBox(
                    [
                        ipw.HBox([
                            ipw.VBox(
                                [
                                    self.w_selection_label,
                                    self.w_selection_controls,
                                ],
                                layout=self.SAMPLE_CONTROLS_LAYOUT,
                            ),
                            self.w_sample_list,
                        ]),
                        ipw.HBox([
                            ipw.VBox(
                                [
                                    self.w_selected_label,
                                    self.w_deselection_controls,
                                ],
                                layout=self.SAMPLE_CONTROLS_LAYOUT,
                            ),
                            self.w_selected_list,
                        ]),
                        self.w_selected_preview,
                        self.w_selection_preview,
                    ],
                    layout=self.MAIN_LAYOUT,
                ),
                self.w_validate,
            ])

        # initialize options
        if not callable(validate_callback_f):
            raise TypeError(
                "validate_callback_f should be a callable function")

        self.validate_callback_f = validate_callback_f
        self.w_sample_list.value = []
        self.w_selected_list.value = []
        self.on_update_button_clicked()

        self.display_samples_preview()
        self.display_selected_samples_preview()

        # setup automations
        self.w_update.on_click(self.on_update_button_clicked)
        self.w_select.on_click(self.on_select_button_clicked)
        self.w_select_all.on_click(self.on_select_all_button_clicked)
        self.w_deselect.on_click(self.on_deselect_button_clicked)
        self.w_deselect_all.on_click(self.on_deselect_all_button_clicked)

        self.w_sample_list.observe(
            names='value',
            handler=self.on_sample_list_clicked,
        )

        self.w_selected_list.observe(
            handler=self.on_selected_list_change,
            names='options',
        )

        self.w_validate.on_click(
            lambda arg: self.on_validate_button_clicked(validate_callback_f))

    @property
    def selected_sample_ids(self):
        return self.w_sample_list.value

    @property
    @remove_empties_from_dict_decorator
    def selected_sample_dict(self):
        dict_query = {'battery_id': get_ids(self.w_selected_list.options)}
        pd_query = self.experiment_model.write_pd_query_from_dict(dict_query)
        results = self.experiment_model.query_available_samples(pd_query)

        selected = []
        for _, result in results.iterrows():
            json = dict_to_formatted_json(result)
            selected.append(json)

        return selected

    @property
    def selected_samples(self):
        "The selected battery sample returned as a `aiida_aurora.schemas.battery.BatterySample` object."
        return [
            BatterySample.parse_obj(sample)
            for sample in self.selected_sample_dict
        ]

    def display_samples_preview(self):
        self.w_selection_preview.clear_output()
        with self.w_selection_preview:
            query = {'battery_id': self.w_sample_list.value}
            self.experiment_model.display_query_results(query)

    def display_selected_samples_preview(self):
        self.w_selected_preview.clear_output()
        with self.w_selected_preview:
            query = {'battery_id': get_ids(self.w_selected_list.options)}
            self.experiment_model.display_query_results(query)

    def on_sample_list_clicked(self, _=None):
        self.display_samples_preview()

    def on_update_button_clicked(self, _=None):
        self.experiment_model.update_available_samples()
        self.w_sample_list.options = self._build_sample_id_options()

    def on_select_button_clicked(self, _=None):
        if sample_ids := self.w_sample_list.value:
            self.experiment_model.add_selected_samples(sample_ids)
        self.update_selected_list_options()

    def on_select_all_button_clicked(self, _=None):
        if sample_ids := get_ids(self.w_sample_list.options):
            self.experiment_model.add_selected_samples(sample_ids)
        self.update_selected_list_options()

    def on_selected_list_change(self, _=None):
        self.update_validate_button_state()
        self.display_selected_samples_preview()

    def on_deselect_button_clicked(self, _=None):
        if sample_ids := self.w_selected_list.value:
            self.experiment_model.remove_selected_samples(sample_ids)
        self.update_selected_list_options()

    def on_deselect_all_button_clicked(self, _=None):
        if sample_ids := get_ids(self.w_selected_list.options):
            self.experiment_model.remove_selected_samples(sample_ids)
        self.update_selected_list_options()

    def on_validate_button_clicked(self, callback_function):
        return callback_function(self)

    def update_validate_button_state(self):
        self.w_validate.disabled = not self.w_selected_list.options

    def update_selected_list_options(self):
        """Updates the lists."""
        self.w_selected_list.options = self._update_selected_list()

    ############################################################
    # This should go to control
    ############################################################

    # @staticmethod
    def _build_sample_id_options(self):
        """Returns a (option_string, battery_id) list."""
        table = self.experiment_model.query_available_samples().sort_values(
            'battery_id')

        return [(row_label(r), r['battery_id']) for _, r in table.iterrows()]

    def _update_selected_list(self):
        """Returns a (option_string, battery_id) list."""
        table = self.experiment_model.selected_samples
        return [(row_label(r), r['battery_id']) for _, r in table.iterrows()]


def row_label(row):
    return f"{row['battery_id']:8} [{row['manufacturer'].split()[0]}] ({row['capacity.nominal']} {row['capacity.units']}) {row['metadata.name']} {row['composition.description']})"


def get_ids(options):
    return [i for _, i in options]
