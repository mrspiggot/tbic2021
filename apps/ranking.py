from modules.Portfolio import Portfolio
import dash_html_components as html
import plotly.express as px
import dash_core_components as dcc
import dash_table
from babel.numbers import format_currency, format_decimal


def portfolio_chart():
    tbic = Portfolio()
    tbic_port = tbic.gain_from_last_meeting()
    tbic_port.sort_values(['cash_gain'], ascending=False, inplace=True)

    fig = px.bar(tbic_port, x=tbic_port['name'], y=tbic_port['cash_gain'])

    return dcc.Graph(figure=fig)

def portfolio_table():
    tbic = Portfolio()
    df = tbic.gain_from_last_meeting()
    df_display = df[['symbol', 'name', 'Qty', 'currency_x', 'quote', 'sector', 'industry', 'stock_style', 'owner', 'Value', 'cash_gain', '%_gain', 'currency_y']]
    df_display.loc[df_display['currency_x'] == 'GBP', ['currency_x']] = 'GBp'
    df_display.sort_values(['cash_gain'], ascending=False, inplace=True)


    for index, row in df_display.iterrows():
        df_display._set_value(index, 'Quote', format_currency(row['quote'], row['currency_x'], locale='en_US'))
        df_display._set_value(index, 'value', format_currency(row['Value'], 'GBP', locale='en_US'))
        df_display._set_value(index, 'Gain(£)', format_currency(row['cash_gain'], 'GBP', locale='en_US'))
        df_display._set_value(index, 'Gain(%)', format_decimal(row['%_gain'], format='#,##0.##;-#', locale='en_US'))

    df_display = df_display[['symbol', 'name', 'Qty', 'currency_x', 'Quote', 'sector', 'industry', 'stock_style', 'owner', 'value', 'Gain(£)', 'Gain(%)']]
    df_display.rename(columns={'symbol':'Symbol', 'name': 'Name', 'currency_x': 'Currency', 'Qty': 'Position', 'sector': 'Sector', 'industry': 'Industry', 'stock_style': 'Type', 'owner': 'Owner', 'value': '£ Value'}, inplace=True)

    return dash_table.DataTable(id='data-table',
                                columns=[{"name": i, "id": i} for i in df_display.columns],
                                data=df_display.to_dict('records'),# the contents of the table
        editable=True,              # allow editing of data inside all cells
        filter_action="native",     # allow filtering of data by user ('native') or not ('none')
        sort_action="native",       # enables data to be sorted per-column by user or not ('none')
        sort_mode="single",         # sort across 'multi' or 'single' columns
        column_selectable="multi",  # allow users to select 'multi' or 'single' columns
        row_selectable="multi",     # allow users to select 'multi' or 'single' rows
        row_deletable=True,         # choose if user can delete a row (True) or not (False)
        selected_columns=[],        # ids of columns that user selects
        selected_rows=[],           # indices of rows that user selects
        page_action="native",       # all data is passed to the table up-front or not ('none')
        page_current=0,             # page number that user is on
        page_size=32,                # number of rows visible per page
        style_cell={                # ensure adequate header width when text is shorter than cell's text
            'width': '{}%'.format(len(df.columns)),
            'textOverflow': 'ellipsis',
            'overflow': 'hidden'
        },
        style_cell_conditional=[    # align text columns to left. By default they are aligned to right
            {
                'if': {'column_id': c},
                'textAlign': 'right',
                'width': '300px',
            }
            for c in ['Symbol', 'Currency', 'Position', 'Owner', 'Quote', 'Value', 'Gain(£)', 'Gain(%)']

        ],
        style_data={                # overflow cells' content into multiple lines
            'whiteSpace': 'normal',
            'height': 'auto'
        }

    )

layout = html.Div([
    html.H4('Stock gains (losses) since last meeting', style={'textAlign': 'center'}),

        portfolio_chart(),
        html.H4('Table of Stocks: Initially ordered by £GBP gain since last meeting'),
        html.P('Columns may be sorted and filtered'),
        portfolio_table(),

])