from typing import List

import ipywidgets as ipw


class ResultsView(ipw.VBox):
    """
    docstring
    """

    SINGLE_PLOT_TYPES = [
        ('Current vs time', 'current_time'),
        ('Voltage vs time', 'voltage_time'),
        ('Voltage & current vs time', 'voltagecurrent_time'),
        ('Capacity vs voltage', 'capacity_voltage'),
        ('Capacity vs cycle', 'capacity_cycle'),
    ]

    def __init__(self) -> None:
        """docstring"""

        self.experiment_selector = ipw.SelectMultiple(
            layout={
                "width": "auto",
            },
            style={
                "description_width": "95px",
            },
            rows=10,
            description="Experiments:",
        )

        self.experiment_selector.add_class("select-monospace")

        self.plot_type_selector = ipw.Dropdown(
            layout={},
            style={
                'description_width': '95px',
            },
            description="Select plot type:",
            value=None,
            options=self.SINGLE_PLOT_TYPES,
        )

        self.plot_button = ipw.Button(
            layout={
                "width": "fit-content",
            },
            button_style='primary',
            tooltip="Generate plot for selected experiments",
            icon='line-chart',
            disabled=True,
        )

        self.update_button = ipw.Button(
            layout={
                "width": "fit-content",
            },
            tooltip="Update experiments",
            icon='refresh',
        )

        self.info = ipw.Output()

        selection_controls = ipw.HBox(
            layout={
                "margin": "4px 0 2px 0",
            },
            children=[
                self.plot_type_selector,
                self.plot_button,
                self.update_button,
                self.info,
            ],
        )

        experiment_selection_container = ipw.VBox(
            layout={
                "margin": "0 2px",
            },
            children=[
                self.experiment_selector,
                selection_controls,
            ],
        )

        self.plots_container = ipw.VBox()

        super().__init__(
            layout={},
            children=[
                experiment_selection_container,
                self.plots_container,
            ],
        )

    @property
    def plot_views(self) -> List:
        return list(self.plots_container.children)
