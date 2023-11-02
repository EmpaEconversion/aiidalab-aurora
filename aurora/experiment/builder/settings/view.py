from __future__ import annotations

from typing import Any

import ipywidgets as ipw
from aiida_aurora.schemas.utils import remove_empties_from_dict_decorator

from ..utils import ResettableView

BOX_STYLE = {
    "description_width": "90px",
}

BUTTON_BOX_LAYOUT = {
    "justify_content": "space-between",
}

BUTTON_LAYOUT = {
    "width": "fit-content",
}

SAVE_BOX_LAYOUT = {
    "margin": "0 0 0 98px",
}

NOTICE_LAYOUT = {
    "margin": "2px 2px 2px 5px",
}

MAIN_LAYOUT = {
    "width": "auto",
    "margin": "2px",
    "padding": "10px",
    "border": "solid darkgrey 1px"
}


class SettingsSelectorView(ResettableView):
    """The Tomato settings selection view."""

    def __init__(self) -> None:
        """`SettingSelectorView` constructor."""

        self.defaults: dict[ipw.ValueWidget, Any] = {}

        self.selector = ipw.Dropdown(
            layout={},
            style=BOX_STYLE,
            value=None,
            description="Protocol:",
        )
        self.defaults[self.selector] = self.selector.value

        super().__init__(
            layout=MAIN_LAYOUT,
            children=[
                self.selector,
                self.__build_settings_section(),
                self.__build_monitors_section(),
                self.__build_controls(),
            ],
        )

    @property
    @remove_empties_from_dict_decorator
    def current_state(self) -> dict:
        """docstring"""

        state: dict[str, dict] = {
            "settings": {
                "verbosity": self.verbosity.value,
            },
            "monitors": {},
        }

        if self.is_monitored.value:
            state["settings"]["snapshot"] = {
                "frequency": self.refresh_rate.value,
                "prefix": "snapshot"
            }
            state["monitors"]["capacity"] = {
                "refresh_rate": self.refresh_rate.value,
                "check_type": self.check_type.value,
                "threshold": self.threshold.value,
                "consecutive_cycles": self.consecutive.value,
            }

        return state

    ###########
    # PRIVATE #
    ###########

    def __build_settings_section(self) -> ipw.VBox:
        """Build a container for tomato settings.

        Returns
        -------
        `ipw.VBox`
            A container for tomato settings widgets.
        """

        self.verbosity = ipw.Dropdown(
            style=BOX_STYLE,
            description="Verbosity:",
            options=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            value="INFO",
        )
        self.defaults[self.verbosity] = self.verbosity.value

        return ipw.VBox(
            layout={},
            children=[
                self.verbosity,
            ],
        )

    def __build_monitors_section(self) -> ipw.VBox:
        """Build a container for monitor settings.

        Returns
        -------
        `ipw.VBox`
            A container for monitor settings widgets.
        """

        self.is_monitored = ipw.Checkbox(
            style=BOX_STYLE,
            description="Monitored job?",
            value=False,
        )
        self.defaults[self.is_monitored] = self.is_monitored.value

        self.refresh_rate = ipw.BoundedIntText(
            style=BOX_STYLE,
            description="Frequency (s):",
            min=10,
            max=1e99,
            step=1,
            value=600,
        )
        self.defaults[self.refresh_rate] = self.refresh_rate.value

        self.check_type = ipw.Dropdown(
            style=BOX_STYLE,
            description="Check type:",
            options=["discharge_capacity", "charge_capacity"],
            value="discharge_capacity",
        )
        self.defaults[self.check_type] = self.check_type.value

        self.threshold = ipw.BoundedFloatText(
            style=BOX_STYLE,
            description="Threshold:",
            min=1e-6,
            max=1.0,
            value=0.80,
        )
        self.defaults[self.threshold] = self.threshold.value

        self.consecutive = ipw.BoundedIntText(
            style=BOX_STYLE,
            description="Consecutive:",
            min=2,
            max=1e6,
            step=1,
            value=2,
        )
        self.defaults[self.consecutive] = self.consecutive.value

        self.monitor_parameters = ipw.VBox()

        return ipw.VBox(
            layout={},
            children=[
                self.is_monitored,
                self.monitor_parameters,
            ],
        )

    def __build_controls(self) -> ipw.HBox:
        """Build selection controls.

        Returns
        -------
        `ipw.HBox`
            A container for selection controls.
        """

        self.save = ipw.Button(
            layout=BUTTON_LAYOUT,
            button_style="success",
            icon="check",
            tooltip="Assign settings/monitors to selected protocol",
            disabled=True,
        )

        self.save_notice = ipw.HTML(layout=NOTICE_LAYOUT)

        return ipw.HBox(
            layout=BUTTON_BOX_LAYOUT,
            children=[
                ipw.HBox(
                    layout=SAVE_BOX_LAYOUT,
                    children=[
                        self.save,
                        self.save_notice,
                    ],
                ),
                self.reset,
            ],
        )
