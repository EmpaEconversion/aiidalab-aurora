import os
from typing import List

import ipywidgets as ipw
from ipyfilechooser import FileChooser


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

    STATISTICAL_PLOT_TYPES = [
        ('Capacity swarm', 'capacity_swarm'),
    ]

    def __init__(self) -> None:
        """docstring"""

        self.weights_label = ipw.HTML(
            layout={
                "margin": "2px 4px 2px 20px",
            },
            value="Weights file:",
        )

        self.weights_filechooser = FileChooser(
            layout={
                "flex": "1",
            },
            path=os.path.expanduser('~'),
        )

        self.group_selector = ipw.Dropdown(
            layout={},
            style={
                'description_width': '95px',
            },
            description="Select group:",
        )

        self.last_days = ipw.BoundedIntText(
            layout={
                "width": "auto",
            },
            min=0,
            max=999,
            value=999,
            description="Last days:",
        )

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
            options=self.SINGLE_PLOT_TYPES + self.STATISTICAL_PLOT_TYPES,
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
            layout={},
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
                "padding": "15px",
                "border": "1px solid grey",
            },
            children=[
                ipw.HBox(
                    layout={},
                    children=[
                        self.group_selector,
                        self.last_days,
                        self.weights_label,
                        self.weights_filechooser,
                    ],
                ),
                self.experiment_selector,
                selection_controls,
            ],
        )

        self.plots_container = ipw.VBox(layout={"margin": "10px 0 0 0"})

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
