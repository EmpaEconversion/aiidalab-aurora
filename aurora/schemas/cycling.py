# -*- coding: utf-8 -*-

from pydantic import (BaseModel, Extra, validator, validator, Field, NonNegativeFloat, NonNegativeInt)
from typing import Dict, Generic, Sequence, TypeVar, Literal, Union
from pydantic.generics import GenericModel

DataT = TypeVar('DataT')
class CyclingParameter(GenericModel, Generic[DataT]):
    "Cycling parameter of type DataT"
    label: str  # the label used in a widget
    description: str = ""  # a long description
    units: str = ""  # physical units of this parameter
    value: DataT = None  # the set value
    required: bool = False  # True if parameter is required
    
    class Config:
        validate_assignment = True
        extra = Extra.forbid
    
    # @classmethod
    # def __concrete_name__(cls: Type[Any], params: Tuple[Type[Any], ...]) -> str:
        # return f'{params[0].__name__.title()}CyclingParameter'

class CyclingTechnique(BaseModel):
    technique: str  # the technique name for tomato
    short_name: str  # short name for the technique
    name: str  # a custom name
    description: str = ""
    parameters: Dict[str, CyclingParameter]
    
    class Config:
        validate_assignment = True
        extra = Extra.forbid

allowed_I_ranges = Literal[
    "keep", "100 pA", "1 nA", "10 nA", "100 nA", "1 uA", "10 uA", "100 uA",
    "1 mA", "10 mA", "100 mA", "1 A", "booster", "auto",
]
allowed_E_ranges = Literal[
    "+-2.5 V", "+-5.0 V", "+-10 V", "auto",
]

class OpenCircuitVoltage(CyclingTechnique, extra=Extra.forbid):
    technique: Literal["open_circuit_voltage"] = "open_circuit_voltage"
    short_name: Literal["OCV"] = "OCV"
    name = "OCV"
    description = "Open circuit voltage"
    parameters: Dict[str, CyclingParameter] = {
        "time": CyclingParameter[NonNegativeFloat](
            label = "Time:",
            description = "The length of the OCV step",
            units = "s",
            value = 0.0,
            required = True,
        ),
        "record_every_dt": CyclingParameter[NonNegativeFloat](
            label = "Record every $dt$:",
            description = "Record a datapoint at prescribed time spacing",
            units = "s",
            value = 30.0
        ),
        "record_every_dE": CyclingParameter[NonNegativeFloat](
            label = "Record every $dE$:",
            description = "Record a datapoint at prescribed voltage spacing",
            units = "V",
            value = 0.005
        ),
        "I_range": CyclingParameter[allowed_I_ranges](
            label = "I range",
            description = "",
            value = "keep"
        ),
        "E_range": CyclingParameter[allowed_E_ranges](
            label = "E range",
            description = "",
            value = "auto"
        ),
    }

class ConstantVoltage(CyclingTechnique, extra=Extra.forbid):
    technique: Literal["constant_voltage"] = "constant_voltage"
    short_name: Literal["CV"] = "CV"
    name = "CV"
    description = "Controlled voltage technique, with optional current and voltage limits"
    parameters: Dict[str, CyclingParameter] = {
        "time": CyclingParameter[NonNegativeFloat](
            label = "Time:",
            description = "Maximum duration of the CV step",
            units = "s",
            value = 0.0,
            required = True,
        ),
        "voltage": CyclingParameter[float](
            label = "Step voltage:",
            description = "Voltage of the current step",
            units = "V",
            value = 0.0,
            required = True,
        ),
        "record_every_dt": CyclingParameter[NonNegativeFloat](
            label = "Record every $dt$:",
            description = "Record a datapoint at prescribed time spacing",
            units = "s",
            value = 30.0
        ),
        "record_every_dI": CyclingParameter[NonNegativeFloat](
            label = "Record every $dI$:",
            description = "Record a datapoint at prescribed current spacing",
            units = "I",
            value = 0.001
        ),
        "I_range": CyclingParameter[allowed_I_ranges](
            label = "I range",
            description = "Select the current range of the potentiostat",
            value = "keep"
        ),
        "E_range": CyclingParameter[allowed_E_ranges](
            label = "E range",
            description = "Select the voltage range of the potentiostat",
            value = "auto"
        ),
        "n_cycles": CyclingParameter[NonNegativeInt](
            label = "Number of cycles:",
            description = "Cycle through the current technique N times.",
            value = 0,
        ),
        "is_delta": CyclingParameter[bool](
            label = "$\delta V$:",
            description = "Is the step voltage a $\delta$ from previous step?",
            value = False
        ),
        "exit_on_limit": CyclingParameter[bool](
            label = "Exit when limits reached?",
            description = "Stop the whole experiment when limit is reached?",
            value = False
        ),
        "limit_voltage_max": CyclingParameter[float](
            label = "Maximum voltage:",
            description = "Define the upper limit of voltage for this step",
            value = None
        ),
        "limit_voltage_min": CyclingParameter[float](
            label = "Minimum voltage:",
            description = "Define the lower limit of voltage for this step",
            value = None
        ),
        "limit_current_max": CyclingParameter[Union[float, str]](
            label = "Maximum current:",
            description = "Define the upper limit of current for this step",
            value = None
        ),
        "limit_current_min": CyclingParameter[Union[float, str]](
            label = "Minimum current:",
            description = "Define the lower limit of current for this step",
            value = None
        )
    }

class ConstantCurrent(CyclingTechnique, extra=Extra.forbid):
    technique: Literal["constant_current"] = "constant_current"
    short_name: Literal["CC"] = "CC"
    name = "CC"
    description = "Controlled current technique, with optional voltage and current limits"
    parameters: Dict[str, CyclingParameter] = {
        "time": CyclingParameter[NonNegativeFloat](
            label = "Time:",
            description = "Maximum duration of the CC step",
            units = "s",
            value = 0.0,
            required = True,
        ),
        "current": CyclingParameter[Union[float, str]](
            label = "Step current:",
            description = "Current during the current step",
            units = "I",
            value = 0.0,
            required = True,
        ),
        "record_every_dt": CyclingParameter[NonNegativeFloat](
            label = "Record every $dt$:",
            description = "Record a datapoint at prescribed time spacing",
            units = "s",
            value = 30.0
        ),
        "record_every_dE": CyclingParameter[NonNegativeFloat](
            label = "Record every $dE$:",
            description = "Record a datapoint at prescribed voltage spacing",
            units = "V",
            value = 0.001
        ),
        "I_range": CyclingParameter[allowed_I_ranges](
            label = "I range",
            description = "Select the current range of the potentiostat",
            value = "keep"
        ),
        "E_range": CyclingParameter[allowed_E_ranges](
            label = "E range",
            description = "Select the voltage range of the potentiostat",
            value = "auto"
        ),
        "n_cycles": CyclingParameter[NonNegativeInt](
            label = "Number of cycles:",
            description = "Cycle through the current technique N times.",
            value = 0,
        ),
        "is_delta": CyclingParameter[bool](
            label = "$\delta I$:",
            description = "Is the step current a $\delta$ from previous step?",
            value = False
        ),
        "exit_on_limit": CyclingParameter[bool](
            label = "Exit when limits reached?",
            description = "Stop the whole experiment when limit is reached?",
            value = False
        ),
        "limit_voltage_max": CyclingParameter[float](
            label = "Maximum voltage:",
            description = "Define the upper limit of voltage for this step",
            value = None
        ),
        "limit_voltage_min": CyclingParameter[float](
            label = "Minimum voltage:",
            description = "Define the lower limit of voltage for this step",
            value = None
        ),
        "limit_current_max": CyclingParameter[Union[float, str]](
            label = "Maximum current:",
            description = "Define the upper limit of current for this step",
            value = None
        ),
        "limit_current_min": CyclingParameter[Union[float, str]](
            label = "Minimum current:",
            description = "Define the lower limit of current for this step",
            value = None
        )
    }

#class SweepVoltage(CyclingTechnique, extra=Extra.forbid):
#    technique: Literal["sweep_voltage"] = "sweep_voltage"
#    short_name: Literal["LSV"] = "LSV"
#    name = "LSV"
#    description = "Controlled voltage technique, allowing linear change of voltage between pre-defined endpoints as a function of time, with optional current and voltage limits"

#class SweepCurrent(CyclingTechnique, extra=Extra.forbid):
#    technique: Literal["sweep_current"] = "sweep_current"
#    short_name: Literal["LSC"] = "LSC"
#    name = ""
#    description = "Controlled current technique, allowing linear change of current between pre-defined endpoints as a function of time, with optional current and voltage limits"

class Loop(CyclingTechnique, extra=Extra.forbid):
    technique: Literal["loop"] = "loop"
    short_name: Literal["LOOP"] = "LOOP"
    name = "LOOP"
    description = "Loop technique, allowing to repeat a set of preceding techniques in a technique array"
    parameters: Dict[str, CyclingParameter] = {
        "n_gotos": CyclingParameter[int](
            label = "Repeats",
            description = "Number of times the technique will jump; set to -1 for unlimited",
            value = -1,
            required = True,
        ),
        "goto": CyclingParameter[int](
            label = "Go to:",
            description = "Index of the technique to go back to",
            value = 0,
            required = True,
        ),
    }

ElectroChemPayloads = Union[
    OpenCircuitVoltage,
    ConstantCurrent,
    ConstantVoltage,
#    SweepCurrent,
#    SweepVoltage,
    Loop,
]

class ElectroChemSequence(BaseModel):
    sequence: Sequence[ElectroChemPayloads]
    
    @property
    def n_steps(self):
        "Number of steps of the sequence"
        return len(self.sequence)

    def add_step(self, elem):
        if not isinstance(elem, ElectroChemPayloads.__args__):
            raise ValueError("Invalid technique")
        self.sequence.append(elem)
    
    def remove_step(self, index):
        self.sequence.pop(index)
    
    def move_step_backward(self, index):
        if index > 0:
            self.sequence[index-1], self.sequence[index] = self.sequence[index], self.sequence[index-1]

    def move_step_forward(self, index):
        if index < self.n_steps - 1:
            self.sequence[index], self.sequence[index+1] = self.sequence[index+1], self.sequence[index]
        
    class Config:
        validate_assignment = True
        extra = Extra.forbid