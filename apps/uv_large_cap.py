import yahoo_fin.stock_info as si
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.express as px



def undervalued_treemap():
    df = si.get_undervalued_large_caps()
    df['portfolio'] = "Undervalued Large Caps. Trailing P/E < 20, Price/Earnings to Growth < 1"
    df['MarketCap'] = df['Market Cap'].map(lambda x: x.split("B")[0]).astype(float)
    df['1d chg'] = df['% Change'].map(lambda x: x.split("%")[0]).astype(float)
    fig = px.treemap(df, path=['portfolio', 'Name'],
                     values='MarketCap', color='1d chg', color_continuous_scale='thermal')

    return dcc.Graph(figure=fig)

def undervalued_table():
    df = si.get_undervalued_large_caps()
    df.drop(['52 Week Range'], axis=1, inplace=True)
    df.sort_values(['PE Ratio (TTM)'], inplace=True)

    table_row = []
    for k, v in df.iterrows():
        url_string = 'https://finance.yahoo.com/quote/' + v['Symbol'] + '?p=' + v['Symbol']
        row = html.Tr([html.A(v['Symbol'], href=url_string),
                       html.Td(v['Name']),
                       html.Td(v['Price (Intraday)']),
                       html.Td(v['Change']),
                       html.Td(v['% Change']),
                       html.Td(v['Volume']),
                       html.Td(v['Avg Vol (3 month)']),
                       html.Td(v['Market Cap']),
                       html.Td(v['PE Ratio (TTM)']),
        ])
        table_row.append(row)

    table_body = [html.Tbody(table_row)]
    table_header = [
        html.Thead(html.Tr([
                   html.Th('Ticker'),
                   html.Th('Name'),
                   html.Th('Latest Price'),
                   html.Th('1d $ Change'),
                   html.Th('1d % Change'),
                   html.Th('Volume'),
                   html.Th('Avg. Vol (3M)'),
                   html.Th('Market Cap ($)'),
                   html.Th('P/E ratio (ttm)'),
                   ]))
        ]
    table = dbc.Table(table_header + table_body, striped=True, bordered=True, hover=True, size="sm",
                      style={'textAlign': 'center', 'font_family': 'cursive', 'font_size': '12px'})

    return table
layout = html.Div([
    html.H1('Research Ideas - Undervalued Large Cap Stocks', style={'textAlign': 'center'}),
    html.H5("Trailing P/E: 0 - 20, Price / Earnings to Growth (P/E/G): < 1"),

        undervalued_treemap(),
        undervalued_table(),

])