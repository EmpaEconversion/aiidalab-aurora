from .parents import MultiSeriesPlotPresenter


class VoltageTimePlotPresenter(MultiSeriesPlotPresenter):
    """
    docstring
    """

    TITLE = "V vs. t"

    X_LABEL = "t [h]"

    Y_LABEL = "Ewe [V]"

    def extract_data(self, dataset: dict) -> tuple:
        """docstring"""
        x = dataset["time"] / 3600.
        y = dataset["Ewe"]
        return (x, y)
