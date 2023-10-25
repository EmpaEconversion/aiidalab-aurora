import aurora.results.plot.presenters as presenters

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
        if plot_type == 'current_time':
            presenter = presenters.CurrentTimePlotPresenter
        elif plot_type == 'voltage_time':
            presenter = presenters.VoltageTimePlotPresenter
        elif plot_type == 'voltagecurrent_time':
            presenter = presenters.VoltageCurrentTimePlotPresenter
        elif plot_type == 'voltage_capacity':
            presenter = presenters.VoltageCapacityPlotPresenter
        elif plot_type == 'efficiency_cycle':
            presenter = presenters.EfficiencyCyclePlotPresenter
        elif plot_type == 'capacity_cycle':
            presenter = presenters.CapacityCyclePlotPresenter
        elif plot_type == 'capacity_swarm':
            presenter = presenters.CapacitySwarmPlotPresenter
        else:
            presenter = PlotPresenter(plot_model, plot_view)
            message = f"{plot_label} not yet implemented"
            presenter.close_view(message=message)
            return presenter

        return presenter(plot_model, plot_view)
