from __future__ import annotations

import ipywidgets as ipw


class PlotView(ipw.Accordion):
    """
    docstring
    """

    def __init__(self, pid: int = 0) -> None:
        """docstring"""

        self.id = pid

        plot_area = self._build_plot_area()

        controls_container = self._build_controls_container()

        super().__init__([
            ipw.VBox(
                layout={},
                children=[
                    plot_area,
                    controls_container,
                ],
            )
        ])

    @property
    def current_controls(self) -> list[ipw.ValueWidget]:
        return list(self.controls.children)

    def _build_plot_area(self):
        """docstring"""

        buttons = self._build_buttons()

        self.warning = ipw.HTML(layout={
            "margin": "auto 10px",
        }, )

        self.plot = ipw.Output(layout={
            "align_items": "center",
        })

        return ipw.VBox(
            layout={
                "border": "solid 1px grey",
                "margin": "0 2px 5px 2px",
                "padding": "5px",
            },
            children=[
                ipw.HBox(
                    layout={},
                    children=[
                        self.warning,
                        buttons,
                    ],
                ),
                self.plot,
            ],
        )

    def _build_buttons(self) -> ipw.HBox:
        """docstring"""

        self.download_button = ipw.Button(
            layout={
                "width": "fit-content",
            },
            button_style='success',
            tooltip="Download data",
            icon='download',
        )

        self.reset_button = ipw.Button(
            layout={
                "width": "fit-content",
            },
            button_style='warning',
            tooltip="Reset controls",
            icon='refresh',
        )

        self.delete_button = ipw.Button(
            layout={
                "width": "fit-content",
            },
            button_style='danger',
            tooltip="Delete plot",
            icon='trash',
        )

        return ipw.HBox(
            layout={
                "padding": "5px",
                "margin": "0 0 0 auto"
            },
            children=[
                self.download_button,
                self.reset_button,
                self.delete_button,
            ],
        )

    def _build_controls_container(self) -> ipw.Accordion:
        """docstring"""

        self.controls = self._build_controls()

        self.info = ipw.Tab(layout={
            "flex": "5",
        })
        self.eid_tab_mapping: dict[int, int] = {}

        controls_container = ipw.Accordion(
            layout={},
            children=[
                ipw.HBox(
                    layout={},
                    children=[
                        self.controls,
                        self.info,
                    ],
                ),
            ],
            selected_index=None,
        )

        controls_container.set_title(0, 'Plot controls')

        return controls_container

    def _build_controls(self) -> ipw.VBox:
        """docstring"""

        self.xlim = ipw.FloatRangeSlider(
            layout={
                "width": "90%",
            },
            description="x-limit",
        )

        self.ylim = ipw.FloatRangeSlider(
            layout={
                "width": "90%",
            },
            description="y-limit",
        )

        self.y2lim: ipw.FloatRangeSlider

        return ipw.VBox(
            layout={
                "flex": "4",
            },
            children=[
                self.xlim,
                self.ylim,
            ],
        )
