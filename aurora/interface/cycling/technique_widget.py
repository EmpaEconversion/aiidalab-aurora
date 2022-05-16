# -*- coding: utf-8 -*-

import ipywidgets as ipw
from aurora.schemas.cycling import ElectroChemPayloads, CyclingParameter
import typing
from pydantic.types import NonNegativeInt, NonNegativeFloat

## NOTE: requirement of parameters is not enforced when assigning

def build_parameter_widget(param_obj):
    if not isinstance(param_obj, CyclingParameter):
        raise TypeError(f"param_obj should be a CyclingParameter instance, not {type(param_obj)}")

    value_type = param_obj.__annotations__['value']
    param_value = param_obj.value
    if isinstance(value_type, typing._LiteralGenericAlias):  # a string Literal
        w_param = ipw.Dropdown(
            description=param_obj.label, placeholder=param_obj.description,
            options=value_type.__args__, value=param_value)
            # layout=***, style=***)
    elif issubclass(value_type, float):
        if value_type in [NonNegativeFloat]:
            value_min, value_max = (0., 1.e99)
        else:
            value_min, value_max = (-1.e99, 1.e99)
        w_param = ipw.BoundedFloatText(
            description=param_obj.label, min=value_min, max=value_max, #step=param_dic.get('step'),
            value=param_value, style={'description_width': 'initial'})
    elif issubclass(value_type, int):
        if value_type in [NonNegativeInt]:
            value_min, value_max = (0, 1e99)
        else:
            value_min, value_max = (-1e99, 1e99)
        w_param = ipw.BoundedIntText(
            description=param_obj.label, min=value_min, max=value_max, #step=param_dic.get('step'),
            value=param_value, style={'description_width': 'initial'})
    elif issubclass(value_type, str):
        w_param = ipw.Text(
            description=param_obj.label, placeholder='',
            value=param_value, style={'description_width': 'initial'})
    else:
        raise NotImplementedError()
    
    w_units = ipw.HTML(param_obj.units + f"  (<i>{param_obj.description}</i>)" if param_obj.description else "")

    return ipw.HBox([w_param, w_units])

class TechniqueParametersWidget(ipw.VBox):
    
    BUTTON_STYLE = {'description_width': '30%'}
    BUTTON_LAYOUT_2 = {'width': '8%', 'margin': '5px'}
        
    def __init__(self, technique, **kwargs):
        # technique is an instance of one of the classes in ElecElectroChemPayloads
        if not isinstance(technique, ElectroChemPayloads.__args__):
            raise ValueError("Invalid technique")
        
        self.tech_short_name = technique.short_name
        self.tech_description = technique.description
        
        self.w_name = ipw.Text(description="Step label:", placeholder="Enter a custom name", value=technique.name)
            # layout=self.BOX_LAYOUT, style=self.BOX_STYLE)
        self.w_tech_label = ipw.HTML(f"<b>Technique:</b> <i>{self.tech_description}</i>")
        self.tech_parameters_names = []
        w_parameters_children = []
        for pname, pobj in technique.parameters.items():  # loop over parameters
            self.tech_parameters_names.append(pname)
            w_parameters_children.append(build_parameter_widget(pobj))
        self.w_tech_parameters = ipw.VBox(w_parameters_children)
        
        super().__init__(**kwargs)
        self.children = [
            self.w_name,
            self.w_tech_label,
            self.w_tech_parameters,
        ]
    
    @property
    def tech_name(self):
        return self.w_name.value

    @property
    def tech_parameters_values(self):
        return [w.children[0].value for w in self.w_tech_parameters.children]
        
    @property
    def selected_tech_parameters(self):
        return {pname: pvalue for pname, pvalue in zip(self.tech_parameters_names, self.tech_parameters_values) if pvalue}