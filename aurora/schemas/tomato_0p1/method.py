# -*- coding: utf-8 -*-

from pydantic import BaseModel, Extra
from typing import Literal, Sequence
from aurora.schemas.cycling import ElectroChemSequence


class Method(BaseModel, extra=Extra.allow):
    device: Literal["MPG2", "worker"]
    technique: str
    # parameter_1
    # parameter_2


def convert_electrochemsequence_to_method_list(elchemsequence: ElectroChemSequence) -> Method:
    """
    Convert an ElectroChemSequence into a list of Method.
    Parameter values that are None will be ignored.
    """

    if not isinstance(elchemsequence, ElectroChemSequence):
        if isinstance(elchemsequence, dict):
            elchemsequence = ElectroChemSequence(**elchemsequence)
        else:
            raise TypeError()
    sequence = []
    for step in elchemsequence.method:
        parameters = {name: param.value for name, param in step.parameters.items() if param.value is not None}
        
        sequence.append(Method(**{
            'device': step.device,
            'technique': step.technique,
            }, **parameters)
        )

    return sequence