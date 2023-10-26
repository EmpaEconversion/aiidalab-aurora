from __future__ import annotations

from .model import SampleSelectorModel
from .view import SampleSelectorView


class SampleSelectorController:
    """A controller class for sample selection.

    Attributes
    ----------
    `view` : `SampleSelectorView`
        The associated view.
    `model` : `SampleSelectorModel`
        The associated model.
    """

    def __init__(
        self,
        view: SampleSelectorView,
        model: SampleSelectorModel,
    ) -> None:
        """`SampleSelectorController` constructor.

        Parameters
        ----------
        `view` : `SampleSelectorView`
            The associated view.
        `model` : `SampleSelectorModel`
            The associated model.
        """
        self.view = view
        self.model = model
        self.__set_event_listeners()

    def update_selector(self, _=None) -> None:
        """Update selector options."""
        filters = self.view.filters.current_state
        self.view.selector.options = self.model.get_available(filters)

    def update_selected(self, _=None) -> None:
        """Update selected options."""
        self.view.selected.options = self.model.get_selected()

    def select_samples(self, _=None) -> None:
        """Add selected samples to model."""
        self.model.select(self.view.selector.value)

    def select_all_samples(self, _=None) -> None:
        """Add all samples to model."""
        self.model.select(get_ids(self.view.selector.options))

    def deselect_samples(self, _=None) -> None:
        """Remove selected samples from model."""
        self.model.deselect(self.view.selected.value)

    def deselect_all_samples(self, _=None) -> None:
        """Remove all samples from model."""
        self.model.deselect(get_ids(self.view.selected.options))

    def reset(self, _=None) -> None:
        """Reset model and view."""
        self.view.filters.selected_index = None
        self.view.selector.value = []
        self.view.filters.reset()
        self.model.reset()

    def refresh(self, _=None):
        """Update spec and sample options."""
        self.view.filters.update()
        self.deselect_all_samples()
        self.update_selector()

    ###########
    # PRIVATE #
    ###########

    def __set_event_listeners(self) -> None:
        """Set event listeners."""
        self.view.on_displayed(self.refresh)
        self.view.select.on_click(self.select_samples)
        self.view.select_all.on_click(self.select_all_samples)
        self.view.deselect.on_click(self.deselect_samples)
        self.view.deselect_all.on_click(self.deselect_all_samples)
        self.view.reset.on_click(self.reset)
        self.view.filters.observe(self.refresh, "changed")
        self.model.observe(self.update_selected, "selected")
        self.model.observe(self.refresh, "updated")


def get_ids(options: tuple[tuple[str, int], ...]) -> tuple[int, ...]:
    """Extract indices from option tuples.

    Parameters
    ----------
    options : `tuple[tuple[str, int], ...]`
        A tuple of `ipywidgets.SelectMultiple` option tuples.

    Returns
    -------
    `tuple[int, ...]`
        A tuple of option indices.
    """
    return tuple(i for _, i in options)
