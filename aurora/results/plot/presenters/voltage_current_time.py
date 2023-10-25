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

    def extract_data(self, dataset: dict) -> tuple:
        """docstring"""
        x = dataset["time"] / 3600.
        yv = dataset["Ewe"]
        yi = dataset["I"] * 1000.
        return (x, yv, yi)

    def plot_series(self, eid: int, dataset: dict) -> None:
        """docstring"""
        x, yv, yi = (np.array(a) for a in self.extract_data(dataset))
        label, color = self.get_series_properties(eid)
        line, = self.model.ax.plot(x, yv, label=f"{label}:V", color=color)
        self.model.ax2.plot(x, yi, "--", label=f"{label}:I", color=color)
        self.store_color(line)
