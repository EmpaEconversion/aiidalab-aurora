from __future__ import annotations

import ipywidgets as ipw

from .preview.view import InputPreviewView
from .protocols.view import ProtocolSelectorView
from .samples.view import SampleSelectorView
from .settings.view import SettingsSelectorView
from .utils import ResettableView

ACCORDION_STEPS = [
    "Select samples",
    "Select protocols",
    "Configure tomato/monitoring",
    "Generate input",
]


class ExperimentBuilderView(ipw.Accordion):
    """docstring"""

    def __init__(
        self,
        samples_section: SampleSelectorView,
        protocols_section: ProtocolSelectorView,
        settings_section: SettingsSelectorView,
        preview_section: InputPreviewView,
    ) -> None:
        """docstring"""

        self.sections: tuple[ResettableView, ...] = (
            samples_section,
            protocols_section,
            settings_section,
        )

        self.preview = preview_section

        super().__init__(
            layout={},
            children=[
                *self.sections,
                self.preview,
            ],
            selected_index=None,
        )

        for i, title in enumerate(ACCORDION_STEPS):
            self.set_title(i, title)
