import ipywidgets as ipw

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

BUTTON_LAYOUT = {"width": "fit-content", "margin": "2px 2px 2px auto"}

PREVIEW_LAYOUT = {
    "width": "50%",
    "max_height": "338px",
    "margin": "2px",
    "border": "solid darkgrey 1px",
}

MAIN_LAYOUT = {
    "width": "auto",
    "margin": "2px",
    "padding": "10px",
    "border": "solid darkgrey 1px"
}


class ProtocolSelectorView(ResettableView):
    """The protocol selection view."""

    def __init__(self) -> None:
        """`ProtocolSelectorView` constructor."""

        super().__init__(
            layout=MAIN_LAYOUT,
            children=[
                self.__build_selection_container(),
                self.reset,
            ],
        )

    ###########
    # PRIVATE #
    ###########

    def __build_selection_container(self) -> ipw.HBox:
        """Build the protocol selection section.

        Includes widgets for protocol (de)selection and preview.

        Returns
        -------
        `ipw.HBox`
            A container of protocol selection widgets.
        """

        self.preview = ipw.Output(layout=PREVIEW_LAYOUT)

        return ipw.HBox(
            layout={},
            children=[
                ipw.VBox(
                    layout={
                        "width": "50%",
                    },
                    children=[
                        self.__build_selection_section(),
                        self.__build_selected_section(),
                    ],
                ),
                self.preview,
            ],
        )

    def __build_selection_section(self) -> ipw.HBox:
        """Build a container for protocol selection including
        controls.

        Returns
        -------
        `ipw.HBox`
            A container for protocol selection widgets.
        """

        self.selector = ipw.Select(
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
                            value="Protocol:",
                            layout={},
                        ),
                        self.__build_selection_controls(),
                    ],
                ),
                self.selector,
            ],
        )

    def __build_selection_controls(self) -> ipw.VBox:
        """Build a container of protocol selection controls widgets.

        Returns
        -------
        `ipw.VBox`
            A container of protocol selection control widgets.
        """

        self.select = ipw.Button(
            description="",
            button_style="",
            tooltip="Select chosen protocol",
            icon="fa-angle-down",
            layout=BUTTON_LAYOUT,
        )

        self.select_all = ipw.Button(
            description="",
            button_style="",
            tooltip="Select all protocols",
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
        """Build a container for protocol deselection including
        controls.

        Returns
        -------
        `ipw.VBox`
            A container for protocol deselection widgets.
        """

        self.selected = ipw.Select(
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
        """Build a container of protocol deselection controls
        widgets.

        Returns
        -------
        `ipw.VBox`
            A container of protocol deselection control widgets.
        """

        self.deselect = ipw.Button(
            description="",
            button_style="",
            tooltip="Deselect chosen protocol",
            icon="fa-angle-up",
            layout=BUTTON_LAYOUT,
        )

        self.deselect_all = ipw.Button(
            description="",
            button_style="",
            tooltip="Deselect all protocols",
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
