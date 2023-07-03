from typing import Tuple

import numpy as np

from .parents import MultiSeriesPlotPresenter


class CapacityCyclePlotPresenter(MultiSeriesPlotPresenter):
    """
    docstring
    """

    TITLE = 'C vs. Cycle #'

    X_LABEL = 'Cycle'

    Y_LABEL = 'Qd [mAh]'

    def extract_data(self, dataset: dict) -> Tuple:
        """docstring"""
        x = [*range(len(dataset['Qd']))]
        y = dataset['Qd'] / 3.6
        return (x, y)

    def plot_series(self, eid: int, dataset: dict) -> None:
        """docstring"""
        x, y = (np.array(a) for a in self.extract_data(dataset))
        self.model.ax.plot(x, y, '.', label=eid)
