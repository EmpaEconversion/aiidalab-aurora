from .model import PlotModel
from .presenter import PlotPresenter
from .presenters import (CapacityCyclePlotPresenter,
                         CapacityVoltagePlotPresenter,
                         CurrentTimePlotPresenter,
                         VoltageCurrentTimePlotPresenter,
                         VoltageTimePlotPresenter)
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
            presenter = CurrentTimePlotPresenter
        elif plot_type == 'voltage_time':
            presenter = VoltageTimePlotPresenter
        elif plot_type == 'voltagecurrent_time':
            presenter = VoltageCurrentTimePlotPresenter
        elif plot_type == 'capacity_cycle':
            presenter = CapacityCyclePlotPresenter
        elif plot_type == 'capacity_voltage':
            presenter = CapacityVoltagePlotPresenter
        else:
            presenter = PlotPresenter(plot_model, plot_view)
            message = f"{plot_label} not yet implemented"
            presenter.close_view(message=message)
            return presenter

        return presenter(plot_model, plot_view)
