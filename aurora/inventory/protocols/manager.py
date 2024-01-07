import ipywidgets as ipw

from aurora.common.models import ProtocolsModel

from .editor import ProtocolEditor

BUTTON_LAYOUT = {
    "width": "fit-content",
}


class ProtocolsManager(ipw.VBox):
    """A protocols inventory manager widget.

    Uses a local copy of the protocols model to add/delete/update
    protocols and save to the app's protocols model.
    """

    def __init__(self, protocols_model: ProtocolsModel):
        """`ProtocolsManager` constructor.

        Parameters
        ----------
        `protocols_model` : `ProtocolsModel`
            The app's protocols model.
        """

        self.protocols_model = protocols_model
        self.local_model = self.protocols_model.copy()

        self.editor = ProtocolEditor(self.local_model)

        self.filters = ipw.Accordion(
            layout={},
            children=[
                ipw.HTML("Coming soon"),
            ],
            selected_index=None,
        )
        self.filters.set_title(0, "Filters")

        self.selector = ipw.Select(
            layout={
                "width": "auto",
                "margin": "2px 2px 5px 2px",
            },
            rows=10,
        )
        self.selector.add_class("select-monospace")

        self.preview = ipw.Output(
            layout={
                "margin": "2px",
                "padding": "10px",
                "width": "50%",
                "max_height": "202px",
                "overflow_y": "auto",
                "border": "solid darkgrey 1px"
            })

        self.save = ipw.Button(
            layout=BUTTON_LAYOUT,
            button_style="success",
            icon="check",
            tooltip="Save changes",
            disabled=True,
        )

        self.delete = ipw.Button(
            layout=BUTTON_LAYOUT,
            button_style="danger",
            icon="fa-trash",
            tooltip="Delete protocol",
            disabled=True,
        )

        self.reset = ipw.Button(
            layout=BUTTON_LAYOUT,
            button_style="warning",
            icon="refresh",
            tooltip="Reset changes",
            disabled=True,
        )

        self.edit = ipw.Button(
            layout=BUTTON_LAYOUT,
            button_style="info",
            icon="fa-pencil",
            tooltip="Edit protocol",
        )

        super().__init__(
            layout={},
            children=[
                self.editor,
                # self.filters,
                ipw.HBox(
                    layout={},
                    children=[
                        ipw.VBox(
                            layout={
                                "width": "50%",
                            },
                            children=[
                                self.selector,
                                ipw.HBox(
                                    layout={},
                                    children=[
                                        self.save,
                                        self.delete,
                                        self.reset,
                                        self.edit,
                                    ],
                                )
                            ],
                        ),
                        self.preview,
                    ],
                ),
            ],
        )

        self._set_event_listeners()

        self.refresh()

    def refresh(self, _=None) -> None:
        """Update selector options and save-button state."""
        self.update_options()
        self.save.disabled = self.local_model == self.protocols_model

    def update_options(self, _=None) -> None:
        """Update selector options."""
        protocols = self.local_model.query()
        self.selector.options = [protocol.name for protocol in protocols]
        self.refresh_display()

    def delete_protocol(self, _=None) -> None:
        """Delete protocols from the local model."""
        self.local_model.delete(self.selector.label)

    def reset_changes(self, _=None) -> None:
        """Reset the local model to the protocols model."""
        self.local_model.sync(self.protocols_model)

    def save_changes(self, _=None) -> None:
        """Synchronize protocol models and persist protocols."""
        self.protocols_model.sync(self.local_model)
        self.protocols_model.save()
        self.save.disabled = True

    def edit_protocol(self, _=None) -> None:
        """docstring"""
        protocol = self.local_model.get_protocol(self.selector.value)
        self.editor.load_protocol(protocol)

    def sync_reset_with_save(self, _=None) -> None:
        """Sync the reset button with the save button state."""
        self.reset.disabled = self.save.disabled

    def on_selection(self, change: dict) -> None:
        """Update delete button state and display selection details.

        Parameters
        ----------
        `change` : `dict`
            The state dictionary of the selector.
        """
        name = change["new"]
        self.delete.disabled = name is None
        if name:
            self.display_selection_preview(name)

    def display_selection_preview(self, name: str) -> None:
        """Display details of the current selection."""
        if protocol := self.local_model.get_protocol(name):
            self.preview.clear_output()
            with self.preview:
                self.local_model.display(protocol)

    def refresh_display(self) -> None:
        """docstring"""
        self.display_selection_preview(self.selector.value)

    def _set_event_listeners(self) -> None:
        """Set event listeners."""
        self.save.on_click(self.save_changes)
        self.delete.on_click(self.delete_protocol)
        self.reset.on_click(self.reset_changes)
        self.edit.on_click(self.edit_protocol)
        self.local_model.observe(self.refresh, "updated")
        self.selector.observe(self.on_selection, "value")
        self.save.observe(self.sync_reset_with_save, "disabled")
