import sshtunnel
import pandas as pd
from forex_python.converter import CurrencyRates
from pathlib import Path
import sqlalchemy
import yahoo_fin.stock_info as si
from datetime import timedelta, datetime, date
from decouple import config
from babel.numbers import format_currency
from app import engine


c = CurrencyRates()
rates = c.get_rates('GBP')
rates.update({'GBP': 100})

class Stock:
    def __init__(self, symbol):
        self.symbol = symbol
        self.currency = self.get_currency()
        self.yahoo_ticker = self.xref()

    def get_currency(self):
        query = "select currency from tbic_stocks where symbol = '" + str(self.symbol) + "'"
        ccy = pd.read_sql(query, engine)['currency'].to_list()[0]
        return ccy

    def xref(self):
        query = "select code from cross_reference where symbol = '" + str(self.symbol) + "' and system = 'Yahoo'"
        yahoo_ticker = pd.read_sql(query, engine)['code'].to_list()[0]
        return yahoo_ticker

    def get_quote(self, quote_date):
        try:
            quote = si.get_data(self.yahoo_ticker, start_date=quote_date, end_date=quote_date + timedelta(days=1))
        except:
            prev_date = quote_date - timedelta(days=1)
            quote = si.get_data(self.yahoo_ticker, start_date=prev_date, end_date=prev_date + timedelta(days=1))

        quote.sort_index(ascending=False, inplace=True)
        return quote.head(1)

    def get_quote_in_gbp(self, quote_date):
        gbp = rates[self.currency]
        try:
            quote = si.get_data(self.yahoo_ticker, start_date=quote_date, end_date=quote_date + timedelta(days=1))
        except:
            prev_date = quote_date - timedelta(days=1)
            quote = si.get_data(self.yahoo_ticker, start_date=prev_date, end_date=prev_date + timedelta(days=1))

        quote[['open', 'high', 'low', 'close', 'adjclose']] = quote[['open', 'high', 'low', 'close', 'adjclose']] / gbp
        return quote

    def get_live_price(self):
        price = si.get_live_price(self.yahoo_ticker)
        if self.currency == 'GBP':
            price = price / 100

        return price

    def get_quote_range(self, start, end):
        quote = si.get_data(self.yahoo_ticker, start_date=start, end_date=end)

        return quote

    def get_latest_price(self):
        query = "select price from intra_day_quotes where ticker = '" + str(self.yahoo_ticker) + "' and datetime > '" \
                + str(date.today()) +"' order by datetime desc"

        try:
            price = pd.read_sql(query, engine)['price'].head(1).to_list()[0]
        except Exception as e:
            query = "select max(index) from stock_quotes where ticker = '" + str(self.yahoo_ticker) + "'"
            m_date = pd.read_sql(query, engine)['max'].to_list()[0]
            query2 = "select adjclose from stock_quotes where ticker = '" + str(self.yahoo_ticker) + "' and index ='" + str(m_date) + "'"
            price = pd.read_sql(query2, engine)['adjclose'].head(1).to_list()[0]

        return price
