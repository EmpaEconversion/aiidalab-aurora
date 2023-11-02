from __future__ import annotations

from aiida_aurora.schemas.cycling import CyclingTechnique, ElectroChemSequence
from traitlets import HasTraits, Integer

from aurora.common.models.backends.backend import Backend
from aurora.common.models.utils import get_valid


class ProtocolsModel(HasTraits):
    """A model used in Aurora to manage available protocols.

    Available protocols are loaded in from the associated backend
    and stored locally as a list of `ElectroChemSequence` instances.

    Attributes
    ----------
    `updated` : `Integer`
        An observable protocols update counter.
    `raw` : `List[dict]`
        The list of validated protocol dictionaries.
    `models` : `List[ElectroChemSequence]`
        The list of validated protocol models.
    """

    updated = Integer(0)

    def __init__(self, backend: Backend | None = None) -> None:
        """`ProtocolModel` constructor.

        Parameters
        ----------
        `backend` : `Backend`
            The model's backend.
        """
        self.__backend = backend
        self.__raw: dict[str, dict] = {}

        if self.__backend:
            self.__backend.init()

    @property
    def raw(self) -> list[dict]:
        """Return a list of validated protocol dictionaries.

        Returns
        -------
        `List[dict]`
            The list of validated protocol dictionaries.
        """
        return list(self.__raw.values())

    @raw.setter
    def raw(self, protocols: list[dict]) -> None:
        """Validate protocols and store as dictionary.

        Parameters
        ----------
        `protocols` : `List[dict]`
            The raw protocols to be validated and stored.
        """
        self.__raw = {
            protocol.name: protocol.dict()
            for protocol in get_valid(protocols, schema=ElectroChemSequence)
        }
        self.updated += 1

    @property
    def models(self) -> dict[str, ElectroChemSequence]:
        """Return the validated protocol models.

        Returns
        -------
        `Dict[str, ElectroChemSequence]`
            A `{name: protocol}` dictionary of validated protocols.
        """
        return {
            protocol.name: protocol
            for protocol in get_valid(self.raw, schema=ElectroChemSequence)
        }

    def set_backend(self, backend: Backend) -> None:
        """Set this model's backend.

        Parameters
        ----------
        `backend` : `Backend`
            The backend to associate with this model.
        """
        self.__backend = backend

    def load(self):
        """Fetch and store new schema-modeled validated protocols."""
        if self.__backend is not None:
            self.raw = self.__backend.fetch()

    def save(self):
        """Persist the current valid protocols in the backend."""
        if self.__backend is not None:
            self.__backend.save(self.raw)

    def get_protocol(self, name: str) -> ElectroChemSequence | None:
        """docstring"""
        return self.models.get(name)

    def update(self, protocol: ElectroChemSequence, save=True) -> None:
        """Update protocol (persisted).

        After persisting, update local cache.

        Parameters
        ----------
        `protocol` : `ElectroChemSequence`
            The updated sample.
        `save` : `Optional[bool]`
            If the samples are to be persisted after operation.
        """
        self.__raw[protocol.name] = protocol.dict()
        self.updated += 1
        if save:
            self.save()

    def add(self, protocol: ElectroChemSequence, save=True) -> None:
        """Add protocol.

        Optionally persist.

        Parameters
        ----------
        `protocol` : `ElectroChemSequence`
            The new protocol.
        `save` : `Optional[bool]`
            If the protocols are to be persisted after operation.
        """
        if protocol.name in self.__raw:
            raise KeyError(f"protocol {protocol.name} already exists.")
        self.update(protocol, save)

    def delete(self, protocol_name: str, save=True) -> None:
        """Delete protocol.

        Optionally persist.

        Parameters
        ----------
        `protocol_name` : `str`
            The name of the protocol to be deleted.
        `save` : `Optional[bool]`
            If the protocols are to be persisted after operation.
        """
        if protocol_name not in self.__raw:
            raise KeyError(f"protocol {protocol_name} does not exist.")
        del self.__raw[protocol_name]
        self.updated += 1
        if save:
            self.save()

    def copy(self, include_backend=False) -> ProtocolsModel:
        """Return a copy of this model.

        Optionally include this model's backend.

        Parameters
        ----------
        `include_backend` : `bool`
            Attache this model's backend to copy if True,
            `False` by default.

        Returns
        -------
        `ProtocolsModel`
            A copy of this model.
        """
        copy = ProtocolsModel()
        copy.sync(self)
        if include_backend and self.__backend:
            copy.set_backend(self.__backend)
        return copy

    def sync(self, other: ProtocolsModel) -> None:
        """Synchronize this model with another.

        Parameters
        ----------
        `other` : `ProtocolsModel`
            Another instance of this class against which to sync.
        """
        self.raw = other.raw

    def query(
        self,
        names: list[str] | None = None,
    ) -> list[ElectroChemSequence]:
        """Return protocols from local cache.

        Optionally filtered by protocol `names`.

        Parameters
        ----------
        `names` : `Optional[List[str]]`
            A list of protocol names, `None` by default.

        Returns
        -------
        `List[ElectroChemSequence]`
            A list of protocols.
        """
        return list(self.models.values()) if names is None \
            else [self.models[name] for name in names]

    def display(self, protocol: CyclingTechnique) -> None:
        """Display details of the `protocol`.

        Parameters
        ----------
        `protocol` : `CyclingTechnique`
            The protocol.
        """
        for step in protocol.method:
            print(f"{step.name} ({step.technique})")
            for label, param in step.parameters:
                default = param.default_value
                value = default if param.value is None else param.value
                units = "" if value is None else param.units
                print(f"{label} = {value} {units}")
            print()

    def as_options(self, protocols: list[ElectroChemSequence]) -> list[str]:
        """Parse protocols list as selection options.

        Parameters
        ----------
        `protocols` : `list[ElectroChemSequence]`
            A list of protocols.

        Returns
        -------
        `list[str]`
            A list of selection options.
        """
        return [protocol.name for protocol in protocols]

    def __contains__(self, name: str) -> bool:
        return name in self.__raw

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ProtocolsModel):
            return NotImplemented
        return self.raw == other.raw
