import ipywidgets as ipw

from .builder.view import ExperimentBuilderView

SUBMISSION_OUTPUT_LAYOUT = {
    "margin": "0 0 0 80px",
    "max_height": "500px",
    "overflow_y": "auto",
}

SUBMISSION_BOX_LAYOUT = {
    "width": "380px",
}

SUBMISSION_LINE_LAYOUT = {
    "width": "auto",
}

SUBMISSION_LINE_STYLE = {
    "description_width": "75px",
}

BUTTON_LAYOUT = {
    "width": "fit-content",
}


class ExperimentView(ipw.VBox):
    """docstring"""

    def __init__(self, builder: ExperimentBuilderView) -> None:
        """docstring"""

        self.builder = builder
        self.submission_output = ipw.Output(layout=SUBMISSION_OUTPUT_LAYOUT)

        super().__init__(
            layout={},
            children=[
                self.builder,
                self.__build_submission_controls(),
                self.submission_output,
            ],
        )

    ###########
    # PRIVATE #
    ###########

    def __build_submission_controls(self) -> ipw.VBox:
        """Build submission controls widgets."""

        self.unlock_when_done = ipw.Checkbox(
            style=SUBMISSION_LINE_STYLE,
            description="Unlock when done?",
            value=False,
        )

        self.experiment_group_label = ipw.Text(
            layout=SUBMISSION_LINE_LAYOUT,
            style=SUBMISSION_LINE_STYLE,
            description="Group label:",
            placeholder="Enter a group label (default: yymmdd-hhmmss)",
        )

        self.code = ipw.Dropdown(
            layout={"flex": "1"},
            style=SUBMISSION_LINE_STYLE,
            description="Select code:",
        )

        self.submit = ipw.Button(
            layout=BUTTON_LAYOUT,
            button_style="success",
            tooltip="Submit the experiment",
            icon="play",
            disabled=True,
        )

        self.reset = ipw.Button(
            layout=BUTTON_LAYOUT,
            button_style="danger",
            tooltip="Start over",
            icon="times",
        )

        return ipw.VBox(
            layout=SUBMISSION_BOX_LAYOUT,
            children=[
                self.unlock_when_done,
                self.experiment_group_label,
                ipw.HBox(
                    layout=SUBMISSION_LINE_LAYOUT,
                    children=[
                        self.code,
                        self.submit,
                        self.reset,
                    ],
                ),
            ],
        )
