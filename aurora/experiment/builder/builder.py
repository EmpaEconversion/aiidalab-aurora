from __future__ import annotations

import ipywidgets as ipw

from aurora.common.models import ProtocolsModel, SamplesModel
from aurora.common.widgets.filters import Filters

from .controller import ExperimentBuilderController
from .model import ExperimentBuilderModel
from .preview.controller import InputPreviewController
from .preview.model import InputPreviewModel
from .preview.view import InputPreviewView
from .protocols.controller import ProtocolSelectorController
from .protocols.model import ProtocolSelectorModel
from .protocols.view import ProtocolSelectorView
from .samples.controller import SampleSelectorController
from .samples.model import SampleSelectorModel
from .samples.view import SampleSelectorView
from .settings.controller import SettingsSelectorController
from .settings.model import SettingsSelectorModel
from .settings.view import SettingsSelectorView
from .view import ExperimentBuilderView


class ExperimentBuilder:
    """docstring"""

    def __init__(
        self,
        samples_model: SamplesModel,
        protocols_model: ProtocolsModel,
    ) -> None:

        self.model = ExperimentBuilderModel(samples_model, protocols_model)

        self.view = ExperimentBuilderView(
            samples_section=self.__build_sample_section(samples_model),
            protocols_section=self.__build_protocol_section(protocols_model),
            settings_section=self.__build_settings_section(),
            preview_section=self.__build_preview_section(
                samples_model,
                protocols_model,
            ),
        )

        _ = ExperimentBuilderController(self.view, self.model)

    ###########
    # PRIVATE #
    ###########

    def __build_sample_section(
        self,
        samples_model: SamplesModel,
    ) -> SampleSelectorView:
        """Build the sample selection section."""

        model = SampleSelectorModel(samples_model)

        filters = Filters(
            model=samples_model,
            fields={
                "Batch": "metadata.batch",
                "Sub-batch": "metadata.subbatch",
                "Manufacturer": "specs.manufacturer",
                "Separator": "specs.composition.separator.name",
                "Cathode": "specs.composition.cathode.formula",
                "Anode": "specs.composition.anode.formula",
                "Electrolyte": "specs.composition.electrolyte.formula",
                "Capacity (mAh)": "specs.capacity.nominal",
            },
        )

        view = SampleSelectorView(filters)

        _ = SampleSelectorController(view, model)

        ipw.dlink((model, "selected"), (self.model, "samples"))

        return view

    def __build_protocol_section(
        self,
        protocols_model: ProtocolsModel,
    ) -> ProtocolSelectorView:
        """Build the cycling protocol section."""
        model = ProtocolSelectorModel(protocols_model)
        view = ProtocolSelectorView()
        _ = ProtocolSelectorController(view, model)
        ipw.dlink((model, "selected"), (self.model, "protocols"))
        return view

    def __build_settings_section(self) -> SettingsSelectorView:
        """Build the settings section."""
        model = SettingsSelectorModel()
        view = SettingsSelectorView()
        _ = SettingsSelectorController(view, model)
        ipw.dlink((self.model, "protocols"), (model, "protocols"))
        ipw.dlink((model, "selected"), (self.model, "settings"))
        return view

    def __build_preview_section(
        self,
        samples_model: SamplesModel,
        protocols_model: ProtocolsModel,
    ) -> InputPreviewView:
        """Build the settings section."""
        model = InputPreviewModel(samples_model, protocols_model)
        view = InputPreviewView()
        controller = InputPreviewController(view, model)
        ipw.dlink((self.model, "samples"), (model, "samples"))
        ipw.dlink((self.model, "protocols"), (model, "protocols"))
        ipw.dlink((self.model, "settings"), (model, "settings"))
        ipw.link((self.model, "valid_input"), (model, "valid_input"))
        self.model.observe(controller.display_preview, "generate_preview")
        return view
