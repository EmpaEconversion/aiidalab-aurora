# -*- coding: utf-8 -*-

import ipywidgets as ipw
from IPython.display import display
from ...query import update_available_samples, query_available_samples, update_available_specs, query_available_specs, write_pd_query_from_dict
from ...schemas.utils import dict_to_formatted_json

class SampleFromSpecs(ipw.VBox):

    _DEBUG = False
    QUERIABLE_SPECS = {
        "manufacturer": "Manufacturer",
        "composition.description": "Composition",
        "capacity.nominal": "Nominal capacity",
        "form_factor": "Form factor",
        # "metadata.creation_datetime": "Creation date",
    }
    BOX_LAYOUT_1 = {'width': '40%'}
    BOX_LAYOUT_2 = {'width': '100%', 'height': '100px'}
    BOX_STYLE = {'description_width': '25%'}
    BUTTON_STYLE = {'description_width': '30%'}
    BUTTON_LAYOUT = {'margin': '5px'}
    OUTPUT_LAYOUT = {'max_height': '500px', 'width': '90%', 'overflow': 'scroll', 'border': 'solid 2px', 'margin': '5px', 'padding': '5px'}
    SAMPLE_BOX_LAYOUT = {'width': '90%', 'border': 'solid blue 2px', 'align_content': 'center', 'margin': '5px', 'padding': '5px'}
    QUERY_PRINT_COLUMNS = ['manufacturer', 'composition.description', 'capacity.nominal', 'capacity.actual', 'capacity.units', 'form_factor', 'metadata.name',
                       'metadata.creation_datetime'] #, 'metadata.creation_process']
    
    def __init__(self, validate_callback_f, recipe_callback_f):

        if not callable(validate_callback_f):
            raise TypeError("validate_callback_f should be a callable function")
        if not callable(recipe_callback_f):
            raise TypeError("recipe_callback_f should be a callable function")

        # initialize widgets
        self.w_specs_header = ipw.HTML(value="<h2>Battery Specifications</h2>")
        self.w_specs_manufacturer = ipw.Select(
            description="Manufacturer:",
            placeholder="Enter manufacturer",
            layout=self.BOX_LAYOUT_2, style=self.BOX_STYLE)
        self.w_specs_composition = ipw.Select(
            description="Composition:",
            placeholder="Enter composition",
            layout=self.BOX_LAYOUT_2, style=self.BOX_STYLE)
        self.w_specs_capacity = ipw.Select(
            description="Nominal capacity:",
            placeholder="Enter nominal capacity",
            layout=self.BOX_LAYOUT_2, style=self.BOX_STYLE)
        self.w_specs_form_factor = ipw.Select(
            description="Form factor:",
            placeholder="Enter form factor",
            layout=self.BOX_LAYOUT_2, style=self.BOX_STYLE)
        # self.w_specs_metadata_creation_date = ipydatetime.DatetimePicker(
        #     description="Creation time:",
        #     style=BOX_STYLE)
        # self.w_specs_metadata_creation_process = ipw.Text(
        #     description="Creation process",
        #     placeholder="Describe creation process",
        #     style=BOX_STYLE)

        self.w_update = ipw.Button(
            description="Update",
            button_style='', tooltip="Update available samples", icon='refresh',
            style=self.BUTTON_STYLE, layout=self.BUTTON_LAYOUT)
        self.w_reset = ipw.Button(
            description="Reset",
            button_style='danger', tooltip="Clear fields", icon='times',
            style=self.BUTTON_STYLE, layout=self.BUTTON_LAYOUT)
        self.w_query_result = ipw.Output(layout=self.OUTPUT_LAYOUT)

        self.w_select_sample_id = ipw.Dropdown(
            description="Select Battery ID:", value=None,
            layout=self.BOX_LAYOUT_1, style={'description_width': 'initial'})
        self.w_cookit = ipw.Button(
            description="Load/Synthesize new", #['primary', 'success', 'info', 'warning', 'danger', '']
            button_style='primary', tooltip="Synthesize sample with these specs", icon='',
            style=self.BUTTON_STYLE, layout=self.BUTTON_LAYOUT)
        self.w_sample_preview = ipw.Output()
        self.w_validate = ipw.Button(
            description="Validate",
            button_style='success', tooltip="Validate the selected sample", icon='check',
            disabled=True,
            style=self.BUTTON_STYLE, layout=self.BUTTON_LAYOUT)

        super().__init__()
        self.children = [
            self.w_specs_header,
            ipw.GridBox([
                self.w_specs_manufacturer,
                self.w_specs_composition,
                self.w_specs_capacity,
                self.w_specs_form_factor,
                # self.w_specs_metadata_creation_date,
                # self.w_specs_metadata_creation_process,
            ], layout=ipw.Layout(grid_template_columns="repeat(2, 45%)")),
            ipw.HBox([self.w_update, self.w_reset], layout={'justify_content': 'center', 'margin': '5px'}),
            self.w_query_result,
            ipw.VBox([
                ipw.HBox([self.w_select_sample_id, ipw.Label(' or '), self.w_cookit], layout={'justify_content': 'space-around'}),
                self.w_sample_preview,
            ], layout=self.SAMPLE_BOX_LAYOUT),
            self.w_validate
        ]

        # initialize options
        self.on_reset_button_clicked()
        update_available_specs()
        self._update_options()
        self.display_query_result()

        # setup automations
        self.w_update.on_click(self.on_update_button_clicked)
        self.w_reset.on_click(self.on_reset_button_clicked)
        self._set_specs_observers()
        self.w_select_sample_id.observe(handler=self.on_battery_id_change, names='value')
        self.w_validate.on_click(lambda arg: self.callback_call(validate_callback_f))
        self.w_cookit.on_click(lambda arg: self.callback_call(recipe_callback_f))


    @property
    def selected_sample_id(self):
        return self.w_select_sample_id.value

    @property
    def selected_sample_dict(self):
        return dict_to_formatted_json(
            query_available_samples(write_pd_query_from_dict({'battery_id': self.w_select_sample_id.value})).iloc[0])

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
        Returns a `(option_string, battery_id)` list.
        The specs currently set are used to filter the sample list.
        The current `spec_field` is removed from the query, as we want to count how many samples correspond to each
        available value of the `spec_field`.
        """
        spec_field_options_list = query_available_specs(spec_field)

        # setup sample query filter from current specs and remove current field from query
        sample_query_filter_dict = self.current_specs.copy()
        sample_query_filter_dict[spec_field] = None

        # perform query of samples
        if self._DEBUG:
            print("\nSPEC FIELD: ", spec_field)
            print(f"       {spec_field_options_list}")
            print(" QUERY: ", sample_query_filter_dict)

        qres = query_available_samples(write_pd_query_from_dict(sample_query_filter_dict),
                                       project=[spec_field, 'battery_id']).sort_values('battery_id')

        # count values
        value_counts = qres[spec_field].value_counts()
        if self._DEBUG:
            print(' counts:', value_counts.to_dict())
        options_pairs = [(f"(no filter)  [{value_counts.sum()}]", None)]
        options_pairs.extend([(f"{value}  [{value_counts.get(value, 0)}]", value) for value in spec_field_options_list])
        return options_pairs

    def _build_sample_id_options(self):
        """Returns a (option_string, battery_id) list."""
        table = query_available_samples(write_pd_query_from_dict(self.current_specs)).sort_values('battery_id')
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
        self.w_select_sample_id.options = self._build_sample_id_options()
        self.w_select_sample_id.value = None

    def update_options(self):
        """Update the specs' options."""
        if self._DEBUG:
            print(f'updating options!')
        self._unset_specs_observers()
        self._update_options()
        self._set_specs_observers()

    def display_query_result(self):
        self.w_query_result.clear_output()
        with self.w_query_result:
            # print(f'Query:\n  {self.current_specs}')
            query_res = query_available_samples(write_pd_query_from_dict(self.current_specs)).set_index('battery_id')[self.QUERY_PRINT_COLUMNS]
            # query_res['metadata.creation_datetime'] = query_res['metadata.creation_datetime'].dt.strftime("%d-%m-%Y %H:%m")
            # display(query_res.style.format(formatter={'metadata.creation_datetime': lambda t: t.strftime("%d-%m-%Y")}))
            display(query_res)

    def display_sample_preview(self):
        self.w_sample_preview.clear_output()
        if self.w_select_sample_id.value is not None:
            with self.w_sample_preview:
                # display(query_available_samples(write_pd_query_from_dict({'battery_id': self.w_select_sample_id.value})))
                print(query_available_samples(write_pd_query_from_dict({'battery_id': self.w_select_sample_id.value})).iloc[0])

    def update_validate_button_state(self):
        self.w_validate.disabled = (self.w_select_sample_id.value is None)

    # def on_specs_value_change(self, which):
    #     def update_fields(_):
    #         self.display_query_result()
    #         self.update_options()#which)
    #     return update_fields

    def on_specs_value_change(self, _=None):
        self.update_options()
        self.display_query_result()

    def on_update_button_clicked(self, _=None):
        update_available_specs()
        update_available_samples()
        self.update_options()
        self.display_query_result()
        # notice: if the old value is not available anymore, an error might be raised!

    def on_reset_button_clicked(self, _=None):
        self.w_specs_manufacturer.value = None
        self.w_specs_composition.value = None
        self.w_specs_form_factor.value = None
        self.w_specs_capacity.value = None
        # self.w_specs_metadata_creation_date.value = None
        # self.w_specs_metadata_creation_process.value = None

    def on_battery_id_change(self, _=None):
        self.display_sample_preview()
        self.update_validate_button_state()

    def callback_call(self, callback_function):
        "Call a callback function and this class instance to it."
        return callback_function(self)

    def _set_specs_observers(self):
        self.w_specs_manufacturer.observe(handler=self.on_specs_value_change, names='value')
        self.w_specs_composition.observe(handler=self.on_specs_value_change, names='value')
        self.w_specs_capacity.observe(handler=self.on_specs_value_change, names='value')
        self.w_specs_form_factor.observe(handler=self.on_specs_value_change, names='value')
        # self.w_specs_metadata_creation_date.observe(handler=self.update_options, names='value')

    def _unset_specs_observers(self):
        self.w_specs_manufacturer.unobserve(handler=self.on_specs_value_change, names='value')
        self.w_specs_composition.unobserve(handler=self.on_specs_value_change, names='value')
        self.w_specs_capacity.unobserve(handler=self.on_specs_value_change, names='value')
        self.w_specs_form_factor.unobserve(handler=self.on_specs_value_change, names='value')
        # self.w_specs_metadata_creation_date.unobserve(handler=self.update_options, names='value')