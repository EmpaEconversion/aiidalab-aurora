from typing import Dict, Tuple

import ipywidgets as ipw
import numpy as np
from matplotlib import pyplot as plt
from traitlets import HasTraits, Unicode

from .model import PlotModel
from .view import PlotView


class PlotPresenter(HasTraits):
    """
    docstring
    """
    TITLE = ''

    X_LABEL = ''

    Y_LABEL = ''

    HAS_LEGEND = True

    legend_pad = 0.04

    closing_message = Unicode('')

    def __init__(self, model: PlotModel, view: PlotView) -> None:
        """docstring"""

        self.model = model
        self.view = view

        self._initialize_figure()

    def start(self) -> None:
        """docstring"""
        self._set_event_handlers()
        self._fetch_data()
        self.draw()
        self._set_plot_labels()
        self._show_legend()
        self._show_plot()
        self._store_defaults()

    def close_view(self, _=None, message='closed') -> None:
        """docstring"""
        self.closing_message = message
        self.view.close()

    def add_controls(self, controls: Dict[str, ipw.ValueWidget]) -> None:
        """docstring"""
        for name, control in controls.items():
            setattr(self.view, name, control)
            self.view.controls.children += (control, )

    def remove_controls(self, controls: Tuple[ipw.ValueWidget, ...]) -> None:
        """docstring"""

        current = self.view.current_controls

        control: ipw.ValueWidget
        for control in controls:
            control.unobserve_all()
            current.remove(control)

        self.view.controls.children = tuple(current)

    def extract_data(self, dataset: dict) -> Tuple:
        """docstring"""
        raise NotImplementedError

    def plot_series(self, eid: int, dataset: dict) -> None:
        """docstring"""
        x, y = (np.array(a) for a in self.extract_data(dataset))
        self.model.ax.plot(x, y, label=eid)

    def draw(self) -> None:
        """docstring"""
        raise NotImplementedError

    ###################
    # PRIVATE METHODS #
    ###################

    def _initialize_figure(self) -> None:
        """docstring"""

        plt.ioff()

        with self.view.plot:

            self.model.fig, self.model.ax = plt.subplots(1, figsize=(10, 5))

            self.model.fig.subplots_adjust(
                left=0.22,
                right=0.78,
                bottom=0.1,
                top=0.9,
            )

            self.model.fig.canvas.header_visible = False

        plt.ion()

    def _set_plot_labels(self) -> None:
        """docstring"""
        self.model.ax.set_title(self.TITLE, pad=10)
        self.model.ax.set_xlabel(self.X_LABEL)
        self.model.ax.set_ylabel(self.Y_LABEL)

        if self.model.has_ax2:
            self.model.ax2.set_ylabel(self.Y2_LABEL)

    def _set_event_handlers(self) -> None:
        """docstring"""

        self.view.delete_button.on_click(self.close_view)
        self.view.reset_button.on_click(self._reset_controls)

        self.view.xlim.observe(
            names='value',
            handler=self._update_xlim,
        )

        self.view.ylim.observe(
            names='value',
            handler=self._update_ylim,
        )

    def _fetch_data(self) -> None:
        """docstring"""

        for eid in self.model.experiment_ids:
            info_tab = self._add_info_tab(eid)

            with info_tab:
                self.model.fetch_data(eid)

    def _add_info_tab(self, eid: int) -> ipw.Output:
        """docstring"""

        info_tab = ipw.Output(layout={
            "overflow_y": "auto",
            "max_height": "260px",
        })

        self.view.info.children += (info_tab, )

        tab_index = len(self.view.info.children) - 1
        self.view.info.set_title(tab_index, str(eid))

        self.view.eid_tab_mapping[eid] = tab_index

        return info_tab

    def _update_xlim(self, _=None) -> None:
        """docstring"""
        with self.view.plot:
            xmin, xmax = self.view.xlim.value
            self.model.ax.set_xlim(xmin, xmax)

    def _update_ylim(self, _=None) -> None:
        """docstring"""
        with self.view.plot:
            ymin, ymax = self.view.ylim.value
            self.model.ax.set_ylim(ymin, ymax)

    def _store_defaults(self) -> None:
        """docstring"""

        self._set_axes_controls()

        self.control_defaults = {
            control: control.value
            for control in self.view.current_controls
        }

    def _set_axes_controls(self) -> None:
        """docstring"""
        self._set_xaxis_control()
        self._set_yaxis_control()

    def _set_xaxis_control(self) -> None:
        """docstring"""
        min, max = self.model.ax.get_xlim()
        min, max = (min, max) if min < max else (max, min)
        self._set_axis_limit_control_params('xlim', min, max)

    def _set_yaxis_control(self) -> None:
        """docstring"""
        min, max = self.model.ax.get_ylim()
        min, max = (min, max) if min < max else (max, min)
        self._set_axis_limit_control_params('ylim', min, max)

    def _set_axis_limit_control_params(
        self,
        name: str,
        min: float,
        max: float,
    ) -> None:
        """docstring"""
        control: ipw.ValueWidget = getattr(self.view, name)
        control.min = -np.inf
        control.max = max
        control.min = min
        control.value = (min, max)
        control.step = (max - min) / 100

    def _show_legend(self) -> None:
        """docstring"""

        if not self.HAS_LEGEND:
            return

        target = self.model.ax

        with self.view.plot:
            handles, labels = self.model.ax.get_legend_handles_labels()

            if self.model.has_ax2:
                h2, l2 = self.model.ax2.get_legend_handles_labels()
                handles.extend(h2)
                labels.extend(l2)
                target = self.model.ax2

            if handles and labels:
                target.legend(
                    handles,
                    labels,
                    framealpha=1.,
                    loc='upper left',
                    bbox_to_anchor=(1 + self.legend_pad, 1),
                )

    def _show_plot(self) -> None:
        """docstring"""
        with self.view.plot:
            plt.show()

    def _reset_controls(self, _=None) -> None:
        """docstring"""
        for control in self.view.current_controls:
            control.value = self.control_defaults[control]
