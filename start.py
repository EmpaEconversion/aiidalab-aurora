# -*- coding: utf-8 -*-

import ipywidgets as ipw

template = """
<h1><a title="Launch Aurora app" href="{appbase}/Aurora-app.ipynb" target="_blank">Aurora app</a></h1>
"""


def get_start_widget(appbase, jupbase, notebase):
    html = template.format(appbase=appbase, jupbase=jupbase, notebase=notebase)
    return ipw.HTML(html)


# EOF
