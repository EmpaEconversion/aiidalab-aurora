import ipywidgets as ipw

from aurora.common.widgets.filters import Filters

from ..utils import ResettableView

BOX_LAYOUT = {
    "flex": "1",
}

BOX_STYLE = {
    "description_width": "5%",
}

CONTROLS_LAYOUT = {
    "width": "70px",
    "align_items": "center",
}

BUTTON_LAYOUT = {
    "width": "fit-content",
    "margin": "2px 2px 2px auto",
}

MAIN_LAYOUT = {
    "width": "auto",
    "margin": "2px",
    "padding": "10px",
    "border": "solid darkgrey 1px"
}


class SampleSelectorView(ResettableView):
    """The sample selection view."""

    def __init__(self, filters: Filters) -> None:
        """`SampleSelectorView` constructor.

        Parameters
        ----------
        `filters` : `Filters`
            A filters widget.
        """

        self.filters = filters

        super().__init__(
            layout={},
            children=[
                self.filters,
                self.__build_selection_container(),
            ],
        )

    ###########
    # PRIVATE #
    ###########

    def __build_selection_container(self) -> ipw.VBox:
        """Build the sample selection section.

        Includes widgets for sample (de)selection.

        Returns
        -------
        `ipw.VBox`
            A container of sample selection widgets.
        """
        return ipw.VBox(
            layout=MAIN_LAYOUT,
            children=[
                self.__build_selection_section(),
                self.__build_selected_section(),
                self.reset,
            ],
        )

    def __build_selection_section(self) -> ipw.HBox:
        """Build a container for sample selection including controls.

        Returns
        -------
        `ipw.HBox`
            A container for sample selection widgets.
        """

        self.selector = ipw.SelectMultiple(
            layout=BOX_LAYOUT,
            style=BOX_STYLE,
            rows=10,
        )
        self.selector.add_class("select-monospace")

        return ipw.HBox(
            layout={},
            children=[
                ipw.VBox(
                    layout=CONTROLS_LAYOUT,
                    children=[
                        ipw.Label(
                            value="Samples:",
                            layout={},
                        ),
                        self.__build_selection_controls(),
                    ],
                ),
                self.selector,
            ],
        )

    def __build_selection_controls(self) -> ipw.VBox:
        """Build a container of sample selection controls widgets.

        Returns
        -------
        `ipw.VBox`
            A container of sample selection control widgets.
        """

        self.select = ipw.Button(
            description="",
            button_style="",
            tooltip="Select chosen sample",
            icon="fa-angle-down",
            layout=BUTTON_LAYOUT,
        )

        self.select_all = ipw.Button(
            description="",
            button_style="",
            tooltip="Select all samples",
            icon="fa-angle-double-down",
            layout=BUTTON_LAYOUT,
        )

        return ipw.VBox(
            layout={},
            children=[
                self.select,
                self.select_all,
            ],
        )

    def __build_selected_section(self) -> ipw.HBox:
        """Build a container for sample deselection including
        controls.

        Returns
        -------
        `ipw.HBox`
            A container for sample deselection widgets.
        """

        self.selected = ipw.SelectMultiple(
            layout=BOX_LAYOUT,
            style=BOX_STYLE,
            rows=10,
        )
        self.selected.add_class("select-monospace")

        return ipw.HBox(
            layout={},
            children=[
                ipw.VBox(
                    layout=CONTROLS_LAYOUT,
                    children=[
                        ipw.Label(
                            value="Selected:",
                            layout={},
                        ),
                        self.__build_deselection_controls(),
                    ],
                ),
                self.selected,
            ],
        )

    def __build_deselection_controls(self) -> ipw.VBox:
        """Build a container of sample deselection controls widgets.

        Returns
        -------
        `ipw.VBox`
            A container of sample deselection control widgets.
        """

        self.deselect = ipw.Button(
            description="",
            button_style="",
            tooltip="Deselect chosen sample",
            icon="fa-angle-up",
            layout=BUTTON_LAYOUT,
        )

        self.deselect_all = ipw.Button(
            description="",
            button_style="",
            tooltip="Deselect all samples",
            icon="fa-angle-double-up",
            layout=BUTTON_LAYOUT,
        )

        return ipw.VBox(
            layout={},
            children=[
                self.deselect_all,
                self.deselect,
            ],
        )
