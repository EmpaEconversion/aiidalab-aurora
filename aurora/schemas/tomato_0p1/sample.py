# -*- coding: utf-8 -*-

from pydantic import BaseModel, Extra, PositiveFloat
from aurora.schemas.data_schemas import BatterySample


class Sample(BaseModel, extra=Extra.ignore):
    name: str
    capacity: PositiveFloat  # [Ah]


def convert_batterysample_to_sample(batsample: BatterySample) -> Sample:
    "Convert a BatterySample into a Sample"""

    if not isinstance(batsample, BatterySample):
        if isinstance(batsample, dict):
            batsample = BatterySample(**batsample)
        else:
            raise TypeError()
    if batsample.capacity.units == "mAh":
        capacity = float(batsample.capacity.nominal) * 0.001
    elif batsample.capacity.units == "Ah":
        capacity = float(batsample.capacity.nominal)

    sample = Sample(
        name = batsample.metadata.name,
        capacity =  capacity
    )
    return sample