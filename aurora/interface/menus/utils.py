from ipywidgets import HTML, VBox

from aurora import __version__


def get_header_box(section_title: str) -> VBox:
    """Return the app's header box reflecting the current section's
    title.

    Parameters
    ----------
    `section_title` : `str`
        The title of the current section.

    Returns
    -------
    `ipywidgets.VBox`
        The header box with the current section's title.
    """

    return VBox(
        [
            HTML(value=f"""
                <h1>Aurora - {section_title}</h1>
                <p>Aurora app version {__version__}</p>
            """),
        ],
        layout={
            'width': '100%',
            'border': 'solid black 4px',
            'padding': '10px'
        },
    )
