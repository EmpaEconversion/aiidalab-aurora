from typing import Tuple

import numpy as np

from .parents import MultiSeriesPlotPresenter


class VoltageCurrentTimePlotPresenter(MultiSeriesPlotPresenter):
    """
    docstring
    """

    TITLE = 'V & I vs. t'

    X_LABEL = 't [h]'

    Y_LABEL = 'Ewe [V]'

    Y2_LABEL = 'I [mA]'

    def extract_data(self, dataset: dict) -> Tuple:
        """docstring"""
        x = dataset["time"] / 3600.
        yv = dataset["Ewe"]
        yi = dataset["I"] * 1000.
        return (x, yv, yi)

    def plot_series(self, eid: int, dataset: dict) -> None:
        """docstring"""
        x, yv, yi = (np.array(a) for a in self.extract_data(dataset))
        color = self.model.colors.get(eid)
        self.model.ax.plot(x, yv, label=f'{eid} : V', color=color)
        self.model.ax2.plot(x, yi, '--', label=f'{eid} : I', color=color)
