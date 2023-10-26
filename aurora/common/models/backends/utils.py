from __future__ import annotations

import json
import pickle
from datetime import datetime
from typing import Any


def as_python_object(dictionary: dict) -> dict | object:
    """Cast `value` of `{"type": value}` dictionary as Python `type`.

    Parameters
    ----------
    `dictionary` : `dict`
        A `{"type": value}` dictionary.

    Returns
    -------
    `dict | object`
        Return decoded Python object if it was not JSON-serializable,
        the serialized dictionary otherwise.
    """
    if "set" in dictionary:
        return set(dictionary["set"])
    if "datetime" in dictionary:
        return datetime.strptime(dictionary["datetime"], r"%Y-%m-%d %H:%M:%S")
    if "_python_object" in dictionary:
        return pickle.loads(dictionary["_python_object"].encode("latin-1"))
    return dictionary


class PyObjEncoder(json.JSONEncoder):
    """A JSONEncoder extension for handling Python objects."""

    def default(self, obj: object) -> dict | Any:
        """Encode Python objects into JSON-serializable objects.

        Parameters
        ----------
        `obj` : `object`
            A Python object.

        Returns
        -------
        `dict | Any`
            A `{"type": value}` dictionary if not JSON-serializable,
            `Any` otherwise.
        """
        if isinstance(obj, set):
            return {"set": list(obj)}
        if isinstance(obj, datetime):
            return {"datetime": str(obj)}
        try:
            return {"_python_object": pickle.dumps(obj).decode("latin-1")}
        except pickle.PickleError:
            return super().default(obj)
