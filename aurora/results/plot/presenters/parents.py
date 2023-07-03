from ..presenter import PlotPresenter


class MultiSeriesPlotPresenter(PlotPresenter):
    """
    docstring
    """

    def draw(self) -> None:
        """docstring"""
        with self.view.plot:
            for eid, dataset in self.model.data.items():
                if dataset:
                    self.plot_series(eid, dataset)


class StatisticalPlotPresenter(PlotPresenter):
    """
    docstring
    """

    def draw(self) -> None:
        """docstring"""
        with self.view.plot:
            if self.model.data:
                self.plot_series(0, self.model.data)
