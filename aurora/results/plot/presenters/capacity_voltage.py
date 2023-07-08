from typing import Tuple

import numpy as np

from .parents import MultiSeriesPlotPresenter


class CapacityVoltagePlotPresenter(MultiSeriesPlotPresenter):
    """
    docstring
    """

    TITLE = 'C vs. V'

    X_LABEL = 'Ewe [V]'

    Y_LABEL = 'Q [mAh]'

    def extract_data(self, dataset: dict) -> Tuple:
        """docstring"""

        x = dataset["Ewe"]

        if 'Q' not in dataset:

            t = dataset['time']
            I = dataset['I']

            Q = []
            for i in range(len(t)):
                q = np.trapz(I[:i], t[:i])
                Q.append(q)

            dataset['Q'] = np.array(Q)

        y = dataset['Q'] / 3.6

        return (x, y)
