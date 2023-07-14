from typing import Tuple

import ipywidgets as ipw
import numpy as np

from ..model import PlotModel
from ..view import PlotView
from .parents import MultiSeriesPlotPresenter


class CapacityCyclePlotPresenter(MultiSeriesPlotPresenter):
    """
    docstring
    """

    TITLE = 'C vs. Cycle #'

    X_LABEL = 'Cycle'

    Y_LABEL = 'Qd [mAh]'

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
                'anode mass',
                'cathode mass',
                'none',
            ],
            value='cathode mass',
            description='normalize by',
        )

        controls = {
            'electrode': electrode,
        }

        self.add_controls(controls)

    def extract_data(self, dataset: dict) -> Tuple:
        """docstring"""
        x = [*range(len(dataset['Qd']))]
        y = dataset['Qd'] / 3.6
        return (x, y)

    def plot_series(self, eid: int, dataset: dict) -> None:
        """docstring"""
        x, y = (np.array(a) for a in self.extract_data(dataset))
        y *= self.weights[eid].get(self.view.electrode.value, 1)
        color = self.model.colors.get(eid)
        self.model.ax.plot(x, y, '.', label=eid, color=color)

    ###################
    # PRIVATE METHODS #
    ###################

    def _set_event_handlers(self) -> None:
        """docstring"""

        super()._set_event_handlers()

        self.view.electrode.observe(
            names='value',
            handler=self._on_electrode_change,
        )

    def _on_electrode_change(self, _=None) -> None:
        """docstring"""
        self.refresh(skip_x=True)
