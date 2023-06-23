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

    PREVIEW_LAYOUT = {
        "margin": "0 auto 10px auto",
        "height": "150px",
        "max_height": "150px",
        "overflow": "auto",
        "align_items": "center",
    }

    def __init__(
        self,
        experiment_model: BatteryExperimentModel,
        validate_callback_f: Callable,
    ) -> None:
        """docstring"""

        self.experiment_model = experiment_model

        filters_container = self._build_filter_container()

        selection_container = self._build_selection_container()

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
                filters_container,
                selection_container,
                self.w_validate,
            ],
        )

        if not callable(validate_callback_f):
            raise TypeError(
                "validate_callback_f should be a callable function")

        self.on_reset_filters_button_clicked()
        self.experiment_model.update_available_specs()
        self._update_options()

        self.w_update_filters.on_click(self.on_update_filters_button_clicked)
        self.w_reset_filters.on_click(self.on_reset_filters_button_clicked)
        self._set_specs_observers()

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
    def current_specs(self):
        """
        A dictionary representing the current specs set by the user, that can be used in a query
        to filter the available samples.
        """
        return {
            'manufacturer': self.w_specs_manufacturer.value,
            'composition.description': self.w_specs_composition.value,
            'capacity.nominal': self.w_specs_capacity.value,
            'form_factor': self.w_specs_form_factor.value,
            # 'metadata.creation_datetime': self.w_specs_metadata_creation_date.value
        }

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

    def update_spec_options(self):
        """Update the specs' options."""
        self._unset_specs_observers()
        self._update_options()
        self._set_specs_observers()

    def update_sample_options(self):
        """docstring"""
        self.experiment_model.update_available_samples()
        self.w_sample_list.options = self._build_sample_id_options()

    def on_update_filters_button_clicked(self, _=None):
        self.experiment_model.update_available_specs()
        self.experiment_model.update_available_samples()
        self.update_spec_options()
        # self.display_query_result()
        # notice: if the old value is not available anymore, an error might be raised!

    def on_reset_filters_button_clicked(self, _=None):
        self.w_specs_manufacturer.value = None
        self.w_specs_composition.value = None
        self.w_specs_form_factor.value = None
        self.w_specs_capacity.value = None
        # self.w_specs_metadata_creation_date.value = None
        # self.w_specs_metadata_creation_process.value = None

    def on_specs_value_change(self, _=None):
        self.update_spec_options()
        self.update_sample_options()

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
        """docstring"""
        self.update_sample_options()

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

    def _build_sample_specs_options(self, spec_field):
        """
        Returns a `(option_string, battery_id)` list.
        The specs currently set are used to filter the sample list.
        The current `spec_field` is removed from the query, as we want to count how many samples correspond to each
        available value of the `spec_field`.
        """
        spec_field_options_list = self.experiment_model.query_available_specs(
            spec_field)

        # setup sample query filter from current specs and remove current field from query
        sample_query_filter_dict = self.current_specs.copy()
        sample_query_filter_dict[spec_field] = None

        # perform query of samples
        qres = self.experiment_model.query_available_samples(
            self.experiment_model.write_pd_query_from_dict(
                sample_query_filter_dict),
            project=[spec_field, 'battery_id']).sort_values('battery_id')

        # count values
        value_counts = qres[spec_field].value_counts()
        options_pairs = [(f"(no filter)  [{value_counts.sum()}]", None)]
        options_pairs.extend([(f"{value}  [{value_counts.get(value, 0)}]",
                               value) for value in spec_field_options_list])
        return options_pairs

    def _update_options(self):
        # first save current values to preserve them
        w_specs_manufacturer_value = self.w_specs_manufacturer.value
        w_specs_composition_value = self.w_specs_composition.value
        w_specs_capacity_value = self.w_specs_capacity.value
        w_specs_form_factor_value = self.w_specs_form_factor.value
        self.w_specs_manufacturer.options = self._build_sample_specs_options(
            'manufacturer')
        self.w_specs_manufacturer.value = w_specs_manufacturer_value
        self.w_specs_composition.options = self._build_sample_specs_options(
            'composition.description')
        self.w_specs_composition.value = w_specs_composition_value
        self.w_specs_capacity.options = self._build_sample_specs_options(
            'capacity.nominal')
        self.w_specs_capacity.value = w_specs_capacity_value
        self.w_specs_form_factor.options = self._build_sample_specs_options(
            'form_factor')
        self.w_specs_form_factor.value = w_specs_form_factor_value
        # self.w_select_sample_id.options = self._build_sample_id_options()
        # self.w_select_sample_id.value = None

    # @staticmethod
    def _build_sample_id_options(self):
        """Returns a (option_string, battery_id) list."""
        dict_query = self.current_specs
        pd_query = self.experiment_model.write_pd_query_from_dict(dict_query)
        unsorted = self.experiment_model.query_available_samples(pd_query)
        table = unsorted.sort_values('battery_id')

        return [(row_label(r), r['battery_id']) for _, r in table.iterrows()]

    def _update_selected_list(self):
        """Returns a (option_string, battery_id) list."""
        table = self.experiment_model.selected_samples
        return [(row_label(r), r['battery_id']) for _, r in table.iterrows()]

    def _set_specs_observers(self):
        self.w_specs_manufacturer.observe(handler=self.on_specs_value_change,
                                          names='value')
        self.w_specs_composition.observe(handler=self.on_specs_value_change,
                                         names='value')
        self.w_specs_capacity.observe(handler=self.on_specs_value_change,
                                      names='value')
        self.w_specs_form_factor.observe(handler=self.on_specs_value_change,
                                         names='value')
        # self.w_specs_metadata_creation_date.observe(handler=self.update_options, names='value')

    def _unset_specs_observers(self):
        self.w_specs_manufacturer.unobserve(handler=self.on_specs_value_change,
                                            names='value')
        self.w_specs_composition.unobserve(handler=self.on_specs_value_change,
                                           names='value')
        self.w_specs_capacity.unobserve(handler=self.on_specs_value_change,
                                        names='value')
        self.w_specs_form_factor.unobserve(handler=self.on_specs_value_change,
                                           names='value')
        # self.w_specs_metadata_creation_date.unobserve(handler=self.update_options, names='value')

    #########
    # widgets
    #########

    def _build_filter_container(self) -> ipw.VBox:
        """docstring"""

        filters = self._build_filters()

        filter_controls = self._build_filter_controls()

        filters_container = ipw.Accordion(
            layout={},
            children=[
                ipw.VBox(
                    layout={},
                    children=[
                        filters,
                        filter_controls,
                    ],
                ),
            ],
            selected_index=None,
        )

        filters_container.set_title(0, 'Filter samples by specification')

        return filters_container

    def _build_filters(self) -> ipw.GridBox:
        """docstring"""

        self.w_specs_manufacturer = ipw.Select(
            description="Manufacturer:",
            placeholder="Enter manufacturer",
            layout=self.BOX_LAYOUT_2,
            style=self.BOX_STYLE_1,
        )

        self.w_specs_composition = ipw.Select(
            description="Composition:",
            placeholder="Enter composition",
            layout=self.BOX_LAYOUT_2,
            style=self.BOX_STYLE_1,
        )

        self.w_specs_capacity = ipw.Select(
            description="Nominal capacity:",
            placeholder="Enter nominal capacity",
            layout=self.BOX_LAYOUT_2,
            style=self.BOX_STYLE_1,
        )

        self.w_specs_form_factor = ipw.Select(
            description="Form factor:",
            placeholder="Enter form factor",
            layout=self.BOX_LAYOUT_2,
            style=self.BOX_STYLE_1,
        )

        # self.w_specs_metadata_creation_date = ipw.DatePicker(
        #     description="Creation time:",
        #     layout=self.BOX_LAYOUT_2,
        #     style=self.BOX_STYLE_1,
        # )

        # self.w_specs_metadata_creation_process = ipw.Text(
        #     description="Creation process",
        #     placeholder="Describe creation process",
        #     layout=self.BOX_LAYOUT_2,
        #     style=self.BOX_STYLE_1,
        # )

        return ipw.GridBox(
            layout={
                "grid_template_columns": "repeat(2, 45%)",
            },
            children=[
                self.w_specs_manufacturer,
                self.w_specs_composition,
                self.w_specs_capacity,
                self.w_specs_form_factor,
                # self.w_specs_metadata_creation_date,
                # self.w_specs_metadata_creation_process,
            ],
        )

    def _build_filter_controls(self) -> ipw.HBox:
        """docstring"""

        self.w_update_filters = ipw.Button(
            description="Update",
            button_style='',
            tooltip="Update available samples",
            icon="refresh",
            style=self.BUTTON_STYLE,
            layout=self.BUTTON_LAYOUT,
        )

        self.w_reset_filters = ipw.Button(
            description="Reset",
            button_style='danger',
            tooltip="Clear fields",
            icon="times",
            style=self.BUTTON_STYLE,
            layout=self.BUTTON_LAYOUT,
        )

        return ipw.HBox(
            layout={
                'justify_content': 'center',
                'margin': '5px'
            },
            children=[
                self.w_update_filters,
                self.w_reset_filters,
            ],
        )

    def _build_selection_container(self) -> ipw.VBox:
        """docstring"""

        selection_section = self._build_selection_section()

        deselection_section = self._build_selected_section()

        return ipw.VBox(
            layout=self.MAIN_LAYOUT,
            children=[
                selection_section,
                deselection_section,
            ],
        )

    def _build_selection_section(self) -> ipw.VBox:
        """docstring"""

        w_selection_label = ipw.HTML(
            value="Battery ID:",
            layout=self.SAMPLE_LABEL_LAYOUT,
        )

        selection_controls = self._build_selection_controls()

        self.w_sample_list = ipw.SelectMultiple(
            rows=10,
            style=self.SAMPLE_BOX_STYLE,
            layout=self.SAMPLE_BOX_LAYOUT,
        )

        self.w_selection_preview = ipw.Output(layout=self.PREVIEW_LAYOUT)

        return ipw.VBox(
            layout={},
            children=[
                ipw.HBox(
                    layout={},
                    children=[
                        ipw.VBox(
                            layout=self.SAMPLE_CONTROLS_LAYOUT,
                            children=[
                                w_selection_label,
                                selection_controls,
                            ],
                        ),
                        self.w_sample_list,
                    ],
                ),
                self.w_selection_preview,
            ],
        )

    def _build_selection_controls(self) -> ipw.VBox:
        """docstring"""

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

        return ipw.VBox(
            layout={},
            children=[
                self.w_update,
                self.w_select,
                self.w_select_all,
            ],
        )

    def _build_selected_section(self) -> ipw.VBox:
        """docstring"""

        w_selected_label = ipw.HTML(
            value="Selected ID:",
            layout=self.SAMPLE_LABEL_LAYOUT,
        )

        deselection_controls = self._build_deselection_controls()

        self.w_selected_list = ipw.SelectMultiple(
            rows=10,
            style=self.SAMPLE_BOX_STYLE,
            layout=self.SAMPLE_BOX_LAYOUT,
        )

        self.w_selected_preview = ipw.Output(layout=self.PREVIEW_LAYOUT)

        return ipw.VBox(
            layout={},
            children=[
                ipw.HBox(
                    layout={},
                    children=[
                        ipw.VBox(
                            layout=self.SAMPLE_CONTROLS_LAYOUT,
                            children=[
                                w_selected_label,
                                deselection_controls,
                            ],
                        ),
                        self.w_selected_list,
                    ],
                ),
                self.w_selected_preview,
            ],
        )

    def _build_deselection_controls(self) -> ipw.VBox:
        """docstring"""

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

        return ipw.VBox(
            layout={},
            children=[
                self.w_deselect_all,
                self.w_deselect,
            ],
        )


def row_label(row):
    return f"{row['battery_id']:8} [{row['manufacturer'].split()[0]}] ({row['capacity.nominal']} {row['capacity.units']}) {row['metadata.name']} {row['composition.description']})"


def get_ids(options):
    return [i for _, i in options]
