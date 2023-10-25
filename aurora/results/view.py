from __future__ import annotations

import os

import ipywidgets as ipw
from ipyfilechooser import FileChooser

BUTTON_LAYOUT = {
    "width": "fit-content",
}


class ResultsView(ipw.VBox):
    """
    docstring
    """

    SINGLE_PLOT_TYPES = [
        ('Current vs time', 'current_time'),
        ('Voltage vs time', 'voltage_time'),
        ('Voltage & current vs time', 'voltagecurrent_time'),
        ('Voltage vs capacity', 'voltage_capacity'),
        ('Efficiency vs cycle', 'efficiency_cycle'),
        ('Capacity vs cycle', 'capacity_cycle'),
    ]

    STATISTICAL_PLOT_TYPES = [
        ('Capacity swarm', 'capacity_swarm'),
    ]

    def __init__(self) -> None:
        """docstring"""

        self.weights_label = ipw.Label(
            layout={
                "width": "95px",
                "margin": "0 6px 0 2px",
                "padding": "0 0 0 24px",
            },
            value="Weights file:",
        )

        self.weights_reset_button = ipw.Button(
            layout=BUTTON_LAYOUT,
            button_style="warning",
            icon="refresh",
            tooltip="Reset weights file",
            disabled=True,
        )

        self.weights_filechooser = FileChooser(
            layout={
                "flex": "1",
            },
            path=os.path.expanduser('~'),
        )

        self.group_selector = ipw.Dropdown(
            layout={
                "width": "50%",
            },
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
            value=10,
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
            layout=BUTTON_LAYOUT,
            button_style='primary',
            tooltip="Generate plot for selected experiments",
            icon='line-chart',
            disabled=True,
        )

        self.update_button = ipw.Button(
            layout=BUTTON_LAYOUT,
            tooltip="Update experiments",
            icon='refresh',
        )

        self.group_name = ipw.Text(
            layout={},
            placeholder="Enter group name",
            disabled=True,
        )

        self.group_add_button = ipw.Button(
            layout=BUTTON_LAYOUT,
            button_style="success",
            icon="check",
            tooltip="Add experiments to group",
            disabled=True,
        )

        self.info = ipw.Output()

        selection_controls = ipw.VBox(
            layout={},
            children=[
                ipw.HBox(
                    layout={
                        "justify_content": "space-between",
                    },
                    children=[
                        ipw.HBox(
                            layout={},
                            children=[
                                self.plot_type_selector,
                                self.plot_button,
                                self.update_button,
                            ],
                        ),
                        ipw.HBox(
                            layout={},
                            children=[
                                self.group_name,
                                self.group_add_button,
                            ],
                        ),
                    ],
                ),
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
                    ],
                ),
                ipw.HBox(
                    layout={
                        "margin": "5px 0",
                        "align_items": "center",
                    },
                    children=[
                        self.weights_label,
                        self.weights_reset_button,
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
    def plot_views(self) -> list:
        return list(self.plots_container.children)
