import ipywidgets as ipw
from traitlets import HasTraits, Unicode

from .model import PlotModel
from .view import PlotView


class PlotPresenter(HasTraits):
    """
    docstring
    """
    TITLE = ''

    X_LABEL = ''

    Y_LABEL = ''

    closing_message = Unicode('')

    def __init__(
        self,
        model: PlotModel,
        view: PlotView
    ) -> None:
        """docstring"""
        self.model = model
        self.view = view

    def start(self) -> None:
        """docstring"""
        self._set_event_handlers()
        self._fetch_data()

    def close_view(self, _=None, message='closed') -> None:
        """docstring"""
        self.closing_message = message
        self.view.close()

    ###################
    # PRIVATE METHODS #
    ###################

    def _set_event_handlers(self) -> None:
        """docstring"""
        self.view.delete_button.on_click(self.close_view)

    def _fetch_data(self) -> None:
        """docstring"""

        for eid in self.model.experiment_ids:
            info_tab = self._add_info_tab(eid)

            with info_tab:
                self.model.fetch_data(eid)

    def _add_info_tab(self, eid: int) -> ipw.Output:
        """docstring"""

        info_tab = ipw.Output(layout={
            "overflow_y": "auto",
            "max_height": "260px",
        })

        self.view.info.children += (info_tab, )

        tab_index = len(self.view.info.children) - 1
        self.view.info.set_title(tab_index, str(eid))

        self.view.eid_tab_mapping[eid] = tab_index

        return info_tab
