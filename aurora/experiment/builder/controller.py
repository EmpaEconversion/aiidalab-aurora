from __future__ import annotations

from .model import ExperimentBuilderModel
from .view import ExperimentBuilderView


class ExperimentBuilderController:
    """A wrapper of the Experiment MVC module."""

    def __init__(
        self,
        view: ExperimentBuilderView,
        model: ExperimentBuilderModel,
    ) -> None:
        """docstring"""
        self.view = view
        self.model = model
        self.__set_event_listeners()

    def on_selected_index_change(self, change: dict) -> None:
        """docstring"""
        if change["new"] == 3:
            self.model.signal_preview()

    ###########
    # PRIVATE #
    ###########

    def __set_event_listeners(self) -> None:
        """Set event listeners."""
        self.view.observe(self.on_selected_index_change, "selected_index")
