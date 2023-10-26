from __future__ import annotations

from copy import deepcopy

from traitlets import Dict, HasTraits, Integer, List


class SettingsSelectorModel(HasTraits):
    """A model for sample selection.

    Attributes
    ----------
    `updated` : `traitlets.Integer`
        Observable update signal.
    `selected` : `traitlets.Dict`
        Observable selected samples register.
    """

    updated = Integer(0)
    selected = Dict()
    protocols = List()

    def get_selected_protocols(self) -> list[str]:
        """Return selected protocol names.

        Returns
        -------
        `list[str]`
            The names of the selected protocols.
        """
        return self.selected.keys()

    def get_settings(self, protocol: str) -> dict:
        """Return protocol settings.

        Parameters
        ----------
        `protocol` : `str`
            The name of the protocol.

        Returns
        -------
        `dict`
            The associated settings dictionary.
        """
        return self.selected.get(protocol)

    def save(self, protocol: str, settings: dict) -> None:
        """Save selected settings to protocol.

        Parameters
        ----------
        `protocol` : `str`
            The name of the protocol.
        `settings` : `dict`
            The selected settings.
        """
        copy = deepcopy(self.selected)
        copy.update({protocol: settings})
        self.selected = copy

    def reset(self, defaults: dict) -> None:
        """Reset the selected settings register.

        Parameters
        ----------
        `defaults` : `dict`
            The default settings.
        """
        self.selected = {protocol: defaults for protocol in self.protocols}
