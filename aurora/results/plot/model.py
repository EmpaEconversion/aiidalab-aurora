from typing import Dict, List

from aiida.orm import load_node
from aiida_aurora.utils.cycling_analysis import cycling_analysis
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from ..model import ResultsModel


class PlotModel():
    """
    docstring
    """
    has_ax2 = False

    def __init__(
        self,
        results_model: ResultsModel,
        experiment_ids: List[int],
    ) -> None:
        """docstring"""

        self.__results_model = results_model
        self.experiment_ids = experiment_ids
        self.data: Dict[int, dict] = {}

        self.fig: Figure
        self.ax: Axes
        self.ax2: Axes

        self.colors: Dict[int, str] = {}

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

    def get_weights(self, eid: int) -> Dict[str, float]:
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

    ###########
    # PRIVATE #
    ###########

    def _reset_weights(self, _=None) -> None:
        """docstring"""
        for eid in self.experiment_ids:
            if eid in self.data and 'weights' in self.data[eid]:
                del self.data[eid]['weights']
