import ipywidgets as ipw

from aurora.common.models import ProtocolsModel, SamplesModel

from .protocols import ProtocolsManager
from .samples.manager import SamplesManager


class InventoryManager(ipw.Tab):
    """
    An inventory manager of experiment components. Includes managing
    samples, groups, specs, and protocols.
    """

    TAB_LABELS = (
        "Samples",
        "Protocols",
    )

    def __init__(
        self,
        samples_model: SamplesModel,
        protocols_model: ProtocolsModel,
    ) -> None:
        """docstring"""

        samples_manager = SamplesManager(samples_model)
        protocols_manager = ProtocolsManager(protocols_model)

        super().__init__(
            layout={},
            children=[
                samples_manager,
                protocols_manager,
            ],
        )

        for i, label in enumerate(self.TAB_LABELS):
            self.set_title(i, label)
