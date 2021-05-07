import yahoo_fin.stock_info as si
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from modules.Portfolio import Portfolio
from datetime import date, timedelta
from babel.numbers import format_currency

tbic = Portfolio()

def make_meeting_dict():
    meeting_dict = {}
    n = 0
    for yr in range(2018, 2026):
        for mth in range(1, 13):
            meeting = [yr, mth]
            meeting_dict[n] = meeting
            n += 1

    return meeting_dict

def third_friday(year, month):
    """Return datetime.date for monthly option expiration given year and
    month
    """
    # The 15th is the lowest third day in the month
    third = datetime.date(year, month, 15)
    # What day of the week is the 15th?
    w = third.weekday()
    # Friday is weekday 4
    if w != 4:
        # Replace just the day (of month)
        third = third.replace(day=(15 + (4 - w) % 7))
    return third

def composition_table():
    port = tbic.gain_from_last_meeting()
    display = port[['ticker', 'name', 'Qty', 'currency_x', 'quote', 'Value', 'sector', 'stock_style', 'm1',  'm2', 'm3', 'm4', 'm5', 'm6', 'm7']]
    meeting_num = port['meeting_num'].to_list()[0]
    meeting_dict = make_meeting_dict()

    display.sort_values(['Value'], inplace=True, ascending=False)
    table_row = []
    for k, v in display.iterrows():
        if v['currency_x'] == 'GBP':
            v['quote'] = v['quote'] / 100
        url_string = 'https://finance.yahoo.com/quote/' + v['ticker'] + '?p=' + v['ticker']
        stock_string = '/stock_history/' + v['ticker']
        row = html.Tr([html.A(v['ticker'], href=url_string),
                       html.Td(v['Qty']),
                      html.A(v['name'], href=stock_string),
                      html.Td(v['currency_x']),
                      html.Td(format_currency(v['quote'], v['currency_x'], locale='en_US')),
                      html.Td(format_currency(v['Value'], 'GBP', locale='en_US')),
                      html.Td(v['sector']),
                      html.Td(v['stock_style']),
                      html.Td(format_currency(v['m1'], 'GBP', locale='en_US')),
                       html.Td(format_currency(v['m2'], 'GBP', locale='en_US')),
                       html.Td(format_currency(v['m3'], 'GBP', locale='en_US')),
                       html.Td(format_currency(v['m4'], 'GBP', locale='en_US')),
                       html.Td(format_currency(v['m5'], 'GBP', locale='en_US')),
                       html.Td(format_currency(v['m6'], 'GBP', locale='en_US')),
                       html.Td(format_currency(v['m7'], 'GBP', locale='en_US')),
                      ])
        table_row.append(row)

    table_body = [html.Tbody(table_row)]
    table_header = [
        html.Thead(html.Tr([html.Th('Symbol'),
                    html.Th('Position'),
                   html.Th('Company'),
                   html.Th('CCY'),
                   html.Th('Latest quote'),
                   html.Th('Position Value'),
                   html.Th('Sector'),
                   html.Th('Style'),
                   html.Th(str(meeting_dict[meeting_num][0]) + "-" + str(meeting_dict[meeting_num][1])),
                    html.Th(str(meeting_dict[meeting_num-1][0]) + "-" + str(meeting_dict[meeting_num-1][1])),
                    html.Th(str(meeting_dict[meeting_num-2][0]) + "-" + str(meeting_dict[meeting_num-2][1])),
                    html.Th(str(meeting_dict[meeting_num-6][0]) + "-" + str(meeting_dict[meeting_num-6][1])),
                    html.Th(str(meeting_dict[meeting_num-12][0]) + "-" + str(meeting_dict[meeting_num-12][1])),
                    html.Th(str(meeting_dict[meeting_num-18][0]) + "-" + str(meeting_dict[meeting_num-18][1])),
                    html.Th(str(meeting_dict[meeting_num-24][0]) + "-" + str(meeting_dict[meeting_num-24][1])),
                ]))
        ]

    table = dbc.Table(table_header + table_body, striped=True, bordered=True, hover=True, size="sm",
                      style={'font_family': 'cursive', 'font_size': '12px'})


    return table

currency = dcc.Graph(id='currency-pie', figure=px.pie(tbic.gain_from_last_meeting().groupby(['currency_x']).sum(),title='Currency', values='weight', names=tbic.gain_from_last_meeting().groupby(['currency_x']).sum().index))
sector = dcc.Graph(id='owner-pie', figure=px.pie(tbic.gain_from_last_meeting().groupby(['sector']).sum(), title='Sector', values='weight', names=tbic.gain_from_last_meeting().groupby(['sector']).sum().index))
style = dcc.Graph(id='owner-pie', figure=px.pie(tbic.gain_from_last_meeting().groupby(['stock_style']).sum(), title='Style', values='weight', names=tbic.gain_from_last_meeting().groupby(['stock_style']).sum().index))

layout = html.Div([
    html.H2("Portfolio Composition"),
    dbc.Row([
        dbc.Col(currency, width=3),
        dbc.Col(sector, width=4),
        dbc.Col(style, width=4),
    ]),
    html.H5("Current and historic GBP Position Values"),
    html.P("For any historical valuations prior to us purchasing a particular stock, the position value is fixed at the meeting at which we bought that stock"),
    dbc.Row(composition_table())

])