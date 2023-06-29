import ipywidgets as ipw

from .samples import ManageSamplesMenu


class InventoryManager(ipw.VBox):
    """
    An inventory manager of experiment components. Includes managing
    samples, groups, specs, and protocols.
    """

    def __init__(self) -> None:
        """docstring"""

        samples_manager = ManageSamplesMenu()

        super().__init__(
            layout={},
            children=[
                samples_manager,
            ],
        )
