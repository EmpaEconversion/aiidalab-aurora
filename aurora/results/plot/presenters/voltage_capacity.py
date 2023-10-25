import ipywidgets as ipw
import numpy as np

from ..model import PlotModel
from ..view import PlotView
from .parents import MultiSeriesPlotPresenter


class VoltageCapacityPlotPresenter(MultiSeriesPlotPresenter):
    """
    docstring
    """

    TITLE = "V vs. C"

    X_LABEL = "Q [mAh]"

    Y_LABEL = "Ewe [V]"

    NORM_AX = "x"

    def __init__(
        self,
        model: PlotModel,
        view: PlotView,
    ) -> None:
        """docstring"""

        super().__init__(model, view)

        electrode = ipw.RadioButtons(
            layout={},
            options=[
                "anode mass",
                "cathode mass",
                "none",
            ],
            value="cathode mass",
            description="normalize by",
        )

        controls = {
            "electrode": electrode,
        }

        self.add_controls(controls)

    def extract_data(self, dataset: dict) -> tuple:
        """docstring"""
        x = dataset["Q"]
        y = dataset["Ewe"]
        return (x, y)

    def plot_series(self, eid: int, dataset: dict) -> None:
        """docstring"""
        x, y = (np.array(a) for a in self.extract_data(dataset))
        x /= self.model.get_weight(eid, self.view.electrode.value)
        label, color = self.get_series_properties(eid)
        line, = self.model.ax.plot(x, y, label=label, color=color)
        self.store_color(line)

    ###################
    # PRIVATE METHODS #
    ###################

    def _set_event_handlers(self) -> None:
        """docstring"""

        super()._set_event_handlers()

        self.view.electrode.observe(
            names="value",
            handler=self.refresh,
        )
