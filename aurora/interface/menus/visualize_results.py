# -*- coding: utf-8 -*-

import ipywidgets as ipw
from aurora.engine.results import query_jobs, cycling_analysis
import aiida_aurora.utils
import pandas as pd
from aurora import __version__


class CyclingResultsWidget(ipw.VBox):
    BOX_STYLE = {'description_width': 'initial'}
    BOX_LAYOUT_1 = {'width': '40%'}
    BUTTON_STYLE = {'description_width': '30%'}
    BUTTON_LAYOUT = {'margin': '5px'}
    OUTPUT_LAYOUT = {'max_height': '500px', 'width': '90%', 'overflow': 'scroll', 'border': 'solid 1px', 'margin': '5px', 'padding': '5px'}
    PLOT_TYPES = [('', ''), ('Voltage & current vs time', 'voltagecurrent_time'), ('Voltage vs time', 'voltage_time'), ('Current vs time', 'current_time'), ('Capacity vs cycle', 'capacity_cycle')]

    def __init__(self):

        # ------------------------------------------------------------ #
        # HEADER BOX
        # ------------------------------------------------------------ #
        self.w_header_box = ipw.VBox([
                ipw.HTML(value=f"<h1>Aurora - Visualize Results</h1>"),
                ipw.HTML(value=f"Aurora app version {__version__}"),
                ],
                layout={'width': '100%', 'border': 'solid black 4px', 'padding': '10px'}
        )
        # ------------------------------------------------------------ #

        # initialize widgets
        self.w_joblist_header = ipw.HTML(value="<h2>Job list</h2>")
        self.w_job_days = ipw.BoundedIntText(
            description="Last n. of days:", min=0, max=1e6, step=1,
            value=0, style=self.BOX_STYLE)
        self.w_update = ipw.Button(
            description="Update",
            button_style='', tooltip="Update list", icon='refresh',
            style=self.BUTTON_STYLE, layout=self.BUTTON_LAYOUT)
        self.w_joblist = ipw.Output(layout=self.OUTPUT_LAYOUT)

        self.w_select_sample_id = ipw.Dropdown(
            description="Select Battery ID:", value=None,
            layout=self.BOX_LAYOUT_1, style={'description_width': 'initial'})
        
        self.w_results_header = ipw.HTML(value="<h2>Results</h2>")
        self.w_plot_type = ipw.Dropdown(
            description="Select plot type:", value=None,
            options=self.PLOT_TYPES,
            layout=self.BOX_LAYOUT_1, style={'description_width': 'initial'})
        self.w_plot_draw = ipw.Button(
            description="Draw plot",
            button_style='info', tooltip="Draw plot", icon='line-chart',
            disabled=True,
            style=self.BUTTON_STYLE, layout=self.BUTTON_LAYOUT)
        self.w_log_output = ipw.Output()
        self.w_plot_output = ipw.Output()

        super().__init__()
        self.children = [
            self.w_header_box,
            self.w_joblist_header,
            ipw.HBox([self.w_job_days, self.w_update]),
            self.w_joblist,
            self.w_select_sample_id,
            self.w_results_header,
            ipw.HBox([self.w_plot_type, self.w_plot_draw]),
            self.w_log_output,
            self.w_plot_output
        ]
        
        # initialize options
        self.update_job_list()
#         self._create_figure(title='')
        
        # setup automations
        self.w_update.on_click(self.update_job_list)
        self.w_select_sample_id.observe(self._load_data)
        self.w_plot_draw.on_click(self.draw_plot)

    def _build_job_list(self):
        query = query_jobs(self.w_job_days.value)
        self.job_list = pd.DataFrame(query)
        self.job_list['ctime'] = self.job_list['ctime'].dt.strftime('%Y-%m-%d %H:%m:%S')
        self.job_list.rename(columns={
            'id': 'ID',
            'label': 'Label',
            'ctime': 'creation time',
            'attributes.process_label': 'job type',
            'attributes.state': 'state',
            'attributes.status': 'reason',
            'extras.monitored': 'monitored'
        }, inplace=True)
        self.job_list['monitored'] = self.job_list['monitored'].astype(bool)

    @staticmethod
    def _build_sample_id_options(table):
        """Returns a (option_string, ID) list."""
        return [("", None)] + [(f"<{row['ID']:5} >   {row['Label']}", row['ID']) for index, row in table.iterrows()]

    def _update_sample_id_options(self):
        """Update the specs' options."""
#         self._unset_specs_observers()
        self.w_select_sample_id.options = self._build_sample_id_options(self.job_list)
#         self._set_specs_observers()

    def update_job_list(self, dummy=None):
        self._build_job_list()
        self.w_joblist.clear_output()
        with self.w_joblist:
            display(self.job_list.style.hide_index())
        self._update_sample_id_options()

    @property
    def selected_job_id(self):
        return self.w_select_sample_id.value
    
    @property
    def selected_plot_type(self):
        return self.w_plot_type.value

    def _cycling_analysis(self):
        return cycling_analysis(self.selected_job_id)
    
    def _load_data(self, dummy=None):
        "Load data, store it, and print some output info."
        self.w_log_output.clear_output()
        if self.selected_job_id:
            self.w_plot_draw.disabled = False
            with self.w_log_output:
                # NOTE TODO: maybe we do not always want to perform a cycling analysis, loading the data would be enough
                self.data = self._cycling_analysis()
        else:
            self.w_plot_draw.disabled = True

        # reset plot
        self.w_plot_type.value = None
        self.w_plot_output.clear_output()

    def draw_plot(self, dummy=None):       
        title = None
        if self.selected_job_id and self.selected_plot_type:
            self.w_plot_output.clear_output()
            with self.w_plot_output:
                # NOTE: this is a very rudimental way of creating plots
                # --> check the internet for the best way to work with matplotlib plots in ipywidgets
                # e.g. https://swdevnotes.com/python/2021/interactive-charts-with-ipywidgets-matplotlib/
                # CURRENT BUG: once created, plots cannot be deleted
                # I think we need to implement a way to update a figure/axes
                if not self.data:
                    print("ERROR: No data loaded!")
                elif self.selected_plot_type == 'voltagecurrent_time':
                    aiida_aurora.utils.plot.plot_Ewe_I(self.data)
                elif self.selected_plot_type == 'voltage_time':
                    aiida_aurora.utils.plot.plot_Ewe(self.data)
                elif self.selected_plot_type == 'current_time':
                    aiida_aurora.utils.plot.plot_I(self.data)
                elif self.selected_plot_type == 'capacity_cycle':
                    aiida_aurora.utils.plot.plot_Qd(self.data)
