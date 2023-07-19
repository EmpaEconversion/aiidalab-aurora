import ipywidgets as ipw

TEMPLATE = """
<h1 style="text-align: center;">
    <a
        title="Aurora"
        href="{appbase}/aurora.ipynb"
        target="_blank"
    >
        &clubs; Aurora &clubs;
    </a>
</h1>
"""


def get_start_widget(appbase, jupbase, notebase):
    html = TEMPLATE.format(appbase=appbase)
    return ipw.HTML(html)
