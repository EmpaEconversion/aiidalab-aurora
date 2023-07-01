from .model import PlotModel
from .presenter import PlotPresenter
from .view import PlotView


class PlotPresenterFactory():
    """
    docstring
    """

    @staticmethod
    def build(
        plot_label: str,
        plot_type: str,
        plot_model: PlotModel,
        plot_view: PlotView,
    ) -> PlotPresenter:
        """docstring"""
        if plot_type == 'test':
            presenter = PlotPresenter(plot_model, plot_view)
            message = f"{plot_label} not yet implemented"
            presenter.close_view(message=message)
            return presenter

        return PlotPresenter(plot_model, plot_view)
