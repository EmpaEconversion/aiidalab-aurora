from contextlib import suppress
from typing import List, Tuple

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

        _range = ipw.Text(
            layout={
                "width": "90%",
            },
            description="range",
            placeholder="start:end:step",
        )

        points = ipw.Text(
            layout={
                "width": "90%",
            },
            description="points",
            placeholder="e.g 0 5 -1",
        )

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
            'range': _range,
            'points': points,
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
        y *= self.model.get_weights(eid).get(self.view.electrode.value, 1)
        x, y = self._down_select(x, y)
        color = self.model.colors.get(eid)
        self.model.ax.plot(x, y, '.', label=eid, color=color)

    ###################
    # PRIVATE METHODS #
    ###################

    def _set_event_handlers(self) -> None:
        """docstring"""

        super()._set_event_handlers()

        self.view.range.observe(
            names='value',
            handler=self._on_range_change,
        )

        self.view.points.observe(
            names='value',
            handler=self._on_points_change,
        )

        self.view.electrode.observe(
            names='value',
            handler=self._on_electrode_change,
        )

    def _on_range_change(self, _=None) -> None:
        """docstring"""

        self.view.points.unobserve(
            names='value',
            handler=self._on_points_change,
        )

        self.view.points.value = ''

        self.view.points.observe(
            names='value',
            handler=self._on_points_change,
        )

        self.refresh()

    def _on_points_change(self, _=None) -> None:
        """docstring"""

        self.view.range.unobserve(
            names='value',
            handler=self._on_range_change,
        )

        self.view.range.value = ''

        self.view.range.observe(
            names='value',
            handler=self._on_range_change,
        )

        self.refresh()

    def _on_electrode_change(self, _=None) -> None:
        """docstring"""
        self.refresh(skip_x=True)

    def _down_select(self, x: np.ndarray, y: np.ndarray) -> Tuple:
        """docstring"""
        x, y = self._filter_range(x, y)
        x, y = self._filter_points(x, y)
        return (x, y)

    def _filter_range(self, x: np.ndarray, y: np.ndarray) -> Tuple:
        """docstring"""

        start, end, step = None, None, None
        args: List[str] = self.view.range.value.split(':')

        if args:
            with suppress(Exception):
                start = int(args[0])

        if len(args) > 1:
            with suppress(Exception):
                end = int(args[1]) + 1 or None

        if len(args) > 2:
            with suppress(Exception):
                step = int(args[2])

        return (x[start:end:step], y[start:end:step])

    def _filter_points(self, x: np.ndarray, y: np.ndarray) -> Tuple:
        """docstring"""
        raw_list: List[str] = self.view.points.value.strip().split()
        points = [int(p) for p in raw_list if p.strip('-').isnumeric()]
        valid = [p for p in set(points) if -len(x) - 1 <= p < len(x)]
        return (x[valid], y[valid]) if valid else (x, y)
