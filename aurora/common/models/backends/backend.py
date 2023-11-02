from abc import ABC, abstractmethod


class Backend(ABC):
    """An abstraction of backends used in Aurora."""

    @abstractmethod
    def init(self):
        """docstring"""
        raise NotImplementedError()

    @abstractmethod
    def fetch(self):
        """docstring"""
        raise NotImplementedError()

    @abstractmethod
    def save(self, payload: object) -> None:
        """docstring"""
        raise NotImplementedError()
