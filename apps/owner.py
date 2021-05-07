import sqlalchemy
import pandas as pd
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from app import app
from forex_python.converter import CurrencyRates
from pathlib import Path
import plotly.express as px
from modules.Portfolio import Portfolio
from dash.dependencies import Input, Output, State



c = CurrencyRates()
rates = c.get_rates('GBP')
rates.update({'GBp': 100.0})
cwd = Path.cwd()
slider_dict = {1: '1m', 2: "2m", 3: '3m', 4: '6m', 5: '1Y', 6: '2Y'}
meeting_list = [0,0,1,2,5,11,23]


layout = html.Div([
    html.H1('TBIC Performance Heatmap by Stock Owner', style={'textAlign': 'center'}),
    dbc.Row([
        dbc.Col(
            dcc.Slider(min=0, max=6, marks=slider_dict, id="owner-treemap-slider", value=0),
            width=7, lg={'size': 6,  "offset": 0, 'order': 'first'}
        ),
        dbc.Col(html.H5('Move Slider to see gains (losses) over different timeframes'),
            width=4, lg={'size': 6,  "offset": 0, 'order': 'first'}),
    ]),
    dbc.Spinner(dcc.Graph(id='owner-treemap', figure = {}), color='primary'),
])
@app.callback(Output('owner-treemap', 'figure'),
              [Input('owner-treemap-slider', 'value')])
def currency_treemap(value):
    tbic = Portfolio()
    tbic_port = tbic.gain_from_meeting(value)
    tbic_port.round(2)
    tbic_port["portfolio"] = "The TBIC Portfolio - By Owner"
    fig = px.treemap(tbic_port, path=['portfolio', 'owner', 'currency_x', 'stock_style', 'sector', 'industry', 'name'],
                     values='Value', color='%_gain', color_continuous_scale='thermal',
                     height=800)

    return fig

