from __future__ import annotations

from .model import ProtocolSelectorModel
from .view import ProtocolSelectorView


class ProtocolSelectorController:
    """docstring"""

    def __init__(
        self,
        view: ProtocolSelectorView,
        model: ProtocolSelectorModel,
    ) -> None:
        """docstring"""
        self.view = view
        self.model = model
        self.__set_event_listeners()

    def update_selector(self, _=None) -> None:
        """Update selector options."""
        self.view.selector.options = self.model.get_available()

    def update_selected(self, _=None) -> None:
        """Update selected options."""
        self.view.selected.options = self.model.get_selected()

    def select_protocols(self, _=None) -> None:
        """Add selected protocols to model."""
        self.model.select([self.view.selector.value])

    def select_all_protocols(self, _=None) -> None:
        """Add all protocols to model."""
        self.model.select(list(self.view.selector.options))

    def deselect_protocols(self, _=None) -> None:
        """Remove selected protocols from model."""
        self.model.deselect([self.view.selected.value])

    def deselect_all_protocols(self, _=None) -> None:
        """Remove all protocols from model."""
        self.model.deselect(list(self.view.selector.options))

    def reset(self, _=None) -> None:
        """Reset model and view."""
        self.view.selector.value = None
        self.model.reset()

    def refresh(self, _=None):
        """Update protocol options."""
        self.deselect_all_protocols()
        self.update_selector()

    def show_preview(self, change: dict) -> None:
        """docstring"""
        self.view.preview.clear_output()
        with self.view.preview:
            self.model.display(change["new"])

    ###########
    # PRIVATE #
    ###########

    def __set_event_listeners(self) -> None:
        """docstring"""
        self.view.on_displayed(self.refresh)
        self.view.select.on_click(self.select_protocols)
        self.view.select_all.on_click(self.select_all_protocols)
        self.view.deselect.on_click(self.deselect_protocols)
        self.view.deselect_all.on_click(self.deselect_all_protocols)
        self.view.reset.on_click(self.reset)
        self.view.selector.observe(self.show_preview, "value")
        self.model.observe(self.update_selected, "selected")
        self.model.observe(self.refresh, "updated")
