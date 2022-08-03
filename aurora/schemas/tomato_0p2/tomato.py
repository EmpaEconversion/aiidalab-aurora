# -*- coding: utf-8 -*-

from pydantic import BaseModel, Extra, Field
from typing import Literal

# copied from dgbowl-schemas/src/dgbowl-schemas/tomato/payload_0_2/tomato.py

class Tomato(BaseModel, extra=Extra.forbid):
    class Output(BaseModel, extra=Extra.forbid):
        path: str = None
        prefix: str = None

    class Snapshot(BaseModel, extra=Extra.forbid):
        path: str = None
        prefix: str = None
        frequency: int = 3600

    unlock_when_done: bool = False
    verbosity: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "WARNING"
    output: Output = Field(default_factory=Output)
    snapshot: Snapshot = None