# -*- coding: utf-8 -*-

from pydantic import BaseModel, Extra, Field
from typing import Literal


class Tomato(BaseModel, extra=Extra.forbid):
    class Output(BaseModel, extra=Extra.forbid):
        path: str = None
        prefix: str = None

    unlock_when_done: bool = False
    verbosity: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    output: Output = Field(default_factory=Output)
