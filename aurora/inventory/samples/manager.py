from typing import List

import ipywidgets as ipw
from aiida_aurora.schemas.utils import pd_dataframe_to_formatted_json

from aurora.common.models import SamplesModel
from aurora.common.widgets import Filters

from .groups import SampleGrouping
from .importer import SamplesImporter

BUTTON_LAYOUT = {
    "width": "fit-content",
}

PREVIEW_LAYOUT = {
    "max_height": "300px",
    "overflow_y": "auto",
}


class SamplesManager(ipw.VBox):
    """A samples inventory manager widget.

    Uses a local copy of the samples model to add/delete/update
    samples and save to the app's samples model.
    """

    def __init__(self, samples_model: SamplesModel):
        """`SamplesManager` constructor..

        Parameters
        ----------
        `samples_model` : `SamplesModel`
            The app's samples model.
        """

        self.samples_model = samples_model
        self.local_model = self.samples_model.copy()

        self.importer = SamplesImporter(self.local_model)

        self.filters = Filters(self.local_model)

        self.group_manager = SampleGrouping(self.local_model)

        self.legend = ipw.HTML(samples_model.get_options_legend())

        self.selector = ipw.SelectMultiple(
            layout={
                "width": "auto",
            },
            rows=10,
        )
        self.selector.add_class("select-monospace")

        self.preview = ipw.Output(layout=PREVIEW_LAYOUT)

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
            tooltip="Delete selected samples",
            disabled=True,
        )

        self.reset = ipw.Button(
            layout=BUTTON_LAYOUT,
            button_style="warning",
            icon="refresh",
            tooltip="Reset changes",
            disabled=True,
        )

        self.subbatch = ipw.Text(
            layout={},
            description="Sub-batch:",
            placeholder="Enter sub-batch id",
        )

        self.subbatch_approve = ipw.Button(
            layout=BUTTON_LAYOUT,
            button_style="success",
            icon="check",
            tooltip="Approve batch id",
            disabled=True,
        )

        super().__init__(
            layout={},
            children=[
                self.importer,
                self.filters,
                self.legend,
                self.selector,
                self.group_manager,
                ipw.HBox(
                    layout={
                        "margin": "5px 0 0 0",
                        "justify_content": "space-between",
                    },
                    children=[
                        ipw.HBox(
                            layout={},
                            children=[
                                self.save,
                                self.delete,
                                self.reset,
                            ],
                        ),
                        ipw.HBox(
                            layout={},
                            children=[
                                self.subbatch,
                                self.subbatch_approve,
                            ],
                        ),
                    ],
                ),
                self.preview,
            ],
        )

        self._set_event_listeners()

        self.refresh()

    def refresh(self, _=None) -> None:
        """Update filter/selector options and save-button state."""
        self.importer.reset()
        self.filters.update(reset=True)
        self.group_manager.update()
        self.update_selector()
        self.toggle_save_button()

    def is_modified(self) -> bool:
        """Check if local model is different from global model.

        Returns
        -------
        `bool`
            `False` if models are synced, `True` otherwise.
        """
        return self.local_model != self.samples_model

    def toggle_save_button(self) -> None:
        """Disable/enable save button based on model state."""
        self.save.disabled = not self.is_modified()

    def toggle_subbatch_approve_button(self, _=None) -> None:
        """docstring"""
        self.subbatch_approve.disabled = \
            not (self.subbatch.value and self.selector.value)

    def update_selector(self, _=None) -> None:
        """Update selector options."""
        query = self.filters.current_state
        table = self.local_model.query(query)
        self.selector.options = self.local_model.as_options(table)

    def assign_sub_batch(self, _=None) -> None:
        """docstring"""
        self.local_model.assign_subbatch(
            ids=list(self.selector.value),
            subbatch=self.subbatch.value,
        )

    def delete_samples(self, _=None) -> None:
        """Delete samples from the local model."""
        self.local_model.delete_many(self.selector.value, save=False)
        self.preview.clear_output()

    def reset_changes(self, _=None) -> None:
        """Reset the local model to the samples model."""
        self.filters.reset()
        self.local_model.sync(self.samples_model)
        self.group_manager.reset_groups()

    def save_changes(self, _=None) -> None:
        """Synchronize sample models and persist samples."""
        # TODO can this be done more cleanly (at least move to model)
        df = self.local_model.samples.reset_index()
        self.local_model.raw = pd_dataframe_to_formatted_json(df)
        self.samples_model.sync(self.local_model)
        self.samples_model.save()
        self.samples_model.update_aiida_groups(self.group_manager.groups)
        self.save.disabled = True
        self.refresh()

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
        sample_ids = change["new"]
        self.delete.disabled = not sample_ids
        self.group_manager.samples_to_add = sample_ids
        self.group_manager.toggle_add_button()  # TODO revisit
        self.toggle_subbatch_approve_button()
        self.display_selection_preview(sample_ids)

    def display_selection_preview(self, sample_ids: List[int]) -> None:
        """Display details of the current selection."""
        self.preview.clear_output()
        if sample_ids:
            result = self.local_model.query({"id": sample_ids})
            with self.preview:
                self.local_model.display(result)

    def _set_event_listeners(self) -> None:
        """Set event listeners."""
        self.save.on_click(self.save_changes)
        self.delete.on_click(self.delete_samples)
        self.reset.on_click(self.reset_changes)
        self.local_model.observe(self.refresh, "updated")
        self.selector.observe(self.on_selection, "value")
        self.filters.observe(self.update_selector, "changed")
        self.save.observe(self.sync_reset_with_save, "disabled")
        self.subbatch.observe(self.toggle_subbatch_approve_button, "value")
        self.subbatch_approve.on_click(self.assign_sub_batch)
