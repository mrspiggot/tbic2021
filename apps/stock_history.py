from app import engine
from datetime import date, timedelta
import pandas as pd
import plotly.graph_objects as go
import yahoo_fin.stock_info as si
import dash_html_components as html
import dash_bootstrap_components as dbc

def ohlc_chart(ticker):
    today = date.today()
    two_years_ago = today - timedelta(days=730)
    df = pd.read_sql("select * from stock_quotes where index > '" + str(two_years_ago) + "' and ticker = '" + str(ticker) + "'", engine)
    df.reset_index(inplace=True)
    df = df.rename(columns={'index': 'date'})
    currency = df['currency'].to_list()[0]
    chart = go.Figure(data=go.Candlestick(x=df.date,
                                          open=df['open'],
                                          high=df['high'],
                                          low=df['low'],
                                          close=df['adjclose']),
                      )
    chart.update_layout(title=str(ticker) + " share price", yaxis_title=currency, xaxis_title="Date")
    return chart

def peers_table(ticker):
    peers = pd.read_sql("select peers from peers where ticker = '" + str(ticker) + "'", engine)['peers'].to_list()
    val_stats = []
    for peer in peers:
        try:
            df = si.get_stats_valuation(peer)
            cols = df.iloc[:, 0].to_list()
            cols.insert(0, 'ticker')
            stat = df.iloc[:,1].to_list()
            stat.insert(0, peer)
            val_stats.append(stat)
        except Exception as e:
            print(e)

    df = pd.DataFrame(val_stats, columns=cols)

    table_row = []
    for k, v in df.iterrows():
        url_string = 'https://finance.yahoo.com/quote/' + v['ticker'] + '?p=' + v['ticker']
        row = html.Tr([html.A(v['ticker'], href=url_string),
           html.Td(v['Trailing P/E']),
           html.Td(v['Forward P/E 1']),
           html.Td(v['PEG Ratio (5 yr expected) 1']),
           html.Td(v['Price/Sales (ttm)']),
           html.Td(v['Price/Book (mrq)']),
           html.Td(v['Enterprise Value/Revenue 3']),
           html.Td(v['Enterprise Value/EBITDA 7']),
           ])
        table_row.append(row)

    table_body = [html.Tbody(table_row)]
    table_header = [
        html.Thead(html.Tr([html.Th('Symbol'),
                            html.Th('Trailing P/E'),
                            html.Th('Forward P/E'),
                            html.Th('PEG (Price/Earnings:Growth) Ratio'),
                            html.Th('Price:Sales'),
                            html.Th('Price:Book'),
                            html.Th('Enterprise Value:Revenue'),
                            html.Th('Enterprise Value:Earnings'),
            ]))
    ]

    table = dbc.Table(table_header + table_body, striped=True, bordered=True, hover=True, size="sm",
                      style={'font_family': 'cursive', 'font_size': '12px'})


    return table
