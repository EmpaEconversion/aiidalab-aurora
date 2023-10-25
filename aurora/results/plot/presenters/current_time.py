from .parents import MultiSeriesPlotPresenter


class CurrentTimePlotPresenter(MultiSeriesPlotPresenter):
    """
    docstring
    """

    TITLE = "I vs. t"

    X_LABEL = "t [h]"

    Y_LABEL = "I [mA]"

    def extract_data(self, dataset: dict) -> tuple:
        """docstring"""
        x = dataset["time"] / 3600.
        y = dataset["I"] * 1000.
        return (x, y)
