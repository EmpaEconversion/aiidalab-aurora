from __future__ import annotations

from aiida.orm import load_node
from aiida_aurora.utils.cycling_analysis import cycling_analysis
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

from ..model import ResultsModel


class PlotModel():
    """
    docstring
    """
    has_ax2 = False

    COLORS = {
        False: [
            "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b",
            "#e377c2", "#7f7f7f", "#bcbd22", "#17becf", "#aec7e8", "#ffbb78",
            "#98df8a", "#ff9896", "#c5b0d5", "#c49c94", "#f7b6d2", "#c7c7c7",
            "#dbdb8d", "#9edae5", "#5254a3", "#393b79", "#637939", "#e6550d",
            "#ad494a", "#ad494a", "#7b4173", "#d6616b", "#e7ba52", "#d9d9d9",
            "#ce6dbd", "#bd9e39"
        ],
        True: ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
    }

    def __init__(
        self,
        results_model: ResultsModel,
        experiment_ids: list[int],
    ) -> None:
        """docstring"""

        self.__results_model = results_model
        self.experiment_ids = experiment_ids
        self.data: dict[int, dict] = {}

        self.fig: Figure
        self.ax: Axes
        self.ax2: Axes

        # True/False are the states of the sub-batch toggle button
        self.colors: dict[bool, dict[str, str]] = {
            True: {},
            False: {},
        }

        self.__results_model.observe(
            names="weights_file",
            handler=self._reset_weights,
        )

    def fetch_data(self, eid: int) -> None:
        """docstring"""
        if eid in self.__results_model.results:
            data, log = self.__results_model.results[eid].values()
            self.data[eid] = data
            print(log)
            return

        self.run_cycling_analysis(eid)

    def run_cycling_analysis(self, eid: int) -> None:
        """docstring"""
        job_node = load_node(pk=eid)
        data, log = cycling_analysis(job_node)
        self.__results_model.results[eid] = {'data': data, 'log': log}
        self.data[eid] = self.__results_model.results[eid]['data']
        print(log)

    def get_weights(self, eid: int) -> dict[str, float]:
        """docstring"""
        if 'weights' not in self.data[eid]:
            self.data[eid]['weights'] = self.__results_model.get_weights(eid)
        return self.data[eid]['weights']

    def has_weights(self) -> bool:
        """docstring"""
        for eid in self.experiment_ids:
            weights: dict = self.data[eid].get('weights', {})
            present = bool(weights)
            not_one = all(weight != 1. for weight in weights.values())
            if present and not_one:
                return True
        return False

    def set_color(self, is_by_subbatch: bool, line: Line2D) -> None:
        """docstring"""
        if is_by_subbatch not in self.colors:
            self.colors[is_by_subbatch] = {}
        self.colors[is_by_subbatch][line.get_label()] = line.get_color()

    def get_color(self, is_by_subbatch: bool, label: str) -> str | None:
        """docstring"""
        colors = self.colors[is_by_subbatch]
        index = len(colors) % (4 if is_by_subbatch else 32)
        return colors.get(label) or self.COLORS[is_by_subbatch][index]

    ###########
    # PRIVATE #
    ###########

    def _reset_weights(self, _=None) -> None:
        """docstring"""
        for eid in self.experiment_ids:
            if eid in self.data and 'weights' in self.data[eid]:
                del self.data[eid]['weights']
