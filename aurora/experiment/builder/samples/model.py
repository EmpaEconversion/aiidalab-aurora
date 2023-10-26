from __future__ import annotations

from typing import Union

from traitlets import HasTraits, Integer, Set

from aurora.common.models import SamplesModel

SetType = Union[Set, set]


class SampleSelectorModel(HasTraits):
    """A model for sample selection.

    Attributes
    ----------
    `updated` : `traitlets.Integer`
        Observable update signal.
    `selected` : `traitlets.Set`
        Observable selected samples register.
    """

    updated = Integer(0)
    selected: SetType = Set()

    def __init__(self, samples_model: SamplesModel) -> None:
        """`SampleSelectorModel` constructor.

        Parameters
        ----------
        `samples_model` : `SamplesModel`
            The global samples model.
        """
        self.__samples_model = samples_model
        self.__samples_model.observe(self.__signal_update, "updated")

    def select(self, ids: tuple[int, ...]) -> None:
        """Add sample ids to local register.

        Parameters
        ----------
        `ids` : `tuple[int, ...]`
            A tuple of sample ids.
        """
        self.selected = self.selected | set(ids)

    def deselect(self, ids: tuple[int, ...]) -> None:
        """Remove sample ids from local register.

        Parameters
        ----------
        `ids` : `tuple[int, ...]`
            A tuple of sample ids.
        """
        self.selected = self.selected - set(ids)

    def get_available(self, filters: dict) -> list[tuple[str, int]]:
        """return available samples as selection options.

        Available samples are filtered by the current state of the
        associated filters widget

        Parameters
        ----------
        `filters` : `dict`
            Current state of the associated filters widget.

        Returns
        -------
        `list[tuple[str, int]]`
            A list of `ipw.SelectMultiple` options.
        """
        samples = self.__samples_model.query(filters)
        return self.__samples_model.as_options(samples)

    def get_selected(self) -> list[tuple[str, int]]:
        """Return selected sample ids as selection options.

        Returns
        -------
        `list[tuple[str, int]]`
            A list of `ipw.SelectMultiple` options.
        """
        samples = self.__samples_model.query({"id": list(self.selected)})
        return self.__samples_model.as_options(samples)

    def reset(self) -> None:
        """Reset the selected samples register."""
        self.selected = set()

    ###########
    # PRIVATE #
    ###########

    def __signal_update(self, _=None) -> None:
        """Signal updated state."""
        self.updated += 1
