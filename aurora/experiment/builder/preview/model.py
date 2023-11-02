from __future__ import annotations

from traitlets import Bool, Dict, HasTraits, List, Set

from aurora.common.models import ProtocolsModel, SamplesModel


class InputPreviewModel(HasTraits):
    """docstring"""

    samples = Set()
    protocols = List()
    settings = Dict()

    valid_input = Bool(False)

    def __init__(
        self,
        samples_model: SamplesModel,
        protocols_model: ProtocolsModel,
    ) -> None:
        """`InputPreviewModel` constructor.

        Parameters
        ----------
        `samples_model` : `SamplesModel`
            The global samples model.
        `protocols_model` : `ProtocolsModel`
            The global protocols model.
        """
        self.__samples_model = samples_model
        self.__protocols_model = protocols_model

    def preview_samples(self) -> None:
        """docstring"""
        query = {"id": list(self.samples)}
        samples = self.__samples_model.query(query)
        self.__samples_model.display(samples)

    def preview_protocol(self, name: str) -> None:
        """docstring"""
        protocol = self.__protocols_model.get_protocol(name)
        self.__protocols_model.display(protocol)

    def preview_settings(self, protocol: str) -> None:
        """docstring"""
        settings = self.settings[protocol]["settings"]
        for key, value in settings.items():
            if isinstance(value, dict):
                for k, v in value.items():
                    print(f"{k}: {v}")
            else:
                print(f"{key}: {value}")

    def preview_monitors(self, protocol: str) -> None:
        """docstring"""
        monitors = self.settings[protocol]["monitors"]
        for monitor, monitor_settings in monitors.items():
            print(f"name: {monitor}")
            for key, value in monitor_settings.items():
                print(f"{key} = {value}")
        print()
