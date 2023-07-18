"""
Cycling protocol customizable by the user.
TODO: Enable the user to save a customized protocol.
"""
import logging
import os
from typing import get_args

import aiida_aurora.schemas.cycling
import ipywidgets as ipw
from aiida_aurora.schemas.cycling import ElectroChemPayloads
from ipyfilechooser import FileChooser

from .technique_widget import TechniqueParametersWidget


class CyclingCustom(ipw.VBox):

    BOX_STYLE = {'description_width': '25%'}
    BOX_STYLE_2 = {'description_width': 'initial'}
    BOX_LAYOUT = {'width': '95%'}
    BOX_LAYOUT_3 = {'width': '95%', 'padding': '5px', 'margin': '10px'}
    BUTTON_STYLE = {'description_width': '30%'}
    BUTTON_LAYOUT = {'margin': '5px'}
    BUTTON_LAYOUT_2 = {'width': '20%', 'margin': '5px'}
    # BUTTON_LAYOUT_3 = {'width': '43.5%', 'margin': '5px'}
    BUTTON_LAYOUT_3 = {'width': '10%', 'margin': '5px'}
    DEFAULT_PROTOCOL = aiida_aurora.schemas.cycling.OpenCircuitVoltage
    _TECHNIQUES_OPTIONS = {
        f"{Technique.schema()['properties']['short_name']['default']}  ({Technique.schema()['properties']['technique']['default']})":
        Technique
        for Technique in get_args(ElectroChemPayloads)
    }

    def __init__(self, experiment_model, validate_callback_f):

        if experiment_model is None:
            raise ValueError('An experiment model must be provided.')
        self.experiment_model = experiment_model
        self.experiment_model.suscribe_observer(self)

        if not callable(validate_callback_f):
            raise TypeError(
                "validate_callback_f should be a callable function")

        # initialize widgets
        self.w_header = ipw.HTML(value="<h2>Custom Protocol</h2>")
        self.w_protocol_label = ipw.HTML(value="Sequence:")
        self.w_protocol_steps_list = ipw.Select(rows=10,
                                                value=None,
                                                description="",
                                                layout={})

        self._update_protocol_steps_list_widget_options()

        self.w_button_add = ipw.Button(description="",
                                       button_style='success',
                                       tooltip="Add step",
                                       icon='plus',
                                       style=self.BUTTON_STYLE,
                                       layout=self.BUTTON_LAYOUT_2)
        self.w_button_remove = ipw.Button(description="",
                                          button_style='danger',
                                          tooltip="Remove step",
                                          icon='minus',
                                          style=self.BUTTON_STYLE,
                                          layout=self.BUTTON_LAYOUT_2)
        self.w_button_up = ipw.Button(description="",
                                      button_style='',
                                      tooltip="Move step up",
                                      icon='arrow-up',
                                      style=self.BUTTON_STYLE,
                                      layout=self.BUTTON_LAYOUT_2)
        self.w_button_down = ipw.Button(description="",
                                        button_style='',
                                        tooltip="Move step down",
                                        icon='arrow-down',
                                        style=self.BUTTON_STYLE,
                                        layout=self.BUTTON_LAYOUT_2)

        self.w_button_load = ipw.Button(description="Load",
                                        button_style='',
                                        tooltip="Load protocol",
                                        icon='',
                                        style=self.BUTTON_STYLE,
                                        layout=self.BUTTON_LAYOUT_3)
        self.w_button_save = ipw.Button(description="Save",
                                        button_style='',
                                        tooltip="Save protocol",
                                        icon='',
                                        style=self.BUTTON_STYLE,
                                        layout=self.BUTTON_LAYOUT_3)
        home_directory = os.path.expanduser('~')
        self.w_filepath_explorer = FileChooser(
            home_directory,
            layout={
                "flex": "1",
                'margin': '5px'
            },
        )
        self.w_filepath_explorer.default_path = home_directory
        self.w_filepath_explorer.default_filename = 'saved_protocol.json'
        self.w_filepath_explorer.reset()

        # initialize protocol steps list
        # self._protocol_steps_list = ElectroChemSequence(method=[])
        # self.add_protocol_step()

        # initialize current step properties widget
        self.w_selected_step_technique_name = ipw.Dropdown(
            description="Technique:",
            options=self._TECHNIQUES_OPTIONS,
            value=type(self.selected_step_technique),
            layout=self.BOX_LAYOUT,
            style=self.BOX_STYLE)
        self.w_selected_step_parameters = TechniqueParametersWidget(
            self.selected_step_technique, layout=self.BOX_LAYOUT_3)
        self.w_selected_step_params_save_button = ipw.Button(
            description="Save",
            button_style='info',
            tooltip="Save current parameters",
            icon='check',
            style=self.BUTTON_STYLE,
            layout=self.BUTTON_LAYOUT_2)
        self.w_selected_step_params_discard_button = ipw.Button(
            description="Discard",
            button_style='',
            tooltip="Discard current parameters",
            icon='times',
            style=self.BUTTON_STYLE,
            layout=self.BUTTON_LAYOUT_2)

        self.w_method_node_label = ipw.Text(
            description="AiiDA Method node label:",
            placeholder="Enter a name for the CyclingSpecsData node",
            layout={
                'width': 'auto',
                "margin": "5px 0",
            },
            style=self.BOX_STYLE_2,
        )

        self.w_validate = ipw.Button(description="Validate",
                                     button_style='success',
                                     tooltip="Validate the selected test",
                                     icon='check',
                                     disabled=False,
                                     style=self.BUTTON_STYLE,
                                     layout=self.BUTTON_LAYOUT)

        # initialize widgets
        super().__init__()
        self.children = [
            self.w_header,
            ipw.HBox(
                layout={},
                children=[
                    self.w_filepath_explorer,
                    self.w_button_load,
                    self.w_button_save,
                ],
            ),
            self.w_protocol_label,
            ipw.HBox(
                layout={
                    'width': 'auto',
                },
                children=[
                    ipw.VBox(
                        layout={
                            "width": "30%",
                            "margin": "0 5px 0 0",
                        },
                        children=[
                            self.w_protocol_steps_list,
                            ipw.HBox(
                                layout={"justify_content": "space-between"},
                                children=[
                                    self.w_button_add,
                                    self.w_button_remove,
                                    self.w_button_up,
                                    self.w_button_down,
                                ],
                            ),
                        ],
                    ),
                    ipw.VBox(
                        layout={
                            "width": "70%",
                            'border': 'solid darkgrey 1px',
                            'padding': '5px',
                        },
                        children=[
                            self.w_selected_step_technique_name,
                            self.w_selected_step_parameters,
                            ipw.HBox(
                                layout={},
                                children=[
                                    self.w_selected_step_params_save_button,
                                    self.w_selected_step_params_discard_button,
                                ],
                            ),
                        ],
                    )
                ],
            ),
            self.w_method_node_label,
            self.w_validate,
        ]

        # setup automations
        # steps list
        self.w_protocol_steps_list.observe(
            self._build_current_step_properties_widget, names='index')

        # self.w_button_add.on_click(self.add_protocol_step)
        # self.w_button_remove.on_click(self.remove_protocol_step)
        # self.w_button_up.on_click(self.move_protocol_step_up)
        # self.w_button_down.on_click(self.move_protocol_step_down)

        self.w_button_add.on_click(self.w_button_add_click)
        self.w_button_remove.on_click(self.w_button_remove_click)
        self.w_button_up.on_click(self.w_button_up_click)
        self.w_button_down.on_click(self.w_button_down_click)

        self.w_button_load.on_click(self.button_load_protocol_click)
        self.w_button_save.on_click(self.button_save_protocol_click)

        # current step's properties:
        #   if technique type changes, we need to initialize a new technique from scratch the widget observer may detect a change
        #   even when a new step is selected therefore we check whether the new technique is the same as the one stored in
        #   self.protocol_steps_list (another possibility would be to deactivate the observer before updating the technique name)
        self.w_selected_step_technique_name.observe(
            self._build_technique_parameters_widgets, names='value')
        # save or discard current step's parameters
        self.w_selected_step_params_save_button.on_click(
            self.save_current_step_properties)
        self.w_selected_step_params_discard_button.on_click(
            self.discard_current_step_properties)
        # validate protocol
        self.w_validate.on_click(
            lambda arg: self.callback_call(validate_callback_f))

    def update(self):
        """Receive updates from the model"""
        self._update_protocol_steps_list_widget_options()
        self._build_current_step_properties_widget()
        # Automatically done by _build_current_step_properties_widget
        # self._build_technique_parameters_widgets()

    @property
    def protocol_steps_list(self):
        "The list of steps composing the cycling protocol. Each step must be one of the allowed ElectroChemPayloads."
        return self.experiment_model.selected_protocol
        # return self._protocol_steps_list

    @property
    def selected_step_technique(self):
        "The step that is currently selected."
        return self.experiment_model.selected_protocol.method[
            self.w_protocol_steps_list.index]
        # return self.protocol_steps_list.method[self.w_protocol_steps_list.index]

    @selected_step_technique.setter
    def selected_step_technique(self, technique):
        self.experiment_model.selected_protocol.method[
            self.w_protocol_steps_list.index] = technique
        # self.protocol_steps_list.method[self.w_protocol_steps_list.index] = technique

    def _count_technique_occurencies(self, technique):
        return [
            type(step)
            for step in self.experiment_model.selected_protocol.method
        ].count(technique)
        # return [type(step) for step in self.protocol_steps_list.method].count(technique)

    def _update_protocol_steps_list_widget_options(self, new_index=None):
        old_selected_index = self.w_protocol_steps_list.index
        self.w_protocol_steps_list.options = [
            f"[{idx + 1}] - {step.name}" for idx, step in enumerate(
                self.experiment_model.selected_protocol.method)
        ]
        # self.w_protocol_steps_list.options = [f"[{idx + 1}] - {step.name}" for idx, step in enumerate(self.protocol_steps_list.method)]
        if new_index is not None:
            old_selected_index = new_index
        if (old_selected_index is None) or (old_selected_index < 0):
            self.w_protocol_steps_list.index = 0
        elif old_selected_index >= self.experiment_model.selected_protocol.n_steps:
            self.w_protocol_steps_list.index = self.experiment_model.selected_protocol.n_steps - 1
        # elif old_selected_index >= self.protocol_steps_list.n_steps:
        #    self.w_protocol_steps_list.index = self.protocol_steps_list.n_steps - 1
        else:
            self.w_protocol_steps_list.index = old_selected_index

    def DEFAULT_STEP_NAME(self, technique):
        return f"{technique.schema()['properties']['short_name']['default']}_{self._count_technique_occurencies(technique) + 1}"

    def add_protocol_step(self, dummy=None):
        name = self.DEFAULT_STEP_NAME(self.DEFAULT_PROTOCOL)
        logging.debug(f"Adding protocol step {name}")
        self.experiment_model.selected_protocol.add_step(
            self.DEFAULT_PROTOCOL(name=name))
        self._update_protocol_steps_list_widget_options(
            new_index=self.experiment_model.selected_protocol.n_steps - 1)
        # self.protocol_steps_list.add_step(self.DEFAULT_PROTOCOL(name=name))
        # self._update_protocol_steps_list_widget_options(new_index=self.protocol_steps_list.n_steps-1)

    def remove_protocol_step(self, dummy=None):
        self.experiment_model.selected_protocol.remove_step(
            self.w_protocol_steps_list.index)
        # self.protocol_steps_list.remove_step(self.w_protocol_steps_list.index)
        self._update_protocol_steps_list_widget_options()

    def move_protocol_step_up(self, dummy=None):
        self.experiment_model.selected_protocol.move_step_backward(
            self.w_protocol_steps_list.index)
        # self.protocol_steps_list.move_step_backward(self.w_protocol_steps_list.index)
        self._update_protocol_steps_list_widget_options(
            new_index=self.w_protocol_steps_list.index - 1)

    def move_protocol_step_down(self, dummy=None):
        _ = self.experiment_model.selected_protocol.move_step_forward(
            self.w_protocol_steps_list.index)
        # moved = self.protocol_steps_list.move_step_forward(self.w_protocol_steps_list.index)
        self._update_protocol_steps_list_widget_options(
            new_index=self.w_protocol_steps_list.index + 1)

    # SELECTED STEP METHODS
    def _build_current_step_properties_widget(self, dummy=None):
        """Build the list of properties of the current step."""
        logging.debug(
            f"Building current step (index={self.w_protocol_steps_list.index}, name={self.w_protocol_steps_list.value}) widget"
        )
        self.w_selected_step_technique_name.value = type(
            self.selected_step_technique)
        # self.w_selected_step_label.value = self.selected_step_technique.name
        self._build_technique_parameters_widgets()

    def _build_technique_parameters_widgets(self, dummy=None):
        """Build widget of parameters for the given technique."""
        logging.debug("Building technique parameters")
        # check if the technique is the same as the one stored in the selected step
        if isinstance(
                self.w_selected_step_technique_name.value,
                type(self.selected_step_technique),
        ):
            # if so, reinitialize the widget using its parameters
            logging.debug("  from selected_step_technique")
            self.w_selected_step_parameters.__init__(
                self.selected_step_technique, layout=self.BOX_LAYOUT_3)
        else:
            # if not, it means that the user changed the technique. We have to pass an instance of the new one
            logging.debug("  from scratch")
            technique = self.w_selected_step_technique_name.value()
            technique.name = self.DEFAULT_STEP_NAME(
                self.w_selected_step_technique_name.value)
            logging.debug(f"  {technique.name}")
            self.w_selected_step_parameters.__init__(technique,
                                                     layout=self.BOX_LAYOUT_3)

    def save_current_step_properties(self, dummy=None):
        "Save label/parameters of the selected step from the widget into technique object"
        logging.debug("Saving current step properties")
        # initialize a new Technique object of the chosen type
        self.selected_step_technique = self.w_selected_step_technique_name.value(
        )
        self.selected_step_technique.name = self.w_selected_step_parameters.tech_name
        for pname, pvalue in self.w_selected_step_parameters.selected_tech_parameters.items(
        ):
            self.selected_step_technique.parameters[pname].value = pvalue
        logging.debug(
            f"  Parameters saved: {self.w_selected_step_parameters.selected_tech_parameters.items()}"
        )
        self._update_protocol_steps_list_widget_options()

    def discard_current_step_properties(self, dummy=None):
        "Discard parameters of the selected step and reload them from the technique object"
        logging.debug("Discarding current step properties")
        # i.e. just rebuild the parameters widget
        self._build_current_step_properties_widget()

    def callback_call(self, callback_function):
        "Call a callback function and this class instance to it."
        return callback_function(self)

    ################################################################################
    # NEW DESIGN
    ################################################################################
    # TODO: figure out what the b param is

    def w_button_add_click(self, b):
        """Click event for w_button_add"""
        self.experiment_model.add_protocol_step()
        number_of_steps = self.experiment_model.selected_protocol.n_steps
        self._update_protocol_steps_list_widget_options(
            new_index=number_of_steps - 1)

    def w_button_remove_click(self, b):
        """Click event for w_button_remove"""
        self.experiment_model.remove_protocol_step(
            self.w_protocol_steps_list.index)

    def w_button_up_click(self, b):
        """Click event for w_button_up"""
        # TODO I need to add a guard on the index?
        current_index = self.w_protocol_steps_list.index
        self.experiment_model.move_protocol_step_up(current_index)
        self._update_protocol_steps_list_widget_options(
            new_index=current_index - 1)

    def w_button_down_click(self, b):
        """Click event for w_button_down"""
        # TODO I need to add a guard on the index?
        current_index = self.w_protocol_steps_list.index
        self.experiment_model.move_protocol_step_down(current_index)
        self._update_protocol_steps_list_widget_options(
            new_index=current_index + 1)

    def button_load_protocol_click(self, dummy=None):
        """Loads the protocol from a file."""
        # filepath = '/home/aiida/saved_protocol.json'
        filepath = self.w_filepath_explorer.selected
        if filepath is None:
            return
        self.experiment_model.load_protocol(filepath)

    def button_save_protocol_click(self, dummy=None):
        """Saves the protocol from a file."""
        filepath = self.w_filepath_explorer.selected
        if filepath is None:
            return
        self.experiment_model.save_protocol(filepath)
