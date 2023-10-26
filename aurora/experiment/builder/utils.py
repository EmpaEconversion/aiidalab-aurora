import ipywidgets as ipw

BUTTON_LAYOUT = {
    "width": "fit-content",
    "margin": "2px 2px 2px auto",
}


class ResettableView(ipw.VBox):
    """An `ipw.VBox` with a reset button."""

    reset = ipw.Button(
        layout=BUTTON_LAYOUT,
        button_style="warning",
        icon="refresh",
        tooltip="Clear selection",
    )
