import ipywidgets as ipw


class InputPreviewView(ipw.Output):
    """docstring"""

    def __init__(self) -> None:
        """docstring"""

        self.protocols = ipw.Tab(layout={
            "min_height": "350px",
            "max_height": "350px",
        })

        self.settings = ipw.Output(
            layout={
                "flex": "1",
                "margin": "2px",
                "border": "solid darkgrey 1px",
                "overflow_y": "auto",
            })

        self.monitors = ipw.Output(
            layout={
                "flex": "1",
                "margin": "2px",
                "border": "solid darkgrey 1px",
                "overflow_y": "auto",
            })

        super().__init__(layout={"margin": "0 0 10px"})
