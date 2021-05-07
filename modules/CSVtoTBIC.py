import sshtunnel
import pandas as pd
import sqlalchemy
from decouple import config

NAME = config('DB_NAME')
USER = config('DB_USER')
PASSWORD = config('DB_PASSWORD')
HOST = config('DB_HOST')
PORT = config('DB_PORT')
SSH_USER = config('SSH_USER')
SSH_PASSWORD = config('SSH_PASSWORD')

sshtunnel.SSH_TIMEOUT = 5.0
sshtunnel.TUNNEL_TIMEOUT = 5.0

with sshtunnel.SSHTunnelForwarder(
        ('ssh.pythonanywhere.com'),
        ssh_username=SSH_USER, ssh_password=SSH_PASSWORD,
        remote_bind_address=(NAME, 12175)
) as tunnel:
    engine = sqlalchemy.create_engine('postgresql://' + str(USER) + ':' + str(PASSWORD) + '@localhost:9999/tbic')

class CSVtoTBIC:
    def __init__(self, filename):
        self.read(filename=filename)

    def read(self, filename):
        self.df = pd.read_csv(filename)
        self.df.drop(self.df.loc[self.df['Symbol'] == 'B09Y8Y2'].index, inplace=True)

    def to_sql_manual(self, year, month, meeting_num):
        self.df['meeting_num'] = meeting_num
        self.df['year'] = year
        self.df['month'] = month
        self.df.to_sql("ii_meeting_stock", engine, if_exists='append')

    def to_sql(self):
        df = pd.read_sql("select max(meeting_num) from tbic_stock_meeting", engine)
        meeting_num = df['max'].to_list()[0]

        mth_yr = pd.read_sql("select month, year from tbic_stock_meeting where meeting_num = '" + str(meeting_num) + "'", engine)
        meeting_num = meeting_num + 1

        if mth_yr['month'].to_list()[0] == 12:
            month = 1
            year = mth_yr['year'].to_list()[0] + 1
        else:
            month = mth_yr['month'] + 1
            year = mth_yr['year']

        self.df['meeting_num'] = meeting_num
        self.df['year'] = year
        self.df['month'] = month
        self.df.to_sql("ii_meeting_stock", engine, if_exists='append')

