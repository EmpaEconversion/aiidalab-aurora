from typing import Dict

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
            min=0,
            max=10,
            value=10,
        )

        controls = {
            'num_cycles': num_cycles,
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
            for cycle, capacity in enumerate(data['Qd'][:num_cycles]):
                df_dict['eid'].append(eid)
                df_dict[self.X_LABEL].append(cycle)
                df_dict[self.Y_LABEL].append(capacity)

        data = pd.DataFrame(df_dict)
        data = data.sort_values([self.X_LABEL, 'eid'])
        data = data.astype({'eid': 'str'})

        return data

    def plot_series(self, eid: int, dataset: dict) -> None:
        """docstring"""

        data = self.extract_data(dataset)

        sns.boxplot(
            ax=self.model.ax,
            data=data,
            x=self.X_LABEL,
            y=self.Y_LABEL,
            orient="v",
            boxprops={"facecolor": (.25, .25, .25, .1)},
            linewidth=0.25,
        )

        sns.swarmplot(
            ax=self.model.ax,
            data=data,
            x=self.X_LABEL,
            y=self.Y_LABEL,
            orient="v",
            hue='eid',
        )

    ###################
    # PRIVATE METHODS #
    ###################

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
