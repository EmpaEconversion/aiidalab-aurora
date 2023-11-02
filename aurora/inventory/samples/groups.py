from __future__ import annotations

import ipywidgets as ipw
from traitlets import Integer

from aurora.common.models import SamplesModel

BUTTON_LAYOUT = {
    "width": "fit-content",
}

# TODO use SampleGroup class to encapsulate functionality and state


class SampleGrouping(ipw.Accordion):
    """docstring"""

    changed = Integer(0)

    def __init__(self, model: SamplesModel) -> None:
        """docstring"""

        self.model = model

        self.__samples_to_add: list[int] = []  # TODO make observable
        self.__groups: dict[str, dict[str, set]] = {}

        self.menu = ipw.Dropdown(
            layout={},
            options=[],
        )

        self.new = ipw.Button(
            layout=BUTTON_LAYOUT,
            button_style="primary",
            icon="plus",
            tooltip="New group",
        )

        self.clone = ipw.Button(
            layout=BUTTON_LAYOUT,
            button_style="info",
            icon="fa-copy",
            tooltip="Clone group",
            disabled=True,
        )

        self.delete = ipw.Button(
            layout=BUTTON_LAYOUT,
            button_style="danger",
            icon="fa-trash",
            tooltip="Delete group",
            disabled=True,
        )

        self.add = ipw.Button(
            layout=BUTTON_LAYOUT,
            icon="fa-angle-down",
            tooltip="Add selected samples",
            disabled=True,
        )

        self.remove = ipw.Button(
            layout=BUTTON_LAYOUT,
            icon="fa-angle-up",
            tooltip="Remove selected samples",
            disabled=True,
        )

        self.reset = ipw.Button(
            layout=BUTTON_LAYOUT,
            button_style="warning",
            icon="refresh",
            tooltip="Reset group",
            disabled=True,
        )

        self.save = ipw.Button(
            layout=BUTTON_LAYOUT,
            button_style="success",
            icon="check",
            tooltip="Save group",
            disabled=True,
        )

        self.selector = ipw.SelectMultiple(
            layout={
                "width": "auto",
                "margin": "2px 2px 5px 2px",
            },
            rows=10,
        )
        self.selector.add_class("select-monospace")

        self.new_group_section = ipw.HBox(
            layout={},
            children=[],
        )

        super().__init__(
            layout={},
            children=[
                ipw.VBox(
                    layout={},
                    children=[
                        ipw.HBox(
                            layout={
                                "justify_content": "space-between",
                            },
                            children=[
                                ipw.HBox(
                                    layout={},
                                    children=[
                                        ipw.HBox(
                                            layout={},
                                            children=[
                                                self.menu,
                                                self.new,
                                            ],
                                        ),
                                        self.new_group_section,
                                    ],
                                ),
                                ipw.HBox(
                                    layout={},
                                    children=[
                                        # self.clone,
                                        self.add,
                                        self.remove,
                                        self.reset,
                                        self.delete,
                                        self.save,
                                    ],
                                ),
                            ],
                        ),
                        self.selector,
                    ],
                ),
            ],
            selected_index=None,
        )

        self.set_title(0, "Groups")

        self._set_event_listeners()

        self.reset_groups()

    @property
    def groups(self) -> dict[str, set[int]]:
        """docstring"""
        return {label: items["ids"] for label, items in self.__groups.items()}

    @property
    def samples_to_add(self) -> list[int]:
        """docstring"""
        return self.__samples_to_add

    @samples_to_add.setter
    def samples_to_add(self, ids: tuple[int]) -> None:
        """docstring"""
        self.__samples_to_add = list(ids)

    def reset_groups(self) -> None:
        """docstring"""
        self.__groups.clear()
        groups = self.model.get_group_labels(discard="all-samples")
        for group in groups:
            self.__groups[group] = {"ids": self.model.get_group_samples(group)}
            self.__groups[group]["temp"] = self.__groups[group]["ids"].copy()
        self.update()

    def update(self, _=None) -> None:
        """docstring"""
        self.update_menu()
        self.update_selector()

    def update_menu(self) -> None:
        """docstring"""
        self.menu.options = list(self.__groups.keys())

    def update_selector(self, _=None) -> None:
        """docstring"""
        if group := self.menu.value:
            query = {"id": list(self.__groups[group]["ids"])}
            group_samples = self.model.query(query)
            self.selector.options = self.model.as_options(group_samples)
        else:
            self.selector.options = []
        self.changed += 1

    def on_group_selection(self, _=None) -> None:
        """docstring"""
        self.update_selector()
        self.toggle_add_button()
        self.toggle_delete_button()
        self.toggle_save_reset_buttons()

    def store_group_state(self, label: str) -> None:
        """docstring"""
        if group := self.__groups.get(label):
            group["temp"] = group["ids"].copy()

    def toggle_add_button(self) -> None:
        """docstring"""
        self.add.disabled = not (self.menu.value and self.__samples_to_add)

    def toggle_remove_button(self, change: dict) -> None:
        """docstring"""
        self.remove.disabled = not change["new"]

    def toggle_delete_button(self) -> None:
        """docstring"""
        self.delete.disabled = not self.menu.value

    def toggle_save_reset_buttons(self, _=None) -> None:
        """docstring"""
        group = self.menu.value
        items = self.__groups.get(group)
        self.save.disabled = not items or (items["temp"] == items["ids"])
        self.reset.disabled = self.save.disabled

    def open_new_group_widget(self, _=None) -> None:
        """docstring"""

        self.new.disabled = True

        self.group_name = ipw.Text(
            layout={},
            placeholder="Enter new group name",
        )

        name_approve = ipw.Button(
            layout=BUTTON_LAYOUT,
            button_style="success",
            icon="check",
            tooltip="Approve group name",
        )

        self.new_group_section.children += (
            self.group_name,
            name_approve,
        )

        name_approve.on_click(self.add_group)

    def add_group(self, _=None) -> None:
        """docstring"""
        self.__groups[self.group_name.value] = {"ids": set(), "temp": set()}
        self.menu.options = (*self.menu.options, self.group_name.value)
        self.menu.value = self.group_name.value
        self.new_group_section.children = []
        self.new.disabled = False

    def clone_group(self, _=None) -> None:
        """docstring"""
        # TODO treat as new group

    def add_to_group(self, _=None) -> None:
        """docstring"""
        group = self.menu.value
        items = self.__groups[group]
        items["ids"] |= set(self.samples_to_add)
        self.update_selector()

    def remove_from_group(self, _=None) -> None:
        """docstring"""
        group = self.menu.value
        items = self.__groups[group]
        items["ids"] -= set(self.selector.value)
        self.update_selector()

    def reset_group(self, _=None) -> None:
        """docstring"""
        group = self.menu.value
        items = self.__groups[group]
        items["ids"] = items["temp"].copy()
        self.update_selector()

    def delete_group(self, _=None) -> None:
        """docstring"""
        group = self.menu.value
        del self.__groups[group]
        self.model.save_group([], group)

    def save_group(self, _=None) -> None:
        """docstring"""
        group = self.menu.value
        items = self.__groups[group]
        items["temp"] = items["ids"].copy()
        self.model.save_group(list(items["ids"]), group)

    def _set_event_listeners(self) -> None:
        """docstring"""
        self.menu.observe(self.on_group_selection, "value")
        self.selector.observe(self.toggle_remove_button, "value")
        self.new.on_click(self.open_new_group_widget)
        self.clone.on_click(self.clone_group)
        self.delete.on_click(self.delete_group)
        self.add.on_click(self.add_to_group)
        self.remove.on_click(self.remove_from_group)
        self.reset.on_click(self.reset_group)
        self.save.on_click(self.save_group)
        self.model.observe(self.update, "updated")
        self.observe(self.toggle_save_reset_buttons, "changed")
