# -*- coding: utf-8 -*-

import ipywidgets as ipw

template = """
<h1>&clubs; <a title="Launch Aurora app" href="{appbase}/Aurora-app.ipynb" target="_blank">Aurora app</a></h1>
<h2>&clubs; <a title="Visualize Results" href="{appbase}/Results-visualizer.ipynb" target="_blank">Results visualizer</a></h2>
"""


def get_start_widget(appbase, jupbase, notebase):
    html = template.format(appbase=appbase, jupbase=jupbase, notebase=notebase)
    return ipw.HTML(html)


# EOF
