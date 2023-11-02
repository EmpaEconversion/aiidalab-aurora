from __future__ import annotations

from datetime import datetime

from aurora.time import TZ

from .model import ExperimentModel
from .view import ExperimentView


class ExperimentController:
    """
    docstring
    """

    def __init__(
        self,
        view: ExperimentView,
        model: ExperimentModel,
    ) -> None:
        """`ExperimentController` constructor.

        Parameters
        ----------
        `view` : `ExperimentView`
            The associated view.
        `model` : `ExperimentModel`
            The associated model.
        """
        self.view = view
        self.model = model
        self.__set_event_listeners()

    def get_codes(self, _=None) -> None:
        """docstring"""
        self.view.code.options = self.model.get_codes()

    def on_valid_input(self, change: dict) -> None:
        """docstring"""
        self.view.submit.disabled = not change["new"]

    def submit(self, _=None) -> None:
        """docstring"""

        default_label = datetime.now(TZ).strftime(r"%y%m%d-%H%M%S")
        group_label = self.view.experiment_group_label.value or default_label

        with self.view.submission_output:
            self.model.submit(
                code_name=self.view.code.value,
                unlock_when_done=self.view.unlock_when_done.value,
                group_label=group_label,
            )

        self.view.builder.selected_index = None

    def reset(self, _=None):
        "Reset view widgets."
        self.view.submission_output.clear_output()
        self.view.builder.selected_index = None
        self.view.unlock_when_done.value = False
        self.view.experiment_group_label.value = ""
        self.model.builder.valid_input = False
        self.__reset_sections()

    ###########
    # PRIVATE #
    ###########

    def __reset_sections(self) -> None:
        """docstring"""
        for section in self.view.builder.sections:
            section.reset.click()

    def __set_event_listeners(self) -> None:
        """Set event listeners."""
        self.view.on_displayed(self.get_codes)
        self.view.submit.on_click(self.submit)
        self.view.reset.on_click(self.reset)
        self.model.builder.observe(self.on_valid_input, "valid_input")
