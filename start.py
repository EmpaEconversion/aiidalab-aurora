# -*- coding: utf-8 -*-

import ipywidgets as ipw

template = """
<h1> Aurora app </h1>
<h2>&clubs; <a title="Submit experiment" href="{appbase}/Aurora-app.ipynb" target="_blank">Submit Experiment</a></h1>
<h2>&clubs; <a title="Manage Samples" href="{appbase}/manage_samples.ipynb" target="_blank">Manage Samples</a></h2>
<h2>&clubs; <a title="Visualize Results" href="{appbase}/Results-visualizer.ipynb" target="_blank">Results visualizer</a></h2>
"""


def get_start_widget(appbase, jupbase, notebase):
    html = template.format(appbase=appbase, jupbase=jupbase, notebase=notebase)
    return ipw.HTML(html)


# EOF
