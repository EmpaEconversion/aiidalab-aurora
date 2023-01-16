# -*- coding: utf-8 -*-

import pandas as pd
import ipywidgets as ipw
import aiida_aurora.utils

from aurora.engine.results import query_jobs, cycling_analysis
from aurora.interface.analyze import OutputExplorerComponent, ResultsPlotterComponent
from aurora import __version__


class CyclingResultsWidget(ipw.VBox):
    """Description pending"""

    def __init__(self):
        """Description pending"""

        # HEADER BOX
        self.w_header_box = ipw.VBox([
                ipw.HTML(value=f"<h1>Aurora - Visualize Results</h1>"),
                ipw.HTML(value=f"Aurora app version {__version__}"),
                ],
                layout={'width': '100%', 'border': 'solid black 4px', 'padding': '10px'}
        )

        # SUB-COMPONENTS
        self.w_output_explorer = OutputExplorerComponent()
        self.w_results_plotter = ResultsPlotterComponent()

        super().__init__()
        self.children = [
            self.w_header_box,
            self.w_output_explorer,
            self.w_results_plotter,
        ]
