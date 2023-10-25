from __future__ import annotations

from datetime import datetime

import ipywidgets as ipw
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.artist import Artist
from matplotlib.collections import Collection
from matplotlib.lines import Line2D
from matplotlib.patches import PathPatch
from traitlets import HasTraits, Unicode

from aurora.time import TZ

from ..utils import get_experiment_sample_node
from .model import PlotModel
from .view import PlotView


class PlotPresenter(HasTraits):
    """
    docstring
    """
    TITLE = ''

    X_LABEL = ''

    Y_LABEL = ''

    Y2_LABEL = ''

    HAS_LEGEND = True

    bbox_to_anchor = (1.3, 1)

    loc = "upper right"

    NORM_AX = ""

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

    def add_controls(self, controls: dict[str, ipw.ValueWidget]) -> None:
        """docstring"""
        for name, control in controls.items():
            setattr(self.view, name, control)
            self.view.controls.children += (control, )

    def remove_controls(self, controls: tuple[ipw.ValueWidget, ...]) -> None:
        """docstring"""

        current = self.view.current_controls

        control: ipw.ValueWidget
        for control in controls:
            control.unobserve_all()
            current.remove(control)

        self.view.controls.children = tuple(current)

    def extract_data(self, dataset: dict) -> tuple | pd.DataFrame:
        """docstring"""
        raise NotImplementedError

    def plot_series(self, eid: int, dataset: dict) -> None:
        """docstring"""
        x, y = (np.array(a) for a in self.extract_data(dataset))
        label, color = self.get_series_properties(eid)
        line, = self.model.ax.plot(x, y, label=label, color=color)
        self.store_color(line)

    def draw(self) -> None:
        """docstring"""
        raise NotImplementedError

    def refresh(self, _=None, skip_x=False) -> None:
        """docstring"""
        self._reset_plot()
        self.draw()
        self._update_plot_axes(axis='y' if skip_x else 'both')
        self._show_legend()

    def download_data(self, _=None) -> None:
        """docstring"""
        raise NotImplementedError

    def get_destination_components(self) -> tuple[str, ...]:
        """docstring"""

        directory = self.view.file_explorer.selected_path

        if filename := self.view.file_explorer.selected_filename:
            prefix = ".".join(filename.split(".")[:-1])
        else:
            timestamp = datetime.now(TZ).strftime(r"%y%m%d-%H%M%S")
            title = self.TITLE.replace(" ", "_")
            prefix = f"{timestamp}_{title}"

        return directory, prefix

    def get_series_properties(self, eid: int) -> tuple[str, str | None]:
        """docstring"""
        label = self._get_series_label(eid)
        color = self.model.get_color(self.view.sub_batch_toggle.value, label)
        return label, color

    def store_color(self, line: Line2D) -> None:
        """docstring"""
        self.model.set_color(self.view.sub_batch_toggle.value, line)

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

            if self.Y2_LABEL:
                self._add_y2axis()

        plt.ion()

    def _add_y2axis(self) -> None:
        """docstring"""

        with self.view.plot:
            self.model.ax2 = self.model.ax.twinx()

        self._add_y2axis_controls()

        self.model.has_ax2 = True

    def _set_plot_labels(self) -> None:
        """docstring"""
        self.model.ax.set_title(self.TITLE, pad=10)
        self.__set_axis_label("ax", "x")
        self.__set_axis_label("ax", "y")

        if self.model.has_ax2:
            self.__set_axis_label("ax2", "y")

    def __set_axis_label(self, ax: str, axis: str) -> None:
        """docstring"""
        label = self.__get_axis_label(ax, axis)
        getattr(getattr(self.model, ax), f"set_{axis}label")(label)

    def __get_axis_label(self, ax: str, axis: str) -> str:
        """docstring"""
        ax_label = self.__get_default_axis_label(ax, axis)
        return ax_label if axis != self.NORM_AX else self.__normalize(ax_label)

    def __get_default_axis_label(self, ax: str, axis: str) -> str:
        """docstring"""
        if ax == "ax" and axis == "x":
            ax_label = self.X_LABEL
        elif ax == "ax" and axis == "y":
            ax_label = self.Y_LABEL
        elif ax == "ax2" and axis == "x":
            raise ValueError("secondary x-axis not yet supported")
        elif ax == "ax2" and axis == "y":
            ax_label = self.Y2_LABEL
        else:
            raise ValueError(f"{axis} is not a valid axis")
        return ax_label

    def __normalize(self, ax_label: str) -> str:
        """docstring"""
        electrode = getattr(self.view, 'electrode', None)
        weights_present = self.model.has_weights()
        if electrode and electrode.value != 'none' and weights_present:
            return ax_label.replace(']', '/g]')
        return ax_label

    def _set_event_handlers(self) -> None:
        """docstring"""

        self.view.download_button.on_click(self.download_data)
        self.view.delete_button.on_click(self.close_view)
        self.view.reset_button.on_click(self._reset_controls)

        self.view.sub_batch_toggle.observe(
            names="value",
            handler=lambda _: self.refresh(skip_x=True),
        )

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

        number_of_pages = int(np.ceil(len(self.model.experiment_ids) / 8))

        for i in range(number_of_pages):
            self._add_info_page(i)

        for i, eid in enumerate(self.model.experiment_ids):
            page_index = i // 8
            info_tab = self._add_info_tab(page_index, eid)

            with info_tab:
                self.model.fetch_data(eid)

    def _add_info_page(self, index: int) -> None:
        """docstring"""
        self.view.info.children += (ipw.Tab(), )
        self.view.info.set_title(index, f"Page {index + 1}")

    def _add_info_tab(self, page_index: int, eid: int) -> ipw.Output:
        """docstring"""

        info_tab = ipw.Output(layout={
            "overflow_y": "auto",
            "max_height": "260px",
        })

        page = self.view.info.children[page_index]
        page.children += (info_tab, )

        tab_index = len(page.children) - 1
        page.set_title(tab_index, str(eid))

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

    def _update_y2lim(self, _=None) -> None:
        """docstring"""
        with self.view.plot:
            ymin, ymax = self.view.y2lim.value
            self.model.ax2.set_ylim(ymin, ymax)

    def _store_defaults(self) -> None:
        """docstring"""

        self._set_axes_controls()

        self.control_defaults = {
            control: control.value
            for control in self.view.current_controls
        }

    def _add_y2axis_controls(self) -> None:
        """docstring"""

        self.view.ylim.description = "y1-limit"

        y2lim = ipw.FloatRangeSlider(
            layout={"width": "90%"},
            description="y2-limit",
        )

        y2lim.observe(
            names="value",
            handler=self._update_y2lim,
        )

        self.add_controls({'y2lim': y2lim})

    def _set_axes_controls(self, axis='both') -> None:
        """docstring"""

        if axis in ('x', 'both'):
            self._set_xaxis_control()

        if axis in ('y', 'both'):

            self._set_yaxis_control()

            if self.model.has_ax2:
                self._set_y2axis_control()

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

    def _set_y2axis_control(self) -> None:
        """docstring"""
        min, max = self.model.ax2.get_ylim()
        min, max = (min, max) if min < max else (max, min)
        self._set_axis_limit_control_params('y2lim', min, max)

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

    def _update_plot_axes(self, axis='both') -> None:
        """docstring"""
        self._set_plot_labels()
        self._reset_plot_limits(axis)
        self._set_axes_controls(axis)

    def _get_series_label(self, eid: int) -> str:
        """docstring"""
        sample = get_experiment_sample_node(eid)
        metadata = sample["metadata"]
        return (f"{metadata['batch']}-{metadata['subbatch']}"
                if self.view.sub_batch_toggle.value else metadata["name"])

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

            handles, labels = self._get_unique_legend(handles, labels)

            if handles and labels:
                target.legend(
                    handles,
                    labels,
                    framealpha=1.,
                    bbox_to_anchor=self.bbox_to_anchor,
                    loc=self.loc,
                )

    def _get_unique_legend(
        self,
        handles: list,
        labels: list,
    ) -> tuple[list, ...]:
        """docstring"""
        unique = {label: handle for handle, label in zip(handles, labels)}
        return list(unique.values()), list(unique.keys())

    def _show_plot(self) -> None:
        """docstring"""
        with self.view.plot:
            plt.show()

    def _reset_controls(self, _=None) -> None:
        """docstring"""
        for control in self.view.current_controls:
            control.value = self.control_defaults[control]

    def _reset_plot(self) -> None:
        """docstring"""

        axes = [self.model.ax]

        if self.model.has_ax2:
            axes.append(self.model.ax2)

        for ax in axes:

            artist: Artist
            for artist in ax.get_children():
                classes = (Line2D, PathPatch, Collection)
                if any(isinstance(artist, art_class) for art_class in classes):
                    artist.remove()

            ax.legend('', frameon=False)

    def _reset_plot_limits(self, axis='both') -> None:
        """docstring"""

        self.model.ax.relim()
        self.model.ax.autoscale(axis=axis)

        if self.model.has_ax2:
            self.model.ax2.relim()
            self.model.ax2.autoscale(axis=axis)
