import typing as t

import ipywidgets as ipw
from aiida_aurora.schemas.cycling import CyclingParameter, CyclingTechnique
from pydantic.types import NonNegativeFloat, NonNegativeInt

CHECKBOX_STYLE = {
    "description_width": "5px",
}

CHECKBOX_LAYOUT = {
    "width": "8%",
    "margin": "6px 2px 0px",
}

BOX_LAYOUT = {
    "width": "300px",
}

BOX_STYLE = {
    "description_width": "150px",
}

MAIN_LAYOUT = {
    "flex": "1",
    "width": "auto",
    "padding": "5px",
    "margin": "10px",
}


class TechniqueParametersWidget(ipw.VBox):

    def __init__(self, technique: CyclingTechnique):
        if not isinstance(technique, CyclingTechnique):
            raise ValueError("Invalid technique")

        self.label = ipw.Text(
            layout=BOX_LAYOUT,
            style=BOX_STYLE,
            description="Label:",
            placeholder="Enter a custom name",
            value=technique.name,
        )

        device_options = t.get_args(
            technique.model_fields["device"].annotation)

        self.device = ipw.Dropdown(
            layout=BOX_LAYOUT,
            style=BOX_STYLE,
            description="Device:",
            options=device_options,
            value=device_options[0],
        )

        self.description = ipw.HTML(
            layout={"margin": "10px 0"},
            value=f"<b>Technique:</b> <i>{technique.description}</i>",
        )

        self.tech_parameters_names = []

        param_children = []
        for name, param in technique.parameters.items():
            self.tech_parameters_names.append(name)
            param_children.append(build_parameter_widget(param))

        self.parameters = ipw.VBox(
            layout={"width": "max-content"},
            children=param_children,
        )

        super().__init__(
            layout=MAIN_LAYOUT,
            children=[
                self.label,
                self.device,
                self.description,
                self.parameters,
            ],
        )

    @property
    def tech_name(self):
        return self.label.value

    @property
    def parameter_values(self):
        """Return list of parameters values.

        If a parameter is disabled, its value will be None.
        """
        return [(child.children[0].value if child.children[1].value else None)
                for child in self.parameters.children]

    @property
    def selected_parameters(self):
        return {
            name: value
            for name, value in zip(
                self.tech_parameters_names,
                self.parameter_values,
            ) if value is not None
        }


def build_parameter_widget(param: CyclingParameter) -> ipw.HBox:
    """docstring"""

    if not isinstance(param, CyclingParameter):
        raise TypeError(
            f"`param` should be a CyclingParameter instance, not {type(param)}"
        )

    w_check = ipw.Checkbox(
        value=param.required or (param.value is not None),
        disabled=param.required,
        description="",
        style=CHECKBOX_STYLE,
        layout=CHECKBOX_LAYOUT,
    )

    param_value = param.default_value if param.value is None else param.value
    annotation = param.model_fields["value"].annotation

    # since 'value' is `Optional`, all values are unions of their
    # actual type and `NoneType`. Here we discard `NoneType`.
    types = t.get_args(annotation)[:-1]

    if len(types) > 1:
        # Optional[Union] case
        # choose generic str by default
        if str in types:
            value_type = str
            param_value = str(param_value)
        else:
            raise NotImplementedError()
    else:
        # Optional[all-other-types] case
        # pick actual type
        value_type = types[0]

    # In pydantic 2.0, `NonNegativeFloat` yields `typing.Annotated[float, Ge(ge=0)]`,
    # so we have to further extract the primitive type
    if t.get_origin(value_type) is t.Annotated:
        value_type = t.get_args(value_type)[0]

    if t.get_origin(value_type) is t.Literal:
        w_param = ipw.Dropdown(
            description=param.label,
            placeholder=param.description,
            options=t.get_args(value_type),
            value=param_value,
            style=BOX_STYLE,
        )

    elif value_type is bool:
        w_param = ipw.Dropdown(
            description=param.label,
            placeholder=param.description,
            options=[("False", False), ("True", True)],
            value=param_value,
            style=BOX_STYLE,
        )

    elif value_type is float:
        if value_type in [NonNegativeFloat]:
            value_min, value_max = (0.0, 1.0e99)
        else:
            value_min, value_max = (-1.0e99, 1.0e99)

        w_param = ipw.BoundedFloatText(
            description=param.label,
            min=value_min,
            max=value_max,
            value=param_value,
            style=BOX_STYLE,
        )

    elif value_type is int:
        if value_type in [NonNegativeInt]:
            value_min, value_max = (0, 1e99)
        else:
            value_min, value_max = (-1e99, 1e99)

        w_param = ipw.BoundedIntText(
            description=param.label,
            min=value_min,
            max=value_max,
            value=param_value,
            style=BOX_STYLE,
        )

    elif value_type is str:
        w_param = ipw.Text(
            description=param.label,
            placeholder="",
            value=param_value,
            style=BOX_STYLE,
        )

    else:
        raise NotImplementedError()

    def enable_w_param(change=None):
        w_param.disabled = not (w_check.value)

    enable_w_param()

    w_check.observe(enable_w_param, names="value")

    tooltip = param.description
    tooltip += f" ({param.units})" if param.units else ""

    w_info = ipw.Button(
        icon="info",
        tooltip=tooltip,
        disabled=True,
    )
    w_info.add_class("info-logo")

    technique_line = ipw.HBox(
        layout={
            "align_items": "center",
        },
        children=[
            w_param,
            w_check,
        ],
    )

    if tooltip:
        technique_line.children += (w_info, )

    return technique_line
