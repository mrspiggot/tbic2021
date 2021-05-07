from pathlib import Path
from app import app
from app import cache
from app import server
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import sqlalchemy
import pandas as pd
from PIL import Image
import plotly.graph_objects as go
#from apps import portfolio, currency, owner, stype, sector, research, semple_slicer, bubble, region, country
from apps import home, portfolio, ranking, sector, stype, currency, owner, sempleSlicer, uv_large_cap, most_shorted, ag_small_cap, uv_growth_stocks, composition, stock_history, bubble, region, country

cwd = Path.cwd()


img = Image.open(cwd.joinpath('assets/Clear Bear.png'))

covid_dropdown = dbc.DropdownMenu(
    children=[
        dbc.DropdownMenuItem("Oxford Bubble Chart", href='/bubble'),
        dbc.DropdownMenuItem("Oxford Index", href='https://player.vimeo.com/video/463163595'),
        dbc.DropdownMenuItem(divider=True),
        dbc.DropdownMenuItem("Country Comparison", href='/ox_country'),
        dbc.DropdownMenuItem("Region Comparison", href='/ox_region'),
        ],
    nav=True,
    in_navbar=True,
    label="C-19",
)
research_dropdown = dbc.DropdownMenu(
    children=[
        dbc.DropdownMenuItem("Undervalued Large Caps", href='/uv_large_cap'),
        dbc.DropdownMenuItem("Most Shorted Stocks", href='/most_shorted'),
        dbc.DropdownMenuItem("Aggressive Small Caps", href='/ag_small_cap'),
        dbc.DropdownMenuItem("Undervalued Growth Stocks", href='/uv_growth_stock'),
        ],
    nav=True,
    in_navbar=True,
    label="Research",
)
heatmap_dropdown = dbc.DropdownMenu(
    children=[
        dbc.DropdownMenuItem("Sector", href='/sector'),
        dbc.DropdownMenuItem("Stock Type", href='/stype'),
        dbc.DropdownMenuItem("Currency", href='/currency'),
        dbc.DropdownMenuItem("Owner", href='/owner'),
        ],
    nav=True,
    in_navbar=True,
    label="Heatmaps",
)
navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=img, height="90px")),
                        dbc.Col(dbc.NavbarBrand("TBIC Dashboard", className="ml-2")),
                    ],
                    align="center",
                    no_gutters=True,
                ),
                href="/",
            ),
            dbc.NavbarToggler(id="navbar-toggler2"),
            dbc.Collapse(
                dbc.Nav(
                    [dbc.NavItem(dbc.NavLink("Intra-Month Performance", href="/performance", disabled=False)),
                     dbc.NavItem(dbc.NavLink("Composition", href="/composition")),
                     dbc.NavItem(dbc.NavLink("Semple's Scimitar", href="/semple")),
                     heatmap_dropdown,
                     research_dropdown,
                     covid_dropdown,
                     ], className="ml-auto", navbar=True
                ),
                id="navbar-collapse2",
                navbar=True,
            ),

        ]
    ),
    color="dark",
    dark=True,
    className="mb-5",
)
CONTENT_STYLE = {
    "margin-left": "2rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}
app.layout = html.Div([
    dcc.Location(id='page-url'),
    html.Div([
        navbar,
    ]),
    html.Div(id='page-content', children=[]),
],
style=CONTENT_STYLE)

@app.callback(Output('page-content', 'children'),
              [Input('page-url', 'pathname')], prevent_initial_call=True)
#@cache.memoize(timeout=20)
def display_page(pathname):
    if pathname == '/performance':
        return portfolio.layout
    if pathname == '/ranking':
        return ranking.layout
    if pathname == '/sector':
        return sector.layout
    if pathname == '/stype':
        return stype.layout
    if pathname == '/currency':
        return currency.layout
    if pathname == '/owner':
        return owner.layout
    if pathname == '/uv_large_cap':
        return uv_large_cap.layout
    if pathname == '/uv_growth_stock':
        return uv_growth_stocks.layout
    if pathname == '/ag_small_cap':
        return ag_small_cap.layout
    if pathname == '/most_shorted':
        return most_shorted.layout
    if pathname == '/semple':
        return sempleSlicer.layout
    if pathname == '/composition':
        return composition.layout
    if pathname == '/bubble':
        return bubble.layout
    if pathname == '/ox_country':
        return country.layout
    if pathname == '/ox_region':
        return region.layout
    if pathname[0:15] == '/stock_history/':
        ticker = pathname[15:]
        chart = stock_history.ohlc_chart(ticker)
        table = stock_history.peers_table(ticker)
        return dcc.Loading(dcc.Graph(figure=chart), type='graph'), html.H5("Key valuation  measures versus peers"), dcc.Loading(table, type='cube')
    else:
        return home.layout

if __name__ == '__main__':
    app.run_server(debug=True)