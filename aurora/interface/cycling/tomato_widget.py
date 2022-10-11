# -*- coding: utf-8 -*-
"""
Widget to setup tomato's settings
"""

import logging
from aurora.interface.cycling.technique_widget import BOX_STYLE
import ipywidgets as ipw
from aurora.schemas.utils import remove_empties_from_dict_decorator

class TomatoSettingsWidget(ipw.VBox):

    BOX_STYLE = {'description_width': 'initial'}
    BOX_LAYOUT = {'width': '95%'}
    GRID_LAYOUT = {"grid_template_columns": "30% 65%", 'width': '100%', 'margin': '5px'} # 'padding': '10px', 'border': 'solid 2px', 'max_height': '500px'

    def __init__(self, label_defaults={}):

        # initialize job settings
        self.w_job_header = ipw.HTML("Tomato Job configuration:")

        ## TODO: UPDATE SUGGESTED LABEL of sample_node, etc...
        self.w_job_method_node_label = ipw.Text(
            description="AiiDA Method node label:",
            placeholder="Enter a name for the CyclingSpecsData node",
            value=label_defaults.get("method", ""),
            layout=self.BOX_LAYOUT, style=self.BOX_STYLE)
        self.w_job_calc_node_label = ipw.Text(
            description="AiiDA CalcJob node label:",
            placeholder="Enter a name for the BatteryCyclerExperiment node",
            value=label_defaults.get("calcjob", ""),
            layout=self.BOX_LAYOUT, style=self.BOX_STYLE)
        self.w_job_unlock_when_finished = ipw.Checkbox(
            value=False, description="Unlock when finished?") # indent=True)
        self.w_job_verbosity = ipw.Dropdown(
            description="Verbosity:", value="INFO",
            options=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],)
            #layout=self.BOX_LAYOUT, style=self.BOX_STYLE)

        self.w_job_monitored = ipw.Checkbox(
            value=False, description="Monitored job?") # indent=True)

        self.w_job_monitor_refresh_rate = ipw.BoundedIntText(
            description="Refresh rate (s):", min=10, max=1e99, step=1,
            value=600, style=self.BOX_STYLE)
        self.w_job_monitor_check_type = ipw.Dropdown(
            description="Check type:", value="discharge_capacity",
            options=["discharge_capacity", "charge_capacity"],)
        self.w_job_monitor_threshold = ipw.BoundedFloatText(
            description="Threshold:", min=1e-6, max=1.0,
            value=0.80, style=self.BOX_STYLE)
        self.w_job_monitor_consecutive_cycles = ipw.BoundedIntText(
            description="Number of consecutive cycles:", min=2, max=1e6, step=1,
            value=2, style=self.BOX_STYLE)
        self.w_job_monitor_parameters = ipw.VBox()

        # initialize widgets
        super().__init__()
        self.children = [
            self.w_job_header,
            ipw.GridBox([
                ipw.VBox([
                    self.w_job_method_node_label,
                    self.w_job_calc_node_label]),
                ipw.VBox([
                    self.w_job_unlock_when_finished,
                    self.w_job_verbosity])
            ], layout=self.GRID_LAYOUT),
            self.w_job_monitored,
            self.w_job_monitor_parameters,
            # self.w_validate,
        ]
        self._build_job_monitor_parameters()

        # setup automations
        self.w_job_monitored.observe(self._build_job_monitor_parameters, names="value")

    @property
    def monitor_job_settings(self):
        if self.w_job_monitored.value:
            return dict(
                refresh_rate = self.w_job_monitor_refresh_rate.value,
                check_type = self.w_job_monitor_check_type.value,
                threshold = self.w_job_monitor_threshold.value,
                consecutive_cycles = self.w_job_monitor_consecutive_cycles.value,
            )
        else:
            return {}

    @property
    @remove_empties_from_dict_decorator
    def job_settings(self):
        return dict(
            method_node_label = self.w_job_method_node_label.value,
            calc_node_label = self.w_job_calc_node_label.value,
            unlock_when_finished = self.w_job_unlock_when_finished.value,
            verbosity = self.w_job_verbosity.value,
            monitor_job_settings = self.monitor_job_settings,
        )
    
    def _build_job_monitor_parameters(self, dummy=None):
        if self.w_job_monitored.value:
            self.w_job_monitor_parameters.children = [
                self.w_job_monitor_refresh_rate,
                self.w_job_monitor_check_type,
                self.w_job_monitor_threshold,
                self.w_job_monitor_consecutive_cycles,
            ]
        else:
            self.w_job_monitor_parameters.children = []