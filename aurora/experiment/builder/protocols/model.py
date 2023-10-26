from __future__ import annotations

from traitlets import HasTraits, Integer, List

from aurora.common.models import ProtocolsModel


class ProtocolSelectorModel(HasTraits):
    """A model for protocol selection.

    Attributes
    ----------
    `updated` : `traitlets.Integer`
        Observable update signal.
    `selected` : `traitlets.List`
        Observable selected protocols register.
    """

    updated = Integer(0)
    selected = List()

    def __init__(self, protocols_model: ProtocolsModel) -> None:
        """`ProtocolSelectorModel` constructor.

        Parameters
        ----------
        `protocols_model` : `ProtocolsModel`
            The global protocols model.
        """
        self.__protocols_model = protocols_model
        self.__protocols_model.observe(self.__signal_update, "updated")

    def select(self, protocols: list[str]) -> None:
        """Add protocols to local register.

        Parameters
        ----------
        `protocols` : `list[str]`
            The names of the selected protocols.
        """
        self.selected = self.selected + [
            protocol for protocol in protocols if protocol not in self.selected
        ]

    def deselect(self, protocols: list[str]) -> None:
        """Remove protocols from local register.

        Parameters
        ----------
        `protocols` : `list[str]`
            The names of the selected protocols.
        """
        self.selected = [
            protocol for protocol in self.selected if protocol not in protocols
        ]

    def get_available(self) -> list[str]:
        """return available protocols as selection options.

        Returns
        -------
        `list[str]`
            A list of `ipw.SelectMultiple` options.
        """
        protocols = self.__protocols_model.query()
        return self.__protocols_model.as_options(protocols)

    def get_selected(self) -> list[str]:
        """Return selected protocol names as selection options.

        Returns
        -------
        `list[str]`
            A list of `ipw.SelectMultiple` options.
        """
        protocols = self.__protocols_model.query(self.selected)
        return self.__protocols_model.as_options(protocols)

    def reset(self) -> None:
        """Reset the selected samples register."""
        self.selected = []

    def display(self, name: str) -> None:
        """Display protocol details.

        Parameters
        ----------
        `name` : `str`
            The name of the selected protocol.
        """
        if protocol := self.__protocols_model.get_protocol(name):
            self.__protocols_model.display(protocol)

    ###########
    # PRIVATE #
    ###########

    def __signal_update(self, _=None) -> None:
        """Signal updated state."""
        self.updated += 1
