import ipywidgets as ipw

from aurora import __version__
from aurora.experiment import ExperimentBuilder
from aurora.inventory import InventoryManager
from aurora.results.model import ResultsModel
from aurora.results.presenter import ResultsPresenter
from aurora.results.view import ResultsView


class MainPanel(ipw.VBox):
    """
    Aurora's main panel containing the tab sections for submitting
    experiments, managing the samples/protocols inventory, and
    visualizing experiment results.
    """

    TITLE = f"""
        <div style="text-align: center;">
            <h1>AURORA</h1>
            <p>Version {__version__}</p>
        </div>
    """

    TAB_LABELS = (
        "Experiment",
        "Inventory",
        "Results",
    )

    def __init__(self) -> None:
        """`MainPanel` constructor."""

        header = ipw.VBox(
            layout={
                'width': '100%',
                'border': 'solid black 4px',
                'padding': '10px'
            },
            children=[
                ipw.HTML(self.TITLE),
            ],
        )

        tabs = self._build_tabs()

        super().__init__(
            layout={},
            children=[
                header,
                tabs,
            ],
        )

    def _build_tabs(self) -> ipw.Tab:
        """Build the main tab sections.

        Returns
        -------
        `ipw.Tab`
            The tab sections of the main panel.
        """

        experiment = ExperimentBuilder()
        manager = InventoryManager()

        tabs = ipw.Tab(
            children=[
                experiment,
                manager,
                self._build_results_section(),
            ],
            selected_index=0,
        )

        for i, title in enumerate(self.TAB_LABELS):
            tabs.set_title(i, title)

        return tabs

    def _build_results_section(self) -> ResultsView:
        """Build the results section, connecting the results model,
        view, and presenter. The presenter is set to listen and
        respond to view events.

        Returns
        -------
        `ResultsView`
            The results view as an `ipw.VBox`.
        """
        model = ResultsModel()
        view = ResultsView()
        _ = ResultsPresenter(model, view)
        return view
