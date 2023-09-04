from typing import Callable, List, Optional, Tuple

import ipywidgets as ipw
import pandas as pd
from aiida_aurora.schemas.battery import BatterySample
from aiida_aurora.schemas.utils import (dict_to_formatted_json,
                                        remove_empties_from_dict_decorator)

from aurora.common.models.battery_experiment import BatteryExperimentModel


class SampleFromId(ipw.VBox):
    """
    A sample selection widgets container used in the main panel to
    select samples for an experiment by sample id.

    TODO implement creation and labeling of sample nodes.
    TODO store submitted samples in a group
    TODO retrieve a node if it was already created.

    TODO refactor filters to separate class
    """

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
        'width': 'auto',
        'margin': '2px',
        'padding': '10px',
        'border': 'solid darkgrey 1px'
    }

    PREVIEW_LAYOUT = {
        "margin": "0 2px 20px",
        "max_height": "300px",
        "overflow_y": "scroll",
        "align_items": "center",
    }

    def __init__(
        self,
        experiment_model: BatteryExperimentModel,
        validate_callback_f: Callable,
    ) -> None:
        """Constructor for the sample-selection-by-id widgets
        container.

        Parameters
        ----------
        `experiment_model` : `BatteryExperimentModel`
            The current battery experiment model instance.
        `validate_callback_f` : `Callable`
            A callback function for the validation button.

        Raises
        ------
        `TypeError`
            If the callback function is not callable.
        """

        if not callable(validate_callback_f):
            raise TypeError(
                "validate_callback_f should be a callable function")

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

        self._initialize_filters()

        self._initialize_selectors()

        self._set_event_listeners(validate_callback_f)

    @property
    def current_specs(self) -> dict:
        """A dictionary representing the current selected specs used
        to filter the available samples.

        Returns
        -------
        `dict`
            A dictionary of selected specs.
        """
        return {
            'manufacturer': self.w_specs_manufacturer.value,
            'composition.description': self.w_specs_composition.value,
            'capacity.nominal': self.w_specs_capacity.value,
            'form_factor': self.w_specs_form_factor.value,
            # 'metadata.creation_datetime': self.w_specs_metadata_creation_date.value,
        }

    @property
    def selected_sample_ids(self) -> Tuple[str, ...]:
        return self.w_sample_list.value

    @property
    @remove_empties_from_dict_decorator
    def selected_sample_dict(self) -> List[dict]:
        """A list of sanitized sample dictionaries. Key/null value
        pairs are discarded.

        Returns
        -------
        `List[dict]`
            A list of non-null sample dictionaries.
        """

        dict_query = {'battery_id': get_ids(self.w_selected_list.options)}
        pd_query = self.experiment_model.write_pd_query_from_dict(dict_query)
        results = self.experiment_model.query_available_samples(pd_query)

        selected = []
        for _, result in results.iterrows():
            json = dict_to_formatted_json(result)
            selected.append(json)

        return selected

    @property
    def selected_samples(self) -> List[BatterySample]:
        """A list of samples validated against the `BatterySample`
        schema.

        Returns
        -------
        `List[BatterySample]`
            A list of validated samples as `BatterySample` objects.
        """
        return [
            BatterySample.parse_obj(sample)
            for sample in self.selected_sample_dict
        ]

    #########
    # widgets
    #########

    def _build_filter_container(self) -> ipw.Accordion:
        """Build the filters section. Includes filter widgets and
        controls.

        Returns
        -------
        `ipw.VBox`
            A container for the filter widgets.
        """

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
        """Build a  grid container of filter widgets.

        Returns
        -------
        `ipw.GridBox`
            A grid of filter widgets.
        """

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
                "grid_template_columns": "repeat(2, 49%)",
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
        """Build a container for filter controls.

        Returns
        -------
        `ipw.HBox`
            A container for filter controls.
        """

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
        """Build the sample selection section. Includes widgets for
        sample (de)selection and preview tables.

        Returns
        -------
        `ipw.VBox`
            A container of sample selection widgets.
        """

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
        """Build a container for sample selection including controls.

        Returns
        -------
        `ipw.VBox`
            A container for sample selection widgets.
        """

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
        """Build a container of sample selection controls widgets.

        Returns
        -------
        `ipw.VBox`
            A container of sample selection control widgets.
        """

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
        """Build a container for sample deselection including
        controls.

        Returns
        -------
        `ipw.VBox`
            A container for sample deselection widgets.
        """

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
        """Build a container of sample deselection controls widgets.

        Returns
        -------
        `ipw.VBox`
            A container of sample deselection control widgets.
        """

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

    ###########################
    # TODO migrate to presenter
    ###########################

    def update_spec_options(self) -> None:
        """Update sample filters with newly fetched spec options.
        Filter observation is paused during the process.
        """
        self._unset_specs_observers()
        self._build_spec_options()
        self._set_specs_observers()

    def on_update_filters_button_click(self, _=None) -> None:
        """Fetch and update current spec options."""
        self.experiment_model.update_available_specs()
        self.update_spec_options()

    def on_reset_filters_button_click(self, _=None) -> None:
        """Reset current spec selections."""
        self.w_specs_manufacturer.value = None
        self.w_specs_composition.value = None
        self.w_specs_form_factor.value = None
        self.w_specs_capacity.value = None
        # self.w_specs_metadata_creation_date.value = None
        # self.w_specs_metadata_creation_process.value = None

    def on_spec_value_change(self, _=None):
        """Update spec and sample options."""
        # TODO this does a lot per value change. Consider decoupling!
        self.update_spec_options()
        self.update_sample_options()

    def update_sample_options(self) -> None:
        """Fetch and update current sample options."""
        self.experiment_model.update_available_samples()
        self.w_sample_list.options = self._build_sample_id_options()

    def display_samples_preview(self) -> None:
        """Display details for current sample selection in a
        `pandas.DataFrame`."""

        self.w_selection_preview.clear_output()
        with self.w_selection_preview:
            query = {'battery_id': self.w_sample_list.value}
            self.experiment_model.display_query_results(query)

    def display_selected_samples_preview(self) -> None:
        """Display details for selected samples in a
        `pandas.DataFrame`."""

        self.w_selected_preview.clear_output()
        with self.w_selected_preview:
            query = {'battery_id': get_ids(self.w_selected_list.options)}
            self.experiment_model.display_query_results(query)

    def on_sample_list_click(self, _=None) -> None:
        """Display sample preview for selected sample option."""
        self.display_samples_preview()

    def on_update_button_click(self, _=None) -> None:
        """Fetch and update sample options."""
        self.update_sample_options()

    def on_select_button_click(self, _=None) -> None:
        """Add selected sample option to selected samples list."""
        if sample_ids := self.w_sample_list.value:
            self.experiment_model.add_selected_samples(sample_ids)
        self.update_selected_list_options()

    def on_select_all_button_click(self, _=None) -> None:
        """Add all sample options to selected samples list."""
        if sample_ids := get_ids(self.w_sample_list.options):
            self.experiment_model.add_selected_samples(sample_ids)
        self.update_selected_list_options()

    def on_selected_list_change(self, _=None) -> None:
        """Update validate button state and display preview for
        current selected samples."""
        self.update_validate_button_state()
        self.display_selected_samples_preview()

    def on_deselect_button_click(self, _=None) -> None:
        """Remove selected sample option from selected samples list."""
        if sample_ids := self.w_selected_list.value:
            self.experiment_model.remove_selected_samples(sample_ids)
        self.update_selected_list_options()

    def on_deselect_all_button_click(self, _=None) -> None:
        """Clear selected samples list."""
        # TODO simplify! Just clear the list
        if sample_ids := get_ids(self.w_selected_list.options):
            self.experiment_model.remove_selected_samples(sample_ids)
        self.update_selected_list_options()

    def on_validate_button_click(self, callback_function: Callable):
        """Communicate widget state out to parent container."""
        # TODO use (d)link?
        return callback_function(self)

    def update_validate_button_state(self) -> None:
        """Enable validate button if selected samples are present."""
        self.w_validate.disabled = not self.w_selected_list.options

    def update_selected_list_options(self) -> None:
        """Update selected list options."""
        # TODO discard redundant method!
        self.w_selected_list.options = self._update_selected_list()

    def _build_single_spec_options(
        self,
        spec_field: str,
    ) -> List[Tuple[str, Optional[int]]]:
        """Build spec options by querying the available specs,
        filtering results for the given spec field.

        A count of available samples w.r.t. the selected field
        is computed and added to the option string.

        Parameters
        ----------
        `spec_field` : `str`
            The spec name to query by.

        Returns
        -------
        `List[Tuple]`
            A list of spec-option/battery-id pairs.
        """

        spec_field_options_list = self.experiment_model.query_available_specs(
            spec_field)

        # setup sample query filter from current specs
        # and remove current field from query
        sample_query_filter_dict = self.current_specs.copy()
        sample_query_filter_dict[spec_field] = None

        # perform query of samples
        query = self.experiment_model.write_pd_query_from_dict(
            sample_query_filter_dict)

        result = self.experiment_model.query_available_samples(
            query,
            project=[spec_field, 'battery_id'],
        ).sort_values('battery_id')

        value_counts = result[spec_field].value_counts()

        options_pairs: List[Tuple[str, Optional[int]]] = [
            (f"(no filter)  [{value_counts.sum()}]", None)
        ]

        options_pairs.extend([(
            f"{value}  [{value_counts.get(value, 0)}]",
            value,
        ) for value in spec_field_options_list])

        return options_pairs

    def _build_spec_options(self) -> None:
        """Build spec options for all fields. Current selections are
        stored and reapplied after the process.
        """

        # store current selections
        w_specs_manufacturer_value = self.w_specs_manufacturer.value
        w_specs_composition_value = self.w_specs_composition.value
        w_specs_capacity_value = self.w_specs_capacity.value
        w_specs_form_factor_value = self.w_specs_form_factor.value

        # build options
        self.w_specs_manufacturer.options = self._build_single_spec_options(
            'manufacturer')
        self.w_specs_composition.options = self._build_single_spec_options(
            'composition.description')
        self.w_specs_capacity.options = self._build_single_spec_options(
            'capacity.nominal')
        self.w_specs_form_factor.options = self._build_single_spec_options(
            'form_factor')

        # reapply selections
        self.w_specs_manufacturer.value = w_specs_manufacturer_value
        self.w_specs_composition.value = w_specs_composition_value
        self.w_specs_capacity.value = w_specs_capacity_value
        self.w_specs_form_factor.value = w_specs_form_factor_value

    # @staticmethod
    def _build_sample_id_options(self):
        """Returns a (option_string, battery_id) list."""
        dict_query = self.current_specs
        pd_query = self.experiment_model.write_pd_query_from_dict(dict_query)
        unsorted = self.experiment_model.query_available_samples(pd_query)
        table = unsorted.sort_values('battery_id')

        return [(as_option(r), r['battery_id']) for _, r in table.iterrows()]

    def _update_selected_list(self):
        """Returns a (option_string, battery_id) list."""
        table = self.experiment_model.selected_samples
        return [(as_option(r), r['battery_id']) for _, r in table.iterrows()]

    def _initialize_filters(self) -> None:
        """Initialize filters by querying for available specs."""
        self.on_reset_filters_button_click()
        self.experiment_model.update_available_specs()
        self._build_spec_options()

    def _initialize_selectors(self) -> None:
        """Initialize filters by querying for available sample."""
        self.w_sample_list.value = []
        self.w_selected_list.value = []
        self.on_update_button_click()
        self.display_samples_preview()
        self.display_selected_samples_preview()

    def _set_event_listeners(self, validate_callback_f) -> None:
        """Set up event listeners for children widgets."""

        self.w_update_filters.on_click(self.on_update_filters_button_click)
        self.w_reset_filters.on_click(self.on_reset_filters_button_click)
        self._set_specs_observers()

        self.w_update.on_click(self.on_update_button_click)
        self.w_select.on_click(self.on_select_button_click)
        self.w_select_all.on_click(self.on_select_all_button_click)
        self.w_deselect.on_click(self.on_deselect_button_click)
        self.w_deselect_all.on_click(self.on_deselect_all_button_click)

        self.w_sample_list.observe(
            names='value',
            handler=self.on_sample_list_click,
        )

        self.w_selected_list.observe(
            handler=self.on_selected_list_change,
            names='options',
        )

        self.w_validate.on_click(
            lambda arg: self.on_validate_button_click(validate_callback_f))

    def _set_specs_observers(self) -> None:
        """Set up event listeners for spec filters."""

        self.w_specs_manufacturer.observe(
            handler=self.on_spec_value_change,
            names='value',
        )

        self.w_specs_composition.observe(
            handler=self.on_spec_value_change,
            names='value',
        )

        self.w_specs_capacity.observe(
            handler=self.on_spec_value_change,
            names='value',
        )

        self.w_specs_form_factor.observe(
            handler=self.on_spec_value_change,
            names='value',
        )

        # self.w_specs_metadata_creation_date.observe(
        #     handler=self.update_options,
        #     names='value',
        # )

    def _unset_specs_observers(self) -> None:
        """Unset spec filter event listeners."""

        self.w_specs_manufacturer.unobserve(
            handler=self.on_spec_value_change,
            names='value',
        )

        self.w_specs_composition.unobserve(
            handler=self.on_spec_value_change,
            names='value',
        )

        self.w_specs_capacity.unobserve(
            handler=self.on_spec_value_change,
            names='value',
        )

        self.w_specs_form_factor.unobserve(
            handler=self.on_spec_value_change,
            names='value',
        )

        # self.w_specs_metadata_creation_date.unobserve(
        #     handler=self.update_options,
        #     names='value',
        # )


def as_option(row: pd.Series) -> str:
    """Parse `pandas.Series` row as option string for sample
    selection list.

    Parameters
    ----------
    `row` : `pd.Series`
        A battery sample info row.

    Returns
    -------
    `str`
        A processed string representation of the sample info. Used
        to display sample options in sample selection list.
    """
    return f"{row['battery_id']:8} [{row['manufacturer'].split()[0]}] ({row['capacity.nominal']} {row['capacity.units']}) {row['metadata.name']} {row['composition.description']})"


def get_ids(options: Tuple[Tuple[str, int], ...]) -> List[int]:
    """Extract indices from option tuples.

    Parameters
    ----------
    options : `Tuple[Tuple[str, int], ...]`
        A tuple of `ipywidgets.SelectMultiple` option tuples.

    Returns
    -------
    `List[int]`
        A list of option indices.
    """
    return [i for _, i in options]
