import ipywidgets as ipw
import numpy as np

from ..model import PlotModel
from ..view import PlotView
from .parents import MultiSeriesPlotPresenter


class CapacityVoltagePlotPresenter(MultiSeriesPlotPresenter):
    """
    docstring
    """

    TITLE = 'C vs. V'

    X_LABEL = 'Ewe [V]'

    Y_LABEL = 'Q [mAh]'

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

    def extract_data(self, dataset: dict) -> tuple:
        """docstring"""

        x = dataset["Ewe"]

        if 'Q' not in dataset:

            t = dataset['time']
            I = dataset['I']

            Q = []
            for i in range(len(t)):
                q = np.trapz(I[:i], t[:i])
                Q.append(q)

            dataset['Q'] = np.array(Q)

        y = dataset['Q'] / 3.6

        return (x, y)

    def plot_series(self, eid: int, dataset: dict) -> None:
        """docstring"""
        x, y = (np.array(a) for a in self.extract_data(dataset))
        y *= self.model.get_weights(eid).get(self.view.electrode.value, 1)
        color = self.model.colors.get(eid)
        self.model.ax.plot(x, y, label=eid, color=color)

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
