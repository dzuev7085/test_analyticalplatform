"""Module for a Plotly chart with line and bar."""
import base64
import plotly
import plotly.graph_objs as go
import plotly.io as pio
from django.utils.safestring import mark_safe
import pandas as pd
import numpy as np
import math
from datetime import timedelta


def pageviews_users(df, return_base64=False):
    """Create a bar chart and scatter.
    @param attribute: df (dataframe) dataframe containing the data
    @param attribute: return_base64 (bool): Whether to return the result as a
        base64 string or not.
    :returns: HTML or base64 string."""

    # Filter out users and pivot data
    df = df[~df.type.str.contains('users')]

    # Used to limit the chart date to the max and min of the data set
    min_date = df.index.min()
    max_date = min_date + timedelta(days=30)

    # Create a pivot table to aggregate data
    df = pd.pivot_table(
        df,
        values='value',
        index='date',
        columns='type',
        aggfunc=np.sum,
        fill_value=0,
    )

    # Fill in missing dates
    idx = pd.date_range(min_date, max_date)
    df = df.reindex(idx, fill_value=0)

    # Create a list of dates for the x-axis
    date_list = df.index

    # Calculate cumulative sum
    new = [df['events'].values[0]]
    for i in range(1, len(df.index)):
        new.append(new[i - 1] + df['events'].values[i])
    df['events_cumsum'] = new

    # Max value of all aggregated values
    max_value = df.select_dtypes(include=[np.number]).max().max()

    # Round max to nearest 100
    max_value = math.ceil(max_value/100)*100

    trace1 = go.Bar(
        x=date_list,
        y=df['unique_pageviews'],
        marker=dict(
            color='#CFD8DC',
        ),
        name='Page views (LHS)',
    )

    trace2 = go.Scatter(
        x=date_list,
        y=df['events_cumsum'],
        mode='markers',
        marker=dict(
            symbol='pentagon',
            size=6,
            color='#0D2E54',
        ),
        name='Cumulative number&nbsp;&nbsp;&nbsp;<br>of downloads (RHS)',
        yaxis='y2',
    )

    data = [
        trace1,
        trace2,
    ]

    layout = dict(
        font=dict(
            family='Aktiv Grotesk',
            size=11,
            color='#000000'),

        xaxis=dict(
            type='date',
            range=[min_date, max_date],
        ),

        annotations=[
            dict(
                textangle=-90,
                font=dict(
                    size=10,
                ),
                showarrow=False,
                x=-0.065,

                yanchor='bottom',
                y=0.815,

                xref='paper',
                yref='paper',
                text='Page views',
            ),
            dict(
                textangle=-90,
                font=dict(
                    size=10,
                ),
                showarrow=False,
                x=1.07,

                yanchor='bottom',
                y=0.815,

                xref='paper',
                yref='paper',
                text='Downloads',
            )
        ],

        yaxis=dict(
#            title='Page views',
            range=[0, max_value],
            anchor='free',
            position=0,
        ),

        yaxis2=dict(
            range=[0, max_value],
            anchor='x',
            rangemode='tozero',
            overlaying='y',
            side='right',
        ),

        autosize=False,
        width=700,  # 411
        height=300,  # 213
        margin=go.layout.Margin(
            l=40,  # noqa: E741
            r=80,
            b=40,
            t=15,
            pad=0
        ),
        legend=dict(
            x=0.72,
            y=0.93,
            # bgcolor='#E2E2E2',
        )
    )

    fig = dict(
        data=data,
        layout=layout,
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
