import pandas as pd
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from datetime import date, timedelta
from modules.Portfolio import Portfolio
import yahoo_fin.stock_info as si
from dash.dependencies import Input, Output
from app import app

slider_dict = {1: '1m', 2: "2m", 3: '3m', 4: '4m', 5: '5m', 6: '6m'}


def order(A):
    if len(A) != len(set(A)):
        return 'Neither'
    elif A == sorted(A,reverse=False):
        return 'Ascending'
    elif A == sorted(A,reverse=True):
        return 'Descending'
    else:
        return 'Neither'

layout = dbc.Container([
    html.H4(
        'Shares in decline - These shares are below their value at the last meeting, and have declined at each of the previous "n" meetings',
        style={'textAlign': 'center'}),
    dbc.Row([
        dbc.Col(
            dcc.Slider(min=1, max=6, marks=slider_dict, id="semple-slider", value=3),

        ),
        dbc.Col(html.H6('Move Slider to extend / shorten the meeting lookback window (i.e. change "n")'),

                ),
    ]),

    dbc.Row([
            dbc.Col(
                dcc.Loading(
                    html.Div(id='page-semple', children=[]),fullscreen=True, type='circle'
            )
        )
    ])


])

@app.callback(Output('page-semple', 'children'),
              [Input('semple-slider', 'value')])
def semple_table(svalue):
    port = Portfolio()
    tbic = port.gain_from_meeting(0)

    today = date.today()
    six_m = today - timedelta(days=svalue*30)
    layout_rows = []
    for index, row in tbic.iterrows():
        perf = [row['Value']]
        perf += row[3:3+svalue].to_list()
        if order(perf) == "Ascending":
            df = si.get_data(row.ticker, six_m, today)
            if row['ticker'][-2:] == '.L':
                df = df.drop(pd.Timestamp('2021-04-13 00:00:00'))

            if row['ticker'] == 'CCL.L':
                df = df.drop(pd.Timestamp('2021-04-21 00:00:00'))

            chart = go.Figure(data=go.Candlestick(x=df.index,
                            open=df['open'],
                            high=df['high'],
                            low=df['low'],
                            close=df['adjclose']),
                            )
            chart.update_layout(title=str(row.ticker) + " share price", yaxis_title=row.currency_x, xaxis_title="Date")
            candle = dcc.Graph(figure=chart)

            row = dbc.Card(candle)
            layout_rows.append(row)

    return layout_rows