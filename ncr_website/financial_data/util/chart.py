"""Module to generate charts."""
import plotly
import plotly.graph_objs as go
from gui.templatetags.financial_statement import reverse_escape_slash
from gui.const import COLOR_LIST
from issuer.models import Issuer


FONT_HEADER_ATTR = dict(
    family='Activ Grotesk',
    color='#000000',
    size=16,
)

FONT_ATTR = dict(
    family='Activ Grotesk',
    color='#000000',
    size=12,
)


def peer_horizontal_bar_chart(self, hoverformat, df, issuer_id):
    """Return a horizontal bar chart"""

    # Get last row of data frame
    df = df.tail(1).reset_index()

    # And remove the pivoty look of the table
    df = df.set_index('Date').stack().reset_index(
        name='Value').rename(columns={'LEI': 'Company'})

    # Order so that largest values are on top
    df = df.sort_values(by=['Value'])

    # Highlight the issuer we're looking into
    target_name = Issuer.objects.get(pk=issuer_id)
    color_list = []
    for index, row in df.iterrows():
        if row['Company'] == target_name.short_name:
            color_list.append('#C5A653')
        else:
            color_list.append('#0d2e54')

    data = []
    data.append(
        go.Bar(
            x=df['Value'].values.tolist(),
            y=df['Company'].values.tolist(),
            orientation='h',
            marker=dict(color=color_list)
        )
    )

    # Todo: annotate header
    layout = go.Layout(
        title="Peer comparison | {}".format(
            reverse_escape_slash(self.kwargs['readable_name'])
        ),
        xaxis=go.layout.XAxis(
            hoverformat=hoverformat,
            exponentformat=None,
            tickformat=hoverformat,
        ),
        font=FONT_ATTR,
        titlefont=FONT_HEADER_ATTR,
        separators='.',
        margin=go.layout.Margin(
            l=140,  # noqa: E741
            b=40,
        ),
    )

    fig = go.Figure(
        data=data,
        layout=layout,
    )

    # Generate the HTML
    div = plotly.offline.plot(
        fig,
        output_type='div',
        show_link=False,
        config=dict(
            displaylogo=False,
            modeBarButtonsToRemove=['sendDataToCloud']
        )
    )

    return div


def peer_grouped_bar_chart(self, hoverformat, df):
    """Return a grouped bar chart"""

    # Create a list of dates for the X-axis
    x_axis = [d.strftime('%Y-%m-%d') + '' for d in df.index.values.tolist()]

    data = []

    # Loop through all columns in data frame and append to chart
    for i, column in enumerate(df):
        data.append(
            go.Bar(
                x=x_axis,
                y=df[column].values.tolist(),

                # Name of company
                name=column,

                # Pick a color from the list of allowed colors above
                marker=dict(color=COLOR_LIST[i]),
                hoverlabel=dict(namelength=-1),
            )
        )

    layout = go.Layout(
        barmode='group',
        title="Peer comparison | {}".format(
            reverse_escape_slash(self.kwargs['readable_name'])
        ),
        font=FONT_ATTR,
        titlefont=FONT_HEADER_ATTR,
        xaxis=go.layout.XAxis(
            ticktext=x_axis,
            tickvals=x_axis
        ),
        yaxis=dict(
            title='Money unit',
            titlefont=dict(
                color='#000000'
            ),
            tickfont=dict(
                color='#000000'
            ),
            hoverformat=hoverformat,
        ),
    )

    # Generate the chart object
    fig = go.Figure(
        data=data,
        layout=layout)

    # Generate the HTML
    div = plotly.offline.plot(
        fig,
        output_type='div',
        show_link=False,
        config=dict(
            displaylogo=False,
            modeBarButtonsToRemove=['sendDataToCloud']
        )
    )

    return div
