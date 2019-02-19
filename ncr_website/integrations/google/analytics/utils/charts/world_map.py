"""Module for a Plotly world map."""
import base64
import plotly
import plotly.graph_objs as go
import plotly.io as pio
from django.utils.safestring import mark_safe


def world_map(df, return_base64=False):
    """Create a world map.
    @param attribute: df (dataframe) dataframe containing the data
    @param attribute: return_base64 (bool): Whether to return the result as a
        base64 string or not.
    :returns: HTML or base64 string."""

    # Limit data to page views
    df = df[~df.type.str.contains('users')]

    scl = [[0.0, '#C5A653'],
           [0.2, '#C5A653'],
           [0.4, '#C5A653'],
           [0.6, '#C5A653'],
           [0.8, '#C5A653'],
           [1.0, '#C5A653']]

    data = [
        dict(
            type='choropleth',
            locations=df['country_iso_code'],
            z=df['value'],
            text=df['country'],
            colorscale=scl,
            showscale=False,
        )
    ]

    layout = dict(
        geo=dict(
            showframe=False,
            showcoastlines=False,
            showcountries=True,
            projection=dict(
                type='equirectangular'
            )
        ),
        autosize=False,
        width=700,
        height=300,
        margin=go.layout.Margin(
            l=0,  # noqa: E741
            r=0,
            b=0,
            t=0,
            pad=0
        ),
    )

    fig = dict(
        data=data,
        layout=layout
    )

    if return_base64:
        img = pio.to_image(
            fig,
            format='svg',
        )
        data = "data:image/svg;base64," + base64.b64encode(img).decode('utf8')
    else:
        # Generate the HTML
        data = plotly.offline.plot(
            fig,
            output_type='div',
            show_link=False,
            config=dict(
                displaylogo=False,
                modeBarButtonsToRemove=['sendDataToCloud']
            )
        )

    return mark_safe(data)
