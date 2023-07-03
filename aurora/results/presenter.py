from typing import List, Tuple

from .model import ResultsModel
from .plot.factory import PlotPresenterFactory
from .plot.model import PlotModel
from .plot.presenter import PlotPresenter
from .plot.view import PlotView
from .view import ResultsView


class ResultsPresenter():
    """
    docstring
    """

    def __init__(
        self,
        model: ResultsModel,
        view: ResultsView,
    ) -> None:
        """docstring"""

        self.model = model
        self.view = view

        self._set_event_handlers()

    def update_view_experiments(self, _=None) -> None:
        """docstring"""
        self.model.update_experiments()
        options = self._build_experiment_selector_options()
        self.view.experiment_selector.options = options

    def update_plot_button_state(self, _=None) -> None:
        """docstring"""
        no_experiments = not bool(self.view.experiment_selector.value)
        no_plot_type = not bool(self.view.plot_type_selector.value)
        self.view.plot_button.disabled = no_experiments or no_plot_type

    def on_plot_button_clicked(self, _=None) -> None:
        """docstring"""
        self.view.info.clear_output()
        if self._has_valid_selection():
            self.add_plot_view()

    def add_plot_view(self) -> None:
        """docstring"""

        experiment_ids = self.view.experiment_selector.value
        plot_label = self.view.plot_type_selector.label
        plot_type = self.view.plot_type_selector.value

        plot_view = PlotView()

        title = f"{plot_label} for experiment"
        title += "s" if len(experiment_ids) > 1 else ""
        title += f" {', '.join(str(id) for id in experiment_ids)}"

        plot_view.set_title(0, title)

        plot_model = PlotModel(self.model, experiment_ids)

        plot_presenter = PlotPresenterFactory.build(
            plot_label,
            plot_type,
            plot_model,
            plot_view,
        )

        if plot_presenter.closing_message:
            message = plot_presenter.closing_message
            self.display_info_message(message)
            return

        self.view.plots_container.children += (plot_view, )

        plot_presenter.observe(
            names="closing_message",
            handler=self.remove_plot_view,
        )

        plot_presenter.start()

    def remove_plot_view(self, trait: dict) -> None:
        """docstring"""

        plot_presenter: PlotPresenter = trait["owner"]

        if (message := trait["new"]) != 'closed':
            self.display_info_message(message)

        if plot_presenter.view in self.view.plot_views:
            self.view.plots_container.children = [
                view for view in self.view.plot_views
                if view is not plot_presenter.view
            ]

        plot_presenter.unobserve(self.remove_plot_view)

    def display_info_message(self, message: str) -> None:
        """docstring"""

        with self.view.info:
            print(message)

    def _set_event_handlers(self) -> None:
        """docstring"""

        self.view.on_displayed(self.update_view_experiments)
        self.view.plot_button.on_click(self.on_plot_button_clicked)
        self.view.update_button.on_click(self.update_view_experiments)

        self.view.experiment_selector.observe(
            names="value",
            handler=self.update_plot_button_state,
        )

        self.view.plot_type_selector.observe(
            names="value",
            handler=self.update_plot_button_state,
        )

    def _build_experiment_selector_options(self) -> List[Tuple]:
        """Returns a (option_string, battery_id) list."""
        return [(as_option(row), row['id'])
                for _, row in self.model.experiments.iterrows()]

    def _has_valid_selection(self) -> bool:
        """docstring"""

        plot_label = self.view.plot_type_selector.label
        experiment_ids = self.view.experiment_selector.value

        labels = [label for label, _ in self.view.STATISTICAL_PLOT_TYPES]

        if plot_label in labels and len(experiment_ids) < 2:
            self.display_info_message("Please select more than one experiment")
            return False

        return True


def as_option(row: dict) -> str:
    """docstring"""
    return f"{row['id']:5} : {row['ctime']} : {row['label'] or 'Experiment'}"
