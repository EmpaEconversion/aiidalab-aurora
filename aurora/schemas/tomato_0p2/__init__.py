# -*- coding: utf-8 -*-

from .sample import Sample
from .method import Method
from .tomato import Tomato

from pydantic import BaseModel, Extra, Field
from typing import Sequence, Literal
from aurora.schemas.convert import remove_empties_from_dict_decorator


class TomatoPayload(BaseModel, extra=Extra.forbid):
    version: Literal["0.2"]
    tomato: Tomato = Field(default_factory=Tomato)
    sample: Sample
    method: Sequence[Method]

    # this decorator remove 'None' values
    @remove_empties_from_dict_decorator
    def dict(self):
        return super().dict()