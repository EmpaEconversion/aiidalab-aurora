from __future__ import annotations

import pandas as pd
from matplotlib.collections import PathCollection

from ..presenter import PlotPresenter


class MultiSeriesPlotPresenter(PlotPresenter):
    """
    docstring
    """

    def draw(self) -> None:
        """docstring"""
        with self.view.plot:
            for eid, dataset in self.model.data.items():
                if dataset:
                    self.plot_series(eid, dataset)

    def download_data(self, _=None) -> None:
        """docstring"""

        directory, prefix = self.get_destination_components()

        axes = [self.model.ax]

        if self.model.has_ax2:
            axes.append(self.model.ax2)

        for i, ax in enumerate(axes, 1):

            suffix = f"ax_{i}.csv"
            path = f"{directory}/{prefix}_{suffix}"

            plot = {line.get_label(): line.get_data() for line in ax.lines}

            df = pd.DataFrame()

            for series, (x, y) in plot.items():
                new = pd.DataFrame({f"{series}_x": x, f"{series}_y": y})
                df = pd.concat([df, new], axis=1)

            with open(path, "w+") as file:
                df.to_csv(file, index=False)


class StatisticalPlotPresenter(PlotPresenter):
    """
    docstring
    """

    def draw(self) -> None:
        """docstring"""
        with self.view.plot:
            if self.model.data:
                self.plot_series(0, self.model.data)

    def download_data(self, _=None) -> None:
        """docstring"""

        directory, prefix = self.get_destination_components()
        path = f"{directory}/{prefix}.csv"

        ax = self.model.ax

        handles, labels = ax.get_legend_handles_labels()
        colors = [patch.get_facecolor() for patch in handles]

        legend_color_label_map: dict[str, str] = {
            str(color[0]): label
            for color, label in zip(colors, labels)
        }

        tick_mapping: dict[int, int] = {
            text.get_position()[0]: int(text.get_text())
            for text in ax.get_xticklabels()
        }

        data_per_series: dict[str, list[list[int | float]]] = {
            label: [[], []]  # [[x-coords], [y-coords]]
            for label in labels
        }

        collection: PathCollection
        for collection in ax.collections:

            if not isinstance(collection, PathCollection):
                continue

            colors = collection.get_facecolors()
            offsets = collection.get_offsets()
            x_coords = offsets[:, 0]
            y_coords = offsets[:, 1]

            for c, x, y in zip(colors, x_coords, y_coords):
                label = legend_color_label_map[str(c)]
                mapped_x = tick_mapping[int(round(x))]
                data_per_series[label][0].append(mapped_x)
                data_per_series[label][1].append(y)

        df = pd.DataFrame()
        for series, (x, y) in data_per_series.items():
            new = pd.DataFrame({f"{series}_x": x, f"{series}_y": y})
            df = pd.concat([df, new], axis=1).convert_dtypes()

        with open(path, "w+") as file:
            df.to_csv(file, index=False)
