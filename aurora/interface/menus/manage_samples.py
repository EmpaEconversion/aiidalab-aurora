import json
import os

import ipywidgets as ipw
import pandas as pd
from ipyfilechooser import FileChooser
from IPython.display import display

from aurora import __version__
from aurora.engine import submit_experiment
from aurora.interface.sample.sample_filter import SampleFilterWidget
from aurora.models import AvailableSamplesModel, BatteryExperimentModel
from aurora.schemas.battery import BatterySample
from aurora.schemas.utils import dict_to_formatted_json


class ManageSamplesMenu(ipw.VBox):

    def __init__(self):
        """Constructs the `Manage Samples` menu from components"""
        self.available_samples_model = AvailableSamplesModel()
        self.experiment_model = BatteryExperimentModel()

        # ------------------------------------------------------------ #
        # HEADER BOX
        # ------------------------------------------------------------ #
        self.w_header_box = ipw.VBox([
            ipw.HTML(value=f"<h1>Aurora - Manage Samples</h1>"),
            ipw.HTML(value=f"Aurora app version {__version__}"),
        ],
                                     layout={
                                         'width': '100%',
                                         'border': 'solid black 4px',
                                         'padding': '10px'
                                     })
        # ------------------------------------------------------------ #

        self.w_sample_filter = SampleFilterWidget(self.available_samples_model)

        home_directory = os.path.expanduser('~')
        self.w_filepath_explorer = FileChooser(
            home_directory,
            layout={
                'width': '85%',
                'margin': '5px'
            },
        )
        self.w_button_import = ipw.Button(
            description="Import Samples",
            button_style='primary',
            tooltip="Import samples",
            layout={
                'height': '85px',
                'margin': '5px'
            },
            disabled=True,
            icon="fa-upload",
        )

        self.w_textin_basename = ipw.Text(
            description='Base name:',
            placeholder='Full name `<basename>-nn`',
            disabled=True,
            layout={'width': '45%'},
        )
        self.w_textin_description = ipw.Text(
            description='Description:',
            placeholder='Description for the battery',
            value='Li-based',
            disabled=True,
            layout={'width': '99%'},
        )
        self.w_textin_manufacturer = ipw.Text(
            description='Manufacturer:',
            placeholder='Name of the manufacturer',
            value='Empa',
            disabled=True,
            layout={'width': '55%'},
        )
        self.w_textin_process = ipw.Text(
            description='C. Process:',
            placeholder='Creation process',
            value='Created by robot',
            disabled=True,
            layout={'width': '60%'},
        )
        self.w_textin_ctime = ipw.Text(
            description='C. Time:',
            placeholder='Creation time',
            disabled=True,
            layout={'width': '40%'},
        )

        super().__init__()
        self.children = [
            self.w_header_box,
            ipw.VBox([
                ipw.HTML(value="<h3>Available Samples</h3>"),
                self.w_sample_filter,
                ipw.HTML(value="<h3>Import samples from robot output</h3>"),
                ipw.VBox([
                    self.w_filepath_explorer,
                    ipw.HBox([
                        ipw.VBox([
                            ipw.HBox([
                                self.w_textin_basename,
                                self.w_textin_manufacturer
                            ]),
                            self.w_textin_description,
                            ipw.HBox(
                                [self.w_textin_process, self.w_textin_ctime]),
                        ],
                                 layout={'width': '75%'}),
                        ipw.VBox([
                            self.w_button_import,
                        ],
                                 layout={'width': '25%'}),
                    ]),
                ],
                         layout={
                             'width': '100%',
                             'padding': '10px'
                         })
            ])
        ]
        #                ipw.HBox([
        #                    ipw.VBox([
        #                        ipw.HBox([self.w_textin_basename, self.w_textin_manufacturer]),
        #                        self.w_textin_description,
        #                        ipw.HBox([self.w_textin_process, self.w_textin_ctime]),
        #                        self.w_filepath_explorer,
        #                    ], layout={'width': '75%'}
        #                    ),
        #                    ipw.VBox([
        #                        self.w_button_import,
        #                    ], layout={'width': '25%'}),
        #                ]),
        #                ],
        #                layout={'width': '100%', 'padding': '10px'}
        #            ),
        #        ]

        #        def minifunc(change):
        #            raise ValueError(f'Well look at this! {change}')
        #
        #        self.w_sample_filter.observe(minifunc, 'filtered_samples_id')

        self.w_button_import.on_click(self.on_click_import_samples)

        self.w_filepath_explorer.register_callback(
            self.on_filepath_select)  # this is a click

        self.w_textin_basename.observe(self.check_if_importable, 'value')
        self.w_textin_description.observe(self.check_if_importable, 'value')
        self.w_textin_manufacturer.observe(self.check_if_importable, 'value')
        self.w_textin_process.observe(self.check_if_importable, 'value')

    def on_filepath_select(self, widget=None):
        self.w_textin_basename.disabled = self.w_filepath_explorer.selected is None
        self.w_textin_description.disabled = self.w_filepath_explorer.selected is None
        self.w_textin_manufacturer.disabled = self.w_filepath_explorer.selected is None
        self.w_textin_process.disabled = self.w_filepath_explorer.selected is None
        #self.w_textin_ctime.disabled = False
        self.check_if_importable()

    def check_if_importable(self, widget=None):
        import_is_disabled = False
        import_is_disabled = import_is_disabled or self.w_filepath_explorer.selected is None
        import_is_disabled = import_is_disabled or self.w_textin_basename.value == ''
        import_is_disabled = import_is_disabled or self.w_textin_description.value == ''
        import_is_disabled = import_is_disabled or self.w_textin_manufacturer.value == ''
        import_is_disabled = import_is_disabled or self.w_textin_process.value == ''
        self.w_button_import.disabled = import_is_disabled

    def on_click_import_samples(self, widget=None):
        """Wrapper for parseadd_robot_output"""
        filepath = self.w_filepath_explorer.selected
        if filepath is None:
            return
        basedict = {
            "basename": self.w_textin_basename.value,
            "manufacturer": self.w_textin_manufacturer.value,
            "description": self.w_textin_description.value,
            "creation_datetime": "2022-06-28T05:59:00+00:00",
            "creation_process": self.w_textin_process.value,
        }
        self.available_samples_model.parseadd_robot_output(filepath, basedict)
        self.experiment_model.update_available_samples()
        self.w_sample_filter.update_options()
