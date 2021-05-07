import dash_bootstrap_components as dbc
import dash_html_components as html
from modules.Portfolio import Portfolio
from babel.numbers import format_currency, format_percent

import plotly.express as px
import dash_core_components as dcc

port = Portfolio()
tbic = port.meeting_history()
glm = port.gain_from_last_meeting()
gains = glm.apply(lambda x: True
                  if x['cash_gain'] > 0 else False, axis =1)


stocks_cash = dbc.Card([
    dbc.CardBody(
        [
            html.H5("Portfolio", className="card-title"),
            html.P(
                "Number of Stocks: ",
                className="card-text"
            ),
            html.H4(str(glm.shape[0]), className="card-title text-right"),
            html.P(
                "Value of stocks: ",
                className="card-text"
            ),
            html.H4(str(format_currency(glm['Value'].sum(), 'GBP', locale='en_US')), className="card-title text-right"),
            html.P(
                "Cash Position: ",
                className="card-text"
            ),
            html.H4(str(format_currency(port.gbp_cash, 'GBP', locale='en_US')), className="card-title text-right"),
            html.P(
                "Total Value: ",
                className="card-text"
            ),
            html.H4(str(
                    format_currency(port.gbp_cash + glm['Value'].sum(), 'GBP', locale='en_US')), className="card-title text-right"),
            dbc.Button(
                "Portfolio View", color="success", className="mt-auto", href="/performance"
            ),
        ]
    ),],
color='primary', inverse=True
)

gain = dbc.Card([
    dbc.CardBody(
        [
            html.H5("Since last meeting", className="card-title"),
            html.P(
                "Gain (loss): ",
                className="card-text"
            ),
            html.H4(str(format_currency(glm['cash_gain'].sum(), 'GBP', locale='en_US')), className="card-title text-right"),
            html.P(
                "Monthly performance: ",
                className="card-text"
            ),
            html.H4(str(format_percent(100*(glm['Value'].sum() - glm['m1'].sum())/glm['m1'].sum(), format='#.##', locale='en_US')) + "%", className="card-title text-right"),
            html.P(
                "Stocks Gained: ",
                className="card-text"
            ),
            html.H4(len(gains[gains == True].index), className="card-title text-right"),
            html.P(
                "Stocks Declined: ",
                className="card-text"
            ),
            html.H4(len(gains[gains == False].index), className="card-title text-right"),
            dbc.Button(
                "Stock Ranking", color="success", className="mt-auto", href="/ranking"
            ),
        ]
    )],
color = 'primary', inverse = True
)
def generate_return(i):
    return html.P(children=str(port.top_3_gainers()['name'].to_list()[i].split(' ')[0]).title() + ": " + format_currency(
                    (port.top_3_gainers()['cash_gain'].to_list()[i]), 'GBP', locale='en_US'),
                    className="card-text")

def generate_loss(i):
    return html.P(children=str(port.top_3_losers()['name'].to_list()[i].split(' ')[0]).title() + ": " + format_currency(
                    (port.top_3_losers()['cash_gain'].to_list()[i]), 'GBP', locale='en_US'),
                    className="card-text")
winners = dbc.Card([
    dbc.CardBody(
        [
            html.H5("Biggest Sterling Gains", className="card-title"),
                dbc.Col(children=[generate_return(i) for i in range(0,10)]

                ),
        ]
    )],
    color='success', inverse='True'
)
losers = dbc.Card(
    dbc.CardBody(
        [
            html.H5("Biggest Sterling Declines", className="card-title"),
                dbc.Col(children=[generate_loss(i) for i in range(0,10)]

                ),
        ]
    )
)
bar_winners = dbc.Card([
    dbc.CardBody(
        dcc.Graph(figure=px.bar(port.bar_gainers(),
                                x=port.bar_gainers()['name'],
                                y=port.bar_gainers()['cash_gain'],
                                title='Gainers',
                                labels={'x': 'Stock', 'y': '£ Gain'})
                  , id='winners',)
    )],
    color='success', inverse='True'
)
bar_losers = dbc.Card([
    dbc.CardBody(
        dcc.Graph(figure=px.bar(port.bar_losers(),
                                x=port.bar_losers()['name'],
                                y=port.bar_losers()['cash_gain'],
                                title='Decliners',
                                labels={'x': 'Stock', 'y': '£ Loss'})
                  , id='winners')
    )],
    color='danger', inverse='True'
)
bar_currency = dbc.Card([
    dbc.CardBody(
        dcc.Graph(figure=px.bar(port.currency_performance(),
                                x=port.currency_performance().index.values,
                                y=port.currency_performance()['cash_gain'],
                                title='Currency Performance',
                                color_continuous_scale='Inferno',
                                labels={'x': 'Currency', 'y': '£ Gain / Loss'})
                  , id='winners')
    )],
    color='warning', inverse='True',
)
bar_style = dbc.Card([
    dbc.CardBody(
        dcc.Graph(figure=px.bar(port.style_performance(),
                                x=port.style_performance().index.values,
                                y=port.style_performance()['cash_gain'],
                                title='Stock Style Performance',
                                color_continuous_scale='Inferno',
                                labels={'x': 'Currency', 'y': '£ Gain / Loss'})
                  , id='winners')
    )],
    color='info', inverse='False'
)
bar_sector = dbc.Card([
    dbc.CardBody(
        dcc.Graph(figure=px.bar(port.sector_performance(),
                                x=port.sector_performance().index.values,
                                y=port.sector_performance()['cash_gain'],
                                title='Stock Sector Performance',
                                color_continuous_scale='Inferno',
                                labels={'x': 'Currency', 'y': '£ Gain / Loss'})
                  , id='winners')
    )],
    color='secondary', inverse='True'
)
top_deck = dbc.CardDeck([stocks_cash, gain, ])
layout = dbc.Container([
    html.H3("Headline performance"),
    dbc.Spinner(dbc.Row([
        dbc.Col([top_deck]),
        dbc.Col(bar_winners),
        dbc.Col(bar_losers),
    ],
    )),
    html.H3("Portfolio Gain / Loss Analysis"),
    dbc.Spinner(dbc.Row([
        dbc.Col(bar_currency),
        dbc.Col(bar_style),
        dbc.Col(bar_sector),
    ],
    )),


],fluid=True)