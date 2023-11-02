from __future__ import annotations

from aiida_aurora.schemas.battery import BatterySample
from aiida_aurora.schemas.cycling import ElectroChemSequence
from traitlets import Bool, Dict, HasTraits, Integer, List, Set

from aurora.common.models import ProtocolsModel, SamplesModel


class ExperimentBuilderModel(HasTraits):
    """
    This model holds currently selected samples, protocols,
    and instrument settings.
    """

    samples = Set()
    protocols = List()
    settings = Dict()

    generate_preview = Integer(0)
    valid_input = Bool(False)

    def __init__(
        self,
        samples_model: SamplesModel,
        protocols_model: ProtocolsModel,
    ) -> None:
        """`ExperimentBuilderModel` constructor.

        Parameters
        ----------
        `samples_model` : `SamplesModel`
            The global samples model.
        `protocols_model` : `ProtocolsModel`
            The global protocols model.
        """
        self.__samples_model = samples_model
        self.__protocols_model = protocols_model

    def signal_preview(self) -> None:
        """docstring"""
        self.generate_preview += 1

    def get_samples(self) -> list[BatterySample]:
        """docstring"""
        return [self.__samples_model.models[id] for id in sorted(self.samples)]

    def get_protocols(self) -> list[ElectroChemSequence]:
        """docstring"""
        return self.__protocols_model.query(self.protocols)

    def get_settings(self, protocol: str) -> dict:
        """docstring"""
        return self.settings[protocol]["settings"]

    def get_monitors(self, protocol: str) -> dict[str, dict]:
        """docstring"""
        return self.settings[protocol]["monitors"]
