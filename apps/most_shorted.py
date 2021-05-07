import yahoo_fin.stock_info as si
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.express as px
import pandas as pd



def shorted_treemap():
    d = {'M': '*0.001', 'B': ''}
    df = pd.read_html('https://finance.yahoo.com/screener/predefined/most_shorted_stocks')[0]
    df['portfolio'] = "Most shorted stocks, Avg 3m Volume Greater than 300,000"
    df['Market Cap'] = [float(n[:-1])/1000 if n[-1:] == 'M' else float(n[:-1]) for n in df['Market Cap']]
    df['1d chg'] = df['% Change'].map(lambda x: x.split("%")[0]).astype(float)
    fig = px.treemap(df, path=['portfolio', 'Name'],
                     values='Market Cap', color='1d chg', color_continuous_scale='thermal')

    return dcc.Graph(figure=fig)

def shorted_table():
    df = pd.read_html('https://finance.yahoo.com/screener/predefined/most_shorted_stocks')[0]
    df.drop(['52 Week Range'], axis=1, inplace=True)
    df['Market Cap'] = [float(n[:-1])/1000 if n[-1:] == 'M' else float(n[:-1]) for n in df['Market Cap']]
    df['Market Cap'] = df['Market Cap'].astype(float)
    df.sort_values(['Market Cap'], ascending=False, inplace=True)
    df = df.round(3)
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
                   html.Th('Market Cap ($Bn)'),
                   html.Th('P/E ratio (ttm)'),
                   ]))
        ]
    table = dbc.Table(table_header + table_body, striped=True, bordered=True, hover=True, size="sm",
                      style={'textAlign': 'center', 'font_family': 'cursive', 'font_size': '12px'})

    return table
layout = html.Div([
    html.H1('Research Ideas - Most Shorted Large & Medium Cap Stocks', style={'textAlign': 'center'}),

        shorted_treemap(),
        shorted_table(),

])