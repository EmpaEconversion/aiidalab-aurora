import ipywidgets as ipw
import pandas as pd
from IPython.display import display

from aurora.engine.results import query_jobs


class OutputExplorerComponent(ipw.VBox):
    """Description pending"""

    BOX_STYLE = {'description_width': 'initial'}
    BOX_LAYOUT_1 = {'width': '40%'}
    BUTTON_STYLE = {'description_width': '30%'}
    BUTTON_LAYOUT = {'margin': '5px'}
    OUTPUT_LAYOUT = {
        'height': '500px',
        'width': '90%',
        'overflow': 'scroll',
        'border': 'solid 1px',
        'margin': '5px',
        'padding': '5px'
    }

    def __init__(self):
        """Description pending"""

        # initialize widgets
        self.w_joblist_header = ipw.HTML(value="<h2>Available Jobs</h2>")
        self.w_job_days = ipw.BoundedIntText(description="Last n. of days:",
                                             min=0,
                                             max=1e6,
                                             step=1,
                                             value=0,
                                             style=self.BOX_STYLE)
        self.w_update = ipw.Button(description="Update",
                                   button_style='',
                                   tooltip="Update list",
                                   icon='refresh',
                                   style=self.BUTTON_STYLE,
                                   layout=self.BUTTON_LAYOUT)
        self.w_joblist = ipw.Output(layout=self.OUTPUT_LAYOUT)

        self.w_select_sample_id = ipw.Dropdown(
            description="Select Battery ID:",
            value=None,
            layout=self.BOX_LAYOUT_1,
            style={'description_width': 'initial'})

        super().__init__()
        self.children = [
            self.w_joblist_header,
            ipw.HBox([self.w_job_days, self.w_update]),
            self.w_joblist,
            self.w_select_sample_id,
        ]

        # initialize options
        self.update_job_list()

        # setup automations
        self.w_update.on_click(self.update_job_list)

    def _build_job_list(self):
        query = query_jobs(self.w_job_days.value)
        self.job_list = pd.DataFrame(query)
        if self.job_list.size == 0:
            return
        self.job_list['ctime'] = self.job_list['ctime'].dt.strftime(
            '%Y-%m-%d %H:%m:%S')
        self.job_list.rename(
            columns={
                'id': 'ID',
                'label': 'Label',
                'ctime': 'creation time',
                'attributes.process_label': 'job type',
                'attributes.state': 'state',
                'attributes.status': 'reason',
                'extras.monitored': 'monitored'
            },
            inplace=True,
        )
        self.job_list['monitored'] = self.job_list['monitored'].astype(bool)

    @staticmethod
    def _build_sample_id_options(table):
        """Returns a (option_string, ID) list."""
        return [("", None)
                ] + [(f"<{row['ID']:5} >   {row['Label']}", row['ID'])
                     for index, row in table.iterrows()]

    def _update_sample_id_options(self):
        """Update the specs' options."""
        # self._unset_specs_observers()
        self.w_select_sample_id.options = self._build_sample_id_options(
            self.job_list)

        # self._set_specs_observers()

    def update_job_list(self, dummy=None):
        self._build_job_list()
        self.w_joblist.clear_output()
        with self.w_joblist:
            display(self.job_list.style.hide_index())
        self._update_sample_id_options()

    @property
    def selected_job_id(self):
        return self.w_select_sample_id.value
