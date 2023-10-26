import json
from pathlib import Path

from .backend import Backend
from .utils import PyObjEncoder, as_python_object


class JSONBackend(Backend):
    """
    A JSON backend.

    Attributes
    ----------
    `filename` : str
        The associated JSON filename.
    """

    def __init__(self, data_dir: str, filename: str) -> None:
        """Initialize the backend with the JSON filename.

        Parameters
        ----------
        `filename` : `str`
            The JSON filename to associate with this instance.
        """
        self.path = f"{data_dir}/{filename}"

    def init(self):
        """docstring"""
        if not Path(self.path).exists():
            with open(self.path, "w+") as handle:
                handle.write("[]")

    def fetch(self):
        """Return the contents of the associated JSON file.

        Returns
        -------
        `JsonType`
            The contents of the associated JSON file as a
            JSON object or list of JSON objects.
        """
        try:
            with open(self.path) as handle:
                return json.load(handle, object_hook=as_python_object)
        except Exception as err:
            print(err)  # TODO log, don't print
            return []

    def save(self, payload: object) -> None:
        """Override the associated JSON file with the payload.

        Parameters
        ----------
        `payload` : `object`
            A JSON serializable data object.
        """
        try:
            with open(self.path, "w+") as handle:
                json.dump(payload, handle, cls=PyObjEncoder)
        except Exception as err:
            print(err)  # TODO log, don't print
