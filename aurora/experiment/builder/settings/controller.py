from __future__ import annotations

from .model import SettingsSelectorModel
from .view import SettingsSelectorView


class SettingsSelectorController:
    """A controller class for settings selection.

    Attributes
    ----------
    `view` : `SettingsSelectorView`
        The associated view.
    `model` : `SettingsSelectorModel`
        The associated model.
    """

    def __init__(
        self,
        view: SettingsSelectorView,
        model: SettingsSelectorModel,
    ) -> None:
        """`SettingsSelectorController` constructor.

        Parameters
        ----------
        `view` : `SettingsSelectorView`
            The associated view.
        `model` : `SettingsSelectorModel`
            The associated model.
        """
        self.view = view
        self.model = model
        self.__set_event_listeners()

    def update_selector(self, _=None) -> None:
        """Update selector options."""
        self.view.selector.options = self.model.get_selected_protocols()

    def toggle_monitor_parameters(self, _=None) -> None:
        """Add monitor parameter widgets to view."""
        if self.view.is_monitored.value:
            self.view.monitor_parameters.children = [
                self.view.refresh_rate,
                self.view.check_type,
                self.view.threshold,
                self.view.consecutive,
            ]
        else:
            self.view.monitor_parameters.children = []

    def on_selection(self, change: dict) -> None:
        """docstring"""
        selected = change["new"]
        # self.load_settings(selected)  # TODO load settings for editing
        self.toggle_save_button(selected)

    def toggle_save_button(self, selected: str | None) -> None:
        """docstring"""
        self.view.save.disabled = not selected

    def save_state_to_protocol(self, _=None) -> None:
        """Save selected settings/monitors to selected protocol."""
        protocol = self.view.selector.value
        self.model.save(protocol, self.view.current_state)
        self.view.save_notice.value = f"Saved to {protocol}!"

    def reset(self, _=None) -> None:
        """Reset model and view."""
        self.__reset_widgets()
        self.model.reset(self.view.current_state)

    def refresh(self, _=None):
        """Reset widgets and update protocol selector options."""
        self.reset()
        self.update_selector()

    ###########
    # PRIVATE #
    ###########

    def __reset_widgets(self) -> None:
        """Reset view widgets."""
        self.view.save_notice.value = ""
        for control, value in self.view.defaults.items():
            control.value = value

    def __set_event_listeners(self) -> None:
        """Set event listeners."""
        self.view.save.on_click(self.save_state_to_protocol)
        self.view.on_displayed(self.refresh)
        self.view.reset.on_click(self.reset)
        self.model.observe(self.refresh, "protocols")
        self.view.selector.observe(self.on_selection, "value")
        self.view.is_monitored.observe(self.toggle_monitor_parameters, "value")
