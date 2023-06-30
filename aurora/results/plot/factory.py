from .model import PlotModel
from .presenter import PlotPresenter
from .view import PlotView


class PlotPresenterFactory():
    """
    docstring
    """

    @staticmethod
    def build(
        plot_type: str,
        plot_model: PlotModel,
        plot_view: PlotView,
    ) -> PlotPresenter:
        """docstring"""
        return PlotPresenter(plot_model, plot_view)
