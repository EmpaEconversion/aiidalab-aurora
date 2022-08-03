# -*- coding: utf-8 -*-

import ipywidgets as ipw


class PreviewResults(ipw.VBox):
    
    BOX_LAYOUT_1 = {'width': '50%'}
    BOX_STYLE = {'description_width': '15%'}
    BUTTON_STYLE = {'description_width': '30%'}
    BUTTON_LAYOUT = {'margin': '5px'}
    MAIN_LAYOUT = {'width': '100%', 'padding': '10px', 'border': 'solid blue 2px'}

    def __init__(self):
        
        # initialize widgets
        self.w_header_label = ipw.HTML(value="<h2>Results Visualization</h2>")
        self.w_select_job = ipw.Dropdown(
            description="Select Job ID:", value=None,
            options=['[25]  Conrad_commercial-1_cycling_20220628'],
            layout=self.BOX_LAYOUT_1, style={'description_width': 'initial'})

        with open("visualizer-example/Ewe_vs_t.png", "rb") as file:
            self.w_plot_1 = ipw.Image(
                value=file.read(),
                format='png', width=400)#, height=400)
        with open("visualizer-example/I_vs_t.png", "rb") as file:
            self.w_plot_2 = ipw.Image(
                value=file.read(),
                format='png', width=400)#, height=400)
        with open("visualizer-example/Q_vs_cn.png", "rb") as file:
            self.w_plot_3 = ipw.Image(
                value=file.read(),
                format='png', width=400)#, height=400)

        super().__init__()
        self.children = [
            self.w_header_label,
            self.w_select_job,
            ipw.HBox([
                self.w_plot_1,
                self.w_plot_2,
                self.w_plot_3,
            ], layout=self.MAIN_LAYOUT),
        ]

w_results = PreviewResults()
w_results