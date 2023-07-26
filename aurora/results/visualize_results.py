import ipywidgets as ipw

from .analyze import OutputExplorerComponent, ResultsPlotterComponent


class CyclingResultsWidget(ipw.VBox):
    """Description pending"""

    def __init__(self):
        """Description pending"""

        # SUB-COMPONENTS
        self.w_output_explorer = OutputExplorerComponent()
        self.w_results_plotter = ResultsPlotterComponent()

        super().__init__()
        self.children = [
            self.w_output_explorer,
            self.w_results_plotter,
        ]
