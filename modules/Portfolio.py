import pandas as pd
from modules.Stock import Stock
from forex_python.converter import CurrencyRates
import time
from app import cache, engine

c = CurrencyRates()
rates = c.get_rates('GBP')
#rates.update({'GBP': 100})

class Portfolio:
    def __init__(self):
        self.tbic = pd.read_sql('tbic_stocks', engine)
        self.yahoo_tickers = self.get_yahoo_tickers()
        self.gbp_cash = self.get_gbp_cash_balance()

    def ticker_list(self):
        return self.tbic['symbol'].to_list()

    def yahoo_ticker_list(self):
        symbols = self.ticker_list()
        ylist = []
        for symbol in symbols:
            ticker = Stock(symbol).yahoo_ticker
            ylist.append(ticker)

        return ylist

    @cache.memoize(1800)
    def meeting_history(self):
        max_meet = pd.read_sql("select max(meeting_num) from tbic_stock_meeting", engine)['max'].to_list()[0]
        m1 = max_meet
        m2 = max_meet-1
        m3 = max_meet-2
        m4 = max_meet-5
        m5 = max_meet-11
        m6 = max_meet-17
        m7 = max_meet-23

        query = 'SELECT t1.symbol, t1.currency, t1."Qty", t1.gbp_position, t2.gbp_position, t3.gbp_position, t4.gbp_position, t5.gbp_position, t6.gbp_position, t7.gbp_position, intra_day_quotes.price, intra_day_quotes.ticker \
                FROM tbic_stock_meeting t1, tbic_stock_meeting t2, tbic_stock_meeting t3, tbic_stock_meeting t4, tbic_stock_meeting t5, tbic_stock_meeting t6, tbic_stock_meeting t7, intra_day_quotes \
                where t1.meeting_num = ' + str(max_meet) + ' and t1.symbol = intra_day_quotes.symbol \
                AND t2.meeting_num = ' + str(m2) + ' and t2.symbol = intra_day_quotes.symbol \
                AND t3.meeting_num = ' + str(m3) + ' and t3.symbol = intra_day_quotes.symbol \
                AND t4.meeting_num = ' + str(m4) + ' and t4.symbol = intra_day_quotes.symbol \
                AND t5.meeting_num = ' + str(m5) + ' and t5.symbol = intra_day_quotes.symbol \
                AND t6.meeting_num = ' + str(m6) + ' and t6.symbol = intra_day_quotes.symbol \
                AND t7.meeting_num = ' + str(m7) + ' and t7.symbol = intra_day_quotes.symbol'
        try:
            df =  pd.read_sql(query, engine)
        except Exception as e:
            print("Error on portfolio.meeting_history()")
            print(e)
            time.sleep(15)
            df = pd.read_sql(query, engine)

        df.columns = ['symbol', 'currency', 'Qty', 'm1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'quote', 'ticker']
        df['meeting_num'] = max_meet
        df_pf = pd.read_sql_table("tbic_stocks", engine)
        return df.merge(df_pf, on='symbol')

    def gain_history(self):
        df = self.meeting_history()
        fx = CurrencyRates().get_rates('GBP')
        fx.update({'GBP': 100})

        for index, row in df.iterrows():
            df._set_value(index, 'Value', row['Qty'] * row['quote'] / fx[row['currency_x']])

        df['g1'] = (df['Value'] - df['m1']) / df['m1']
        df['g2'] = (df['Value'] - df['m2']) / df['m2']
        df['g3'] = (df['Value'] - df['m3']) / df['m3']
        df['g4'] = (df['Value'] - df['m4']) / df['m4']
        df['g5'] = (df['Value'] - df['m5']) / df['m5']
        df['g6'] = (df['Value'] - df['m6']) / df['m6']
        df['g7'] = (df['Value'] - df['m7']) / df['m7']

        return df

    @cache.memoize(1800)
    def get_yahoo_tickers(self):
        query = "select code from cross_reference where symbol in (select symbol from tbic_stocks) and system = 'Yahoo'"
        return pd.read_sql(query, engine)['code'].to_list()

    def currency_list(self):
        return list(set(self.tbic['currency'].to_list()))

    @cache.memoize(1800)
    def get_gbp_cash_balance(self):
        return pd.read_sql("select gbp_cash from tbic_cash_meeting where meeting_num in (select max(meeting_num) from tbic_cash_meeting)", engine)['gbp_cash'].to_list()[0]

    @cache.memoize(1800)
    def get_latest_prices(self):
        m_dt = pd.read_sql("select max(datetime) from intra_day_quotes", engine)['max'].to_list()[0]
        try:
            latest = pd.read_sql("select symbol, ticker, currency, price from intra_day_quotes where datetime = '" + str(m_dt) + "'", engine)
        except Exception as e:
            m_dt = pd.read_sql("select max(datetime) from stock_quotes", engine)['max'].to_list()[0]
            latest = pd.read_sql(
                "select symbol, ticker, currency, adjclose from stock_quotes where datetime = '" + str(m_dt) + "'",
                engine)
            latest.rename(columns={'adjclose': 'price'}, inplace=True)

        return latest

    def get_forex(self):
        latest = self.get_latest_prices()
        currency = self.currency_list()
        r = []
        for ccy in currency:
            d = {
                'currency': ccy,
                'fx': rates[ccy]
            }
            r.append(d)
        df_fx = pd.DataFrame(r)

        latest = latest.merge(df_fx, on='currency')

        return latest

    @cache.memoize(1800)
    def get_latest_position(self):
        m_mn = pd.read_sql("select max(meeting_num) from tbic_stock_meeting", engine)['max'].to_list()[0]
        query = 'select symbol, "Qty" from tbic_stock_meeting where meeting_num = ' + "'" + str(m_mn) + "'"

        position = pd.read_sql(query, engine)

        return position

    def get_value(self):
        forex = self.get_forex()

        value = self.tbic.merge(forex, on=['symbol', 'currency'])
        value.rename(columns={'symbol_x':'symbol'}, inplace=True)

        position = self.get_latest_position()
        position = position.merge(value, on='symbol')
        position['gbp_value'] = position['price']*position['Qty']/position['fx']

        eq_value = position['gbp_value'].sum()
        position['weight'] = position['gbp_value'] / eq_value

        return position

    @cache.memoize(1800)
    def gain_from_meeting(self, meeting_num):
        gain = self.gain_history()
        gain['cash_gain'] = gain['Value'] - gain[gain.columns[meeting_num+3]]
        gain['%_gain'] = 100 * gain[gain.columns[meeting_num+20]]
        gain['weight'] = gain['Value'] / gain['Value'].sum()
        return gain

    def gain_from_last_meeting(self):
        return self.gain_from_meeting(0)

    def top_3_gainers(self):
        df = self.gain_from_meeting(0)
        df_sort = df.sort_values(by='cash_gain', ascending=False)

        return df_sort

    def top_3_losers(self):
        df = self.gain_from_meeting(0)
        df_sort = df.sort_values(by='cash_gain', ascending=True)

        return df_sort

    def bar_gainers(self):
        df = self.gain_from_meeting(0)
        df_sort = df.sort_values(by='cash_gain', ascending=False)

        df_disp = df_sort[['name', 'cash_gain']]
        return df_disp.head(5)

    def bar_losers(self):
        df = self.gain_from_meeting(0)
        df_sort = df.sort_values(by='cash_gain', ascending=True)

        df_disp = df_sort[['name', 'cash_gain']]
        return df_disp.head(5)

    def currency_performance(self):
        df = self.gain_from_meeting(0)
        df2 = df.groupby(['currency_x']).sum()
        df_disp = df2[['cash_gain']]
        return df_disp

    def style_performance(self):
        df = self.gain_from_meeting(0)
        df2 = df.groupby(['stock_style']).sum()
        df_disp = df2[['cash_gain']]
        return df_disp

    def sector_performance(self):
        df = self.gain_from_meeting(0)
        df2 = df.groupby(['sector']).sum()
        df_disp = df2[['cash_gain']]
        return df_disp



