
from typing import TypedDict, Union, Optional
from datetime import datetime
from pydantic import BaseModel, validator, root_validator
from numpy import datetime64

class BatteryComposition(BaseModel):  # TypedDict?
    description: str = None
    cathode: str = None
    anode: str = None
    electrolyte: str = None
    
    class Config:
        # exclude fields from export, to avoid validation errors when reloaded
        fields = {
            'cathode': {'exclude': True},
            'anode': {'exclude': True},
            'electrolyte': {'exclude': True},
        }

    @root_validator
    def validate_composition(cls, values):
        """
        Check that components are not specified if 'description' is specified
        then build components from a 'description' string, or vice versa.
        # TODO: what to do if 'description' is not in the C|E|A format?
        """
        if values['description']:
            if any([values[key] for key in ('cathode', 'anode', 'electrolyte')]):
                raise ValueError("You cannot specify a 'description' and any component at the same time.")
            values['description'] = values['description'].strip()
            components = list(map(str.strip, values['description'].split('|')))
            if len(components) == 3:
                values['cathode'], values['electrolyte'], values['anode'] = components
            else:
                values['cathode'], values['electrolyte'], values['anode'] = (None, None, None)
                # raise ValueError(
                    # "Composition 'description' does not have 3 components (i.e. {cathode}|{electrolyte}|{anode}).")
        elif any([values[key] for key in ('cathode', 'anode', 'electrolyte')]):
            for key in ('cathode', 'anode', 'electrolyte'):
                values[key] = values[key].strip()
            values['description'] = f"{values['cathode']}|{values['electrolyte']}|{values['anode']}"
        else:
            raise ValueError("You must specify either a string 'description' or the components.")
        return values
    
class BatteryCapacity(BaseModel): # TypedDict?
    nominal: float
    actual: Optional[float]
    units: str
    # TODO: Possibility of entering a string e.g. '1.00 mAh'

class BatteryMetadata(BaseModel):
    creation_datetime: datetime
    creation_process: str
    
class BatterySpecs(BaseModel):
    """
    Battery specification schema.
    """
    manufacturer: str
    composition: BatteryComposition
    form_factor: str
    capacity: BatteryCapacity
    metadata: BatteryMetadata
    
    # should we add a validator?
    # to check that e.g. manufacturer is one of the available ones
    # ...
    
    # add pre-validator to allow capacity: str (e.g. '4.8 mAh')

class BatterySample(BatterySpecs):
    """
    Battery sample schema.
    """
    battery_id: int
    name: str = None

# data types imposed when reading the JSON of available specs/samples
# TODO: write a function that generates this dict automatically from the pydantic schema
BatterySpecsJsonTypes = {
    'manufacturer': str,
    'form_factor': str,
    'composition.description': str,
    'capacity.nominal': float,
    'capacity.actual': float,
    'capacity.units': str,
    'metadata.creation_datetime': str, #datetime64,
    'metadata.creation_process': str
}
BatterySampleJsonTypes = {
    'manufacturer': str,
    'form_factor': str,
    'battery_id': int,
    'name': str,
    'composition.description': str,
    'capacity.nominal': float,
    'capacity.actual': float,
    'capacity.units': str,
    'metadata.creation_datetime': str, #datetime64,
    'metadata.creation_process': str
}