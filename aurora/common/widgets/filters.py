from __future__ import annotations

from typing import Any, Callable

import ipywidgets as ipw
from traitlets import Integer

from aurora.common.models.samples import SamplesModel

GRID_LAYOUT = {
    "grid_template_columns": "repeat(4, 22%)",
    "justify_content": "space-around",
}

FILTER_LAYOUT = {
    "width": "95%",
    "height": "100px",
}

GROUP_LAYOUT = {
    "width": "100%",
    "padding": "0 8px 0 0",
    "grid_area": "b",
}

GROUP_STYLE = {
    "description_width": "60px",
}

DATE_LAYOUT = {
    "width": "100%",
    "padding": "0 7px 0 0",
}

DATE_STYLE = {
    "description_width": "40px",
}

BUTTON_LAYOUT = {
    "width": "fit-content",
    "margin": "0 20px",
}

FIELDS = {
    "Batch": "metadata.batch",
    "Sub-batch": "metadata.subbatch",
    "Manufacturer": "specs.manufacturer",
    "Separator": "specs.composition.separator.name",
    "Cathode": "specs.composition.cathode.formula",
    "Anode": "specs.composition.anode.formula",
    "Electrolyte": "specs.composition.electrolyte.formula",
    "Capacity (mAh)": "specs.capacity.nominal",
}


def silent(method: Callable) -> Callable:
    """docstring"""

    def wrapper(self: Filters, *args, **kwargs):
        """docstring"""
        self._unsubscribe_observers()
        method(self, *args, **kwargs)
        self._subscribe_observers()

    return wrapper


class SpecFilter(ipw.VBox):
    """docstring"""

    def __init__(self, field: str, description: str) -> None:
        """docstring"""

        self.filter = ipw.SelectMultiple(layout=FILTER_LAYOUT)
        self.filter.field = field

        self.filter.add_class("select-monospace")

        super().__init__(
            layout={
                "align_items": "center",
            },
            children=[
                ipw.Label(description),
                self.filter,
            ],
        )


class Filters(ipw.Accordion):
    """docstring"""

    changed = Integer(0)

    def __init__(
        self,
        model: SamplesModel,
        fields: dict[str, str] | None = None,
    ) -> None:
        """docstring"""

        self.__model = model

        self.group = ipw.Dropdown(
            layout=GROUP_LAYOUT,
            style=GROUP_STYLE,
            description="By group:",
        )

        self.from_ = ipw.DatePicker(
            layout=DATE_LAYOUT,
            style=DATE_STYLE,
            description="From:",
        )

        self.to = ipw.DatePicker(
            layout=DATE_LAYOUT,
            style=DATE_STYLE,
            description="To:",
        )

        self.grid = ipw.GridBox(layout=GRID_LAYOUT)

        for description, field in (fields or FIELDS).items():
            self.add_grid_filter(field, description)

        self.reset_button = ipw.Button(
            layout=BUTTON_LAYOUT,
            button_style="warning",
            icon="refresh",
            tooltip="Reset fields",
        )

        super().__init__(
            layout={},
            children=[
                ipw.VBox(
                    layout={},
                    children=[
                        self.grid,
                        ipw.GridBox(
                            layout={
                                "margin": "5px 0",
                                "justify_content": "space-around",
                                "grid_template_columns": "repeat(4, 22%)",
                                "grid_template_areas": "'b b r g'",
                            },
                            children=[
                                self.group,
                                self.from_,
                                self.to,
                            ],
                        ),
                        ipw.HBox(
                            layout={
                                "justify_content": "flex-end",
                            },
                            children=[
                                self.reset_button,
                            ],
                        ),
                    ],
                ),
            ],
            selected_index=None,
        )

        self.set_title(0, "Filters")

        self._set_event_listeners()

        self.update()

    @property
    def grid_filters(self) -> list[SpecFilter]:
        return [box.filter for box in self.grid.children]

    @property
    def current_state(self) -> dict[str, Any]:
        return {
            "group": self.group.value,
            "from": self.from_.value,
            "to": self.to.value,
            **{
                filter.field: filter.value
                for filter in self.grid_filters if filter.value
            },
        }

    def on_change(self, _=None) -> None:
        """docstring"""
        self.update_grid()
        self.changed += 1

    def update(self, reset=False) -> None:
        """docstring"""
        self.update_groups()
        # HACK deleting samples in the manager from a filtered set raises
        # an error due to the filter still being selected after it no longer
        # exists. This hack resets the filters prior to the update. Rethink!
        if reset:
            self.reset()
        self.update_grid()

    def update_groups(self) -> None:
        """docstring"""
        self.group.options = self.__model.get_group_labels()

    @silent
    def update_grid(self) -> None:
        """docstring"""
        self._build_grid_options()

    def add_grid_filter(self, field: str, description: str) -> None:
        """docstring"""
        new_filter = SpecFilter(field, description)
        self.grid.children += (new_filter, )
        new_filter.filter.observe(self.on_change, "value")

    # TODO silent? post-update?
    def reset(self, _=None) -> None:
        """docstring"""
        self.group.value = "all-samples" if self.group.options else None
        self.from_.value = None
        self.to.value = None
        for filter in self.grid_filters:
            filter.value = []

    def _build_grid_options(self) -> None:
        """docstring"""
        for filter in self.grid_filters:
            value = filter.value
            filter.options = self._build_filter_options(filter.field)
            filter.value = value

    def _build_filter_options(
        self,
        field: str,
    ) -> list[tuple[str, Any]]:
        """docstring"""

        if not self.__model.has_samples():
            return []

        query = self.current_state
        query.pop(field, None)
        result = self.__model.query(query, project=[field])

        value_counts = result[field].value_counts()

        options_pairs: list[tuple[str, Any]] = []

        result = self.__model.query({}, project=[field])

        relevant_indexes = result[field].unique()

        for index_label in relevant_indexes:
            count = value_counts.get(index_label, 0)
            options_pairs.append((f"{index_label} [{count}]", index_label))

        return options_pairs

    def _subscribe_observers(self) -> None:
        """docstring"""
        for filter in self.grid_filters:
            filter.observe(self.on_change, "value")

    def _unsubscribe_observers(self) -> None:
        """docstring"""
        for filter in self.grid_filters:
            filter.unobserve(self.on_change, "value")

    def _set_event_listeners(self) -> None:
        """docstring"""
        self.reset_button.on_click(self.reset)
        self.group.observe(self.on_change, "value")
        self.from_.observe(self.on_change, "value")
        self.to.observe(self.on_change, "value")
