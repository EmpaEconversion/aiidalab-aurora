import ipywidgets as ipw
from aiida.manage.configuration import load_profile

from aurora import __version__
from aurora.common.models import ProtocolsModel, SamplesModel
from aurora.common.models.backends import JSONBackend
from aurora.experiment.builder import ExperimentBuilder
from aurora.experiment.controller import ExperimentController
from aurora.experiment.model import ExperimentModel
from aurora.experiment.view import ExperimentView
from aurora.inventory import InventoryManager
from aurora.results.model import ResultsModel
from aurora.results.presenter import ResultsPresenter
from aurora.results.view import ResultsView

DATA_DIR = "data"
AVAILABLE_SAMPLES_FILE = "available_samples.json"
AVAILABLE_PROTOCOLS_FILE = 'available_protocols.json'

MAIN_LAYOUT = {
    'width': '100%',
    'border': 'solid black 4px',
    'padding': '10px',
}


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
        "Inventory",
        "Experiment",
        "Results",
    )

    def __init__(self) -> None:
        """`MainPanel` constructor."""

        load_profile()

        super().__init__(
            layout={},
            children=[
                ipw.VBox(
                    layout=MAIN_LAYOUT,
                    children=[
                        ipw.HTML(self.TITLE),
                    ],
                ),
                self._build_tabs(),
            ],
        )

    def _build_tabs(self) -> ipw.Tab:
        """Build the main tab sections.

        Returns
        -------
        `ipw.Tab`
            The tab sections of the main panel.
        """

        samples_backend = JSONBackend(DATA_DIR, AVAILABLE_SAMPLES_FILE)
        samples_model = SamplesModel(samples_backend)
        samples_model.load()

        protocols_backend = JSONBackend(DATA_DIR, AVAILABLE_PROTOCOLS_FILE)
        protocols_model = ProtocolsModel(protocols_backend)
        protocols_model.load()

        inventory = InventoryManager(samples_model, protocols_model)

        experiment = self.__build_experiment_section(
            samples_model,
            protocols_model,
        )

        tabs = ipw.Tab(
            children=[
                inventory,
                experiment,
                self._build_results_section(),
            ],
            selected_index=0,
        )

        for i, title in enumerate(self.TAB_LABELS):
            tabs.set_title(i, title)

        return tabs

    def __build_experiment_section(
        self,
        samples_model: SamplesModel,
        protocols_model: ProtocolsModel,
    ) -> ExperimentView:
        """docstring"""
        builder = ExperimentBuilder(samples_model, protocols_model)
        model = ExperimentModel(builder.model)
        view = ExperimentView(builder.view)
        _ = ExperimentController(view, model)
        return view

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
