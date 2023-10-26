from __future__ import annotations

import ipywidgets as ipw
from IPython.display import display

from .model import InputPreviewModel
from .view import InputPreviewView


class InputPreviewController:
    """docstring"""

    def __init__(
        self,
        view: InputPreviewView,
        model: InputPreviewModel,
    ) -> None:
        """docstring"""
        self.view = view
        self.model = model
        self.__set_event_listeners()

    def display_preview(self, _=None) -> None:
        """
        Verify that all the input is there and display preview.
        If so, enable submission button.
        """

        self.view.clear_output()

        with self.view:

            if not self.model.samples:
                notice = "No battery samples selected!"
                return self.__signal_missing_input(notice)

            self.__display_samples_preview()

            if not self.model.protocols:
                notice = "No cycling protocols selected!"
                return self.__signal_missing_input(notice)

            self.__display_protocols_preview()

            if not self.model.settings:
                notice = "No protocol settings selected!"
                return self.__signal_missing_input(notice)

            self.__display_settings_and_monitors()

            print("✅ All good!")
            self.model.valid_input = True

    ###########
    # PRIVATE #
    ###########

    def __display_samples_preview(self) -> None:
        """docstring"""

        samples = ipw.Output(
            layout={
                "max_height": "300px",
                "overflow_y": "scroll",
                "align_items": "center",
            })

        display(
            ipw.VBox(
                layout={},
                children=[
                    ipw.HTML("<h3 style='margin: 0'>Samples</h3>"),
                    samples,
                ],
            ))

        with samples:
            self.model.preview_samples()

    def __display_protocols_preview(self) -> None:
        """docstring"""

        self.view.protocols.children = []
        self.view.protocols.selected_index = None

        self.view.settings.clear_output()
        self.view.monitors.clear_output()

        display(
            ipw.HBox(
                layout={
                    "margin": "0 0 10px",
                    "grid_gap": "5px",
                },
                children=[
                    ipw.VBox(
                        layout={
                            "width": "50%",
                        },
                        children=[
                            ipw.HTML("<h3>Protocols</h3>"),
                            self.view.protocols,
                        ],
                    ),
                    ipw.VBox(
                        layout={
                            "width": "50%",
                            "grid_gap": "5px",
                        },
                        children=[
                            ipw.VBox(
                                layout={
                                    "flex": "1",
                                },
                                children=[
                                    ipw.HTML("<h3>Settings</h3>"),
                                    self.view.settings,
                                ],
                            ),
                            ipw.VBox(
                                layout={
                                    "flex": "1",
                                },
                                children=[
                                    ipw.HTML("<h3>Monitors</h3>"),
                                    self.view.monitors,
                                ],
                            ),
                        ],
                    )
                ],
            ))

        for protocol in self.model.protocols:

            output = ipw.Output()

            self.view.protocols.children += (output, )
            index = len(self.view.protocols.children) - 1
            self.view.protocols.set_title(index, protocol)

            with output:
                self.model.preview_protocol(protocol)

        self.view.protocols.selected_index = 0

    def __display_settings_and_monitors(
        self,
        change: dict | None = None,
    ) -> None:
        """docstring"""

        if (index := change["new"] if change else 0) is None:
            return

        protocol = self.model.protocols[index]

        self.view.settings.clear_output()
        with self.view.settings:
            self.model.preview_settings(protocol)

        self.view.monitors.clear_output()
        with self.view.monitors:
            self.model.preview_monitors(protocol)

    def __signal_missing_input(self, message: str) -> None:
        """docstring"""
        print(f"❌ {message}")
        self.model.valid_input = False

    def __set_event_listeners(self) -> None:
        """Set event listeners."""
        self.view.protocols.observe(
            self.__display_settings_and_monitors,
            "selected_index",
        )
