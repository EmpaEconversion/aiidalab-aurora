import contextlib
from typing import Dict, List

import ipywidgets as ipw
import numpy as np
import pandas as pd
import seaborn as sns

from ..model import PlotModel
from ..view import PlotView
from .parents import StatisticalPlotPresenter


class CapacitySwarmPlotPresenter(StatisticalPlotPresenter):
    """
    docstring
    """

    TITLE = "Capacity Swarm"

    X_LABEL = "Cycle"

    Y_LABEL = "Qd [mAh]"

    max_cycle = -1

    BOX_PROPS = {
        'boxprops': {
            'facecolor': (0.25, 0.25, 0.25, 0.1),
        },
        'linewidth': 0.25,
    }

    HIDDEN_BOX_PROPS = {
        'boxprops': {
            'facecolor': 'none',
            'edgecolor': 'none'
        },
        'medianprops': {
            'color': 'none'
        },
        'whiskerprops': {
            'color': 'none'
        },
        'capprops': {
            'color': 'none'
        }
    }

    def __init__(
        self,
        model: PlotModel,
        view: PlotView,
    ) -> None:
        """docstring"""

        super().__init__(model, view)

        num_cycles = ipw.BoundedIntText(
            layout={
                "width": "140px",
            },
            description="# to show",
            min=1,
            max=10,
            value=10,
        )

        draw_box = ipw.Checkbox(
            layout={},
            description='show box',
            value=True,
        )

        draw_swarm = ipw.Checkbox(
            layout={},
            description='show swarm',
            value=True,
        )

        _range = ipw.Text(
            layout={
                "width": "190px",
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
            'num_cycles': num_cycles,
            'draw_box': draw_box,
            'draw_swarm': draw_swarm,
            'range': _range,
            'points': points,
            'electrode': electrode,
        }

        self.add_controls(controls)

    def extract_data(self, dataset: dict) -> pd.DataFrame:
        """docstring"""

        self._set_max_cycle(dataset)

        if self.max_cycle < 0:
            return pd.DataFrame()

        self.view.num_cycles.max = self.max_cycle
        num_cycles = self.view.num_cycles.value

        df_dict: Dict[str, list] = {
            self.X_LABEL: [],
            'eid': [],
            self.Y_LABEL: [],
        }

        for eid, data in dataset.items():
            weights: dict = self.model.get_weights(eid)
            factor = weights.get(self.view.electrode.value, 1) / 3.6
            for cycle, capacity in enumerate(data['Qd'][:num_cycles]):
                df_dict['eid'].append(eid)
                df_dict[self.X_LABEL].append(cycle)
                df_dict[self.Y_LABEL].append(capacity * factor)

        data = pd.DataFrame(df_dict)
        data = data.sort_values([self.X_LABEL, 'eid'])
        data = data.astype({'eid': 'str'})

        return data

    def plot_series(self, eid: int, dataset: dict) -> None:
        """docstring"""
        data = self.extract_data(dataset)
        data = self._down_select(data)
        self._plot_boxplot(data, draw=self.view.draw_box.value)
        self._plot_swarmplot(data, draw=self.view.draw_swarm.value)

    ###########
    # PRIVATE #
    ###########

    def _plot_boxplot(self, data: pd.DataFrame, draw=True) -> None:
        """docstring"""
        sns.boxplot(
            ax=self.model.ax,
            data=data,
            x=self.X_LABEL,
            y=self.Y_LABEL,
            orient="v",
            **self.BOX_PROPS if draw else self.HIDDEN_BOX_PROPS,
        )

    def _plot_swarmplot(self, data: pd.DataFrame, draw=True) -> None:
        """docstring"""
        if draw:
            sns.swarmplot(
                ax=self.model.ax,
                data=self._get_swarm_copy(data),
                x=self.X_LABEL,
                y=self.Y_LABEL,
                orient="v",
                hue='eid',
            )

    def _get_swarm_copy(self, data: pd.DataFrame) -> pd.DataFrame:
        """docstring"""
        swarm_data = data.copy(deep=True)
        x_series = swarm_data[self.X_LABEL]
        old_new_map = {old: new for new, old in enumerate(x_series.unique())}
        swarm_data[self.X_LABEL] = x_series.apply(lambda old: old_new_map[old])
        return swarm_data

    def _set_max_cycle(self, dataset: dict) -> None:
        """docstring"""

        max_cycle = np.inf
        limiting_experiment = 0
        for eid, data in dataset.items():
            last_cycle = len(data['Qd'])
            if last_cycle < max_cycle:
                max_cycle = last_cycle
                limiting_experiment = eid

        if max_cycle > 1:
            message = "Maximum cycle set to lowest final cycle: "
            message += f"{max_cycle} (eid = {limiting_experiment})"
            warning = f"<b style='color: red;'>{message}</b>"
            self.view.warning.value = warning
        else:
            message = "Insufficient valid data - see tabs below for details"
            warning = f"<b style='color: red;'>{message}</b>"
            self.view.warning.value = warning
            return

        self.max_cycle = max_cycle

    def _set_event_handlers(self) -> None:
        """docstring"""

        super()._set_event_handlers()

        self.view.num_cycles.observe(
            names='value',
            handler=self.refresh,
        )

        self.view.draw_box.observe(
            names='value',
            handler=self.refresh,
        )

        self.view.draw_swarm.observe(
            names='value',
            handler=self.refresh,
        )

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

    def _down_select(self, data: pd.DataFrame) -> pd.DataFrame:
        """docstring"""
        data = self._filter_range(data)
        data = self._filter_points(data)
        return data

    def _filter_range(self, data: pd.DataFrame) -> pd.DataFrame:
        """docstring"""

        start, end, step = None, None, None
        args: List[str] = self.view.range.value.split(':')

        max_cycle = data[self.X_LABEL].max()

        if args:
            with contextlib.suppress(Exception):
                start = int(args[0])

        if len(args) > 1:
            with contextlib.suppress(Exception):
                end = int(args[1]) + 1 or None

        if len(args) > 2:
            with contextlib.suppress(Exception):
                step = int(args[2])

        _range = list(np.array(range(max_cycle + 1))[start:end:step])

        return data.query(f'{self.X_LABEL} == {_range}') if _range else data

    def _filter_points(self, data: pd.DataFrame) -> pd.DataFrame:
        """docstring"""
        raw_list: List[str] = self.view.points.value.strip().split()
        points = [int(p) for p in raw_list if p.strip('-').isnumeric()]
        max_cycle = data[self.X_LABEL].max() + 1
        valid = [p for p in set(points) if -max_cycle - 1 <= p < max_cycle]
        _range = list(np.array(range(max_cycle))[valid])
        return data.query(f'{self.X_LABEL} == {_range}') if _range else data
