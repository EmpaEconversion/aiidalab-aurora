# -*- coding: utf-8 -*-
import os
import json

import ipywidgets as ipw
from IPython.display import display
from aurora.schemas.battery import BatterySample
from aurora.schemas.utils import dict_to_formatted_json, remove_empties_from_dict_decorator

class SampleFilterWidget(ipw.VBox):

    _DEBUG = False
    BOX_LAYOUT_1 = {'width': '100%', 'height': '100px'}
    BOX_STYLE_1 = {'description_width': '25%'}
    BUTTON_STYLE = {'description_width': '30%'}
    BUTTON_LAYOUT = {'margin': '5px'}
    OUTPUT_LAYOUT = {'height': '120px', 'width': '90%', 'overflow': 'scroll', 'border': 'solid 1px', 'margin': '2px', 'padding': '5px'}
    QUERY_PRINT_COLUMNS = ['manufacturer', 'composition.description', 'capacity.nominal', 'capacity.actual', 'capacity.units', 'form_factor', 'metadata.name',
                       'metadata.creation_datetime'] #, 'metadata.creation_process']

    def __init__(self, available_samples_model):
        """Constructs the `SampleFilter` widget from components"""

        self.available_samples_model = available_samples_model

        self.w_specs_manufacturer = ipw.Select(
            description="Manufacturer:",
            placeholder="Enter manufacturer",
            layout=self.BOX_LAYOUT_1, style=self.BOX_STYLE_1
        )
        self.w_specs_composition = ipw.Select(
            description="Composition:",
            placeholder="Enter composition",
            layout=self.BOX_LAYOUT_1, style=self.BOX_STYLE_1
        )
        self.w_specs_capacity = ipw.Select(
            description="Nominal capacity:",
            placeholder="Enter nominal capacity",
            layout=self.BOX_LAYOUT_1, style=self.BOX_STYLE_1
        )
        self.w_specs_form_factor = ipw.Select(
            description="Form factor:",
            placeholder="Enter form factor",
            layout=self.BOX_LAYOUT_1, style=self.BOX_STYLE_1
        )


        #----------------------------------------#
        # BUTTONS
        #----------------------------------------#

        self.w_button_reset_d = ipw.Button(
            description="Reset changes",
            button_style='primary', tooltip="Reset unsaved changes", icon="refresh",
            style=self.BUTTON_STYLE, layout=self.BUTTON_LAYOUT
        )
        self.w_button_reset_f = ipw.Button(
            description="Reset filters",
            button_style='primary', tooltip="Clear filtering fields", icon="times",
            style=self.BUTTON_STYLE, layout=self.BUTTON_LAYOUT
        )
        self.w_button_delete = ipw.Button(
            description="Delete sample",
            button_style='danger', tooltip="Delete sample", icon="fa-trash",
            style=self.BUTTON_STYLE, layout=self.BUTTON_LAYOUT, disabled=True,
        )

        self.w_button_save = ipw.Button(
            description="Save changes",
            button_style='success', tooltip="Save changes", icon="fa-trash",
            style=self.BUTTON_STYLE, layout=self.BUTTON_LAYOUT, disabled=True,
        )

        #----------------------------------------#
        # DATA DISPLAYS
        #----------------------------------------#
        #self.w_query_result0 = ipw.Output(layout=self.OUTPUT_LAYOUT)
        self.w_query_result = ipw.Select(
            rows=10,
            layout={'width': '90%', 'overflow': 'scroll'},
        )
        self.w_extra_info = ipw.Output(layout=self.OUTPUT_LAYOUT)

        super().__init__()
        self.children = [
            ipw.GridBox([
                self.w_specs_manufacturer,
                self.w_specs_composition,
                self.w_specs_capacity,
                self.w_specs_form_factor,
                ],
                layout=ipw.Layout(grid_template_columns="repeat(2, 45%)")
            ),
            ipw.HBox(
                [self.w_button_reset_f, self.w_button_reset_d, self.w_button_delete, self.w_button_save],
                layout={'justify_content': 'center', 'margin': '5px'}
            ),
            #self.w_query_result0,
            self.w_query_result,
            self.w_extra_info,
        ]

        # initialize options
        self.on_reset_button_clicked()
        self._update_options()
        self.display_query_result()

        # setup automations
        self.w_button_reset_d.on_click(self.on_click_button_reset_d)
        self.w_button_reset_f.on_click(self.on_reset_button_clicked)
        self.w_button_delete.on_click(self.on_delete_button_clicked)
        self.w_button_save.on_click(self.on_click_save_changes)
        self._set_specs_observers()
        self._filtered_samples_id = None

        self.w_query_result.observe(handler=self.update_extra_info, names='value')
        self.available_samples_model.suscribe_observer(self)

    def update_observer(self):
        self.display_query_result()

    @property
    def filtered_samples_id(self):
        return self._filtered_samples_id

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

    def _build_sample_specs_options(self, spec_field):
        """
        Returns a list of `(option_string, field_content)`.
        The specs currently set are used to filter the sample list.
        The current `spec_field` is removed from the query, as we want to count how many samples correspond to each available value of the `spec_field`.

        FIRST CALL

        spec_field -> "manufacturer" (<class 'str'>)
        
        spec_field_options_list -> ['BIG-MAP', 'Conrad energy', 'Maxell'] (<class 'list'>)
        
        sample_query_filter_dict -> <class 'dict'>
        {'manufacturer': None, 'composition.description': None, 'capacity.nominal': None, 'form_factor': None}

        query_inp -> <class 'NoneType'>
        None

        query_res -> <class 'pandas.core.frame.DataFrame'>
                manufacturer  battery_id
            0  Conrad energy          10
            1  Conrad energy          11
            2  Conrad energy          12
            3           Empa         108
            4           Empa         109
            5           Empa         111
            6           Empa         112
            7           Empa         115
            8           Empa         116

        value_counts -> <class 'pandas.core.series.Series'>
            Empa             6
            Conrad energy    3
            Name: manufacturer, dtype: int64


        options_pairs -> <class 'list'>
        [
            ('(no filter)  [9]', None), # first value
            ('BIG-MAP  [0]', 'BIG-MAP'),
            ('Conrad energy  [3]', 'Conrad energy'),
            ('Maxell  [0]', 'Maxell')
        ]

        """
        # setup sample query filter from current specs and remove current field from query
        sample_query_filter_dict = self.current_specs.copy()
        sample_query_filter_dict[spec_field] = None

        query_inp = self.available_samples_model.write_pd_query_from_dict(sample_query_filter_dict)
        query_res = self.available_samples_model.query_available_samples(query_inp, project=[spec_field, 'battery_id'])
        query_res = query_res.sort_values('battery_id')

        # count values
        value_counts = query_res[spec_field].value_counts()
        #for a,b in value_counts.items():
        #    raise ValueError(f'Let us start: {type(b)}\n\n{b}\n\n')

        options_pairs = [(f"(no filter)  [{value_counts.sum()}]", None)]
        #for value in spec_field_options_list:
        #    options_pairs.append((f"{value}  [{value_counts.get(value, 0)}]", value))

        sample_query_filter_dict = {'manufacturer': None, 'composition.description': None, 'capacity.nominal': None, 'form_factor': None}
        query_inp = self.available_samples_model.write_pd_query_from_dict(sample_query_filter_dict)
        query_res = self.available_samples_model.query_available_samples(query_inp, project=[spec_field, 'battery_id'])
        relevant_indexes = query_res[spec_field].unique()

        for index_label in relevant_indexes:
            count = value_counts.get(index_label, 0)
            options_pairs.append((f"{index_label}  [{count}]", index_label))

        return options_pairs

    def _build_sample_id_options(self):
        """Returns a (option_string, battery_id) list."""
        query = self.available_samples_model.write_pd_query_from_dict(self.current_specs)
        table = self.available_samples_model.query_available_samples(query).sort_values('battery_id')
        return [("", None)] + [(f"<{row['battery_id']:5}>   \"{row['metadata.name']}\"", row['battery_id']) for index, row in table.iterrows()]

    def _update_options(self):
        # first save current values to preserve them
        w_specs_manufacturer_value = self.w_specs_manufacturer.value
        w_specs_composition_value = self.w_specs_composition.value
        w_specs_capacity_value = self.w_specs_capacity.value
        w_specs_form_factor_value = self.w_specs_form_factor.value
        self.w_specs_manufacturer.options = self._build_sample_specs_options('manufacturer')
        self.w_specs_manufacturer.value = w_specs_manufacturer_value
        self.w_specs_composition.options = self._build_sample_specs_options('composition.description')
        self.w_specs_composition.value = w_specs_composition_value
        self.w_specs_capacity.options = self._build_sample_specs_options('capacity.nominal')
        self.w_specs_capacity.value = w_specs_capacity_value
        self.w_specs_form_factor.options = self._build_sample_specs_options('form_factor')
        self.w_specs_form_factor.value = w_specs_form_factor_value

    def update_options(self):
        """Update the specs' options."""
        if self._DEBUG:
            print(f'updating options!')
        self._unset_specs_observers()
        self._update_options()
        self._set_specs_observers()
        self._filtered_samples_id = 1

    def on_specs_value_change(self, _=None):
        self.update_options()
        self.display_query_result()

    def on_delete_button_clicked(self, _=None):
        deletion_idval = self.w_query_result.value
        self.available_samples_model.remove_sample_with_id(deletion_idval)
        self.w_query_result.value = None
        self.w_extra_info.clear_output()
        with self.w_extra_info:
            print(f'Battery id = {deletion_idval} deleted!')
        self.update_options()
        self.display_query_result()

    def on_click_button_reset_d(self, _=None):
        self.available_samples_model.load_samples_file()
        self.update_options()
        self.display_query_result()
        # notice: if the old value is not available anymore, an error might be raised!

    def on_reset_button_clicked(self, _=None):
        self.w_specs_manufacturer.value = None
        self.w_specs_composition.value = None
        self.w_specs_form_factor.value = None
        self.w_specs_capacity.value = None

    def callback_call(self, callback_function):
        "Call a callback function and this class instance to it."
        return callback_function(self)

    def _set_specs_observers(self):
        self.w_specs_manufacturer.observe(handler=self.on_specs_value_change, names='value')
        self.w_specs_composition.observe(handler=self.on_specs_value_change, names='value')
        self.w_specs_capacity.observe(handler=self.on_specs_value_change, names='value')
        self.w_specs_form_factor.observe(handler=self.on_specs_value_change, names='value')

    def _unset_specs_observers(self):
        self.w_specs_manufacturer.unobserve(handler=self.on_specs_value_change, names='value')
        self.w_specs_composition.unobserve(handler=self.on_specs_value_change, names='value')
        self.w_specs_capacity.unobserve(handler=self.on_specs_value_change, names='value')
        self.w_specs_form_factor.unobserve(handler=self.on_specs_value_change, names='value')

    def display_query_result(self):
        #self.w_query_result0.clear_output()
        #with self.w_query_result0:
        #    query_inp = self.available_samples_model.write_pd_query_from_dict(self.current_specs)
        #    query_res = self.available_samples_model.query_available_samples(query_inp)
        #    query_res = query_res.set_index('battery_id')[self.QUERY_PRINT_COLUMNS]
        #    display(query_res)
        
        query_inp = self.available_samples_model.write_pd_query_from_dict(self.current_specs)
        table = self.available_samples_model.query_available_samples(query_inp)
        table = table.sort_values('battery_id')
        def row_label(row):
            # return f"<{row['battery_id']:8}>   \"{row['metadata.name']}\""
            return f"{row['battery_id']:8}   [{row['manufacturer'].split()[0]}]  ({row['capacity.nominal']} {row['capacity.units']})  {row['metadata.name']} ({row['composition.description']})"
        self.w_query_result.options = [("", None)] + [(row_label(row), row['battery_id']) for index, row in table.iterrows()]

        # Check if saveable
        self.w_button_save.disabled = not self.available_samples_model.has_unsaved_changes()
        #raise ValueError(f'Let us start: {type(query_res)}\n\n{query_res}\n\n')
        #self.w_query_result.options = []

    def update_extra_info(self, widget=None):
        self.w_extra_info.clear_output()
        with self.w_extra_info:
            battery_id = self.w_query_result.value
            if battery_id is None:
                self.w_button_delete.disabled = True
                return
            query_inp = self.available_samples_model.write_pd_query_from_dict({'battery_id': battery_id})
            query_res = self.available_samples_model.query_available_samples(query_inp)
            display(query_res)
            self.w_button_delete.disabled = False

    def on_click_save_changes(self, widget=None):
        self.available_samples_model.save_samples_file()
        self.w_button_save.disabled = not self.available_samples_model.has_unsaved_changes()
