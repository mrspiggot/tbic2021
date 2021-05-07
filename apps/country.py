import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
from app import app
import datetime
from datetime import date, timedelta


import pickle

with open("assets/country.pkl", "rb") as f:
    df = pickle.load(f)

with open("assets/world_pop.pkl", "rb") as f:
    wp = pickle.load(f)


mask = (df['Date'] < (pd.Timestamp('today') - pd.Timedelta(3, unit='D')))
df = df.loc[mask]
df_combined = df.merge(wp, left_on="CountryCode", right_on="Country Code")
df_combined['Deaths per capita per million'] = 1000000 * df_combined['ConfirmedDeaths'] / df_combined['Value']
y = ["C1_School closing", "C2_Workplace closing", "C3_Cancel public events", "C4_Restrictions on gatherings", "C5_Close public transport", "C6_Stay at home requirements", "C7_Restrictions on internal movement", "C8_International travel controls", "H6_Facial Coverings"]


df_combined[y] = df_combined[y] * 67.56/19


with open("assets/c_list.pkl", "rb") as f:
    c_list = pickle.load(f)

options = []
for country in c_list:
    c_dict = {'label': country, 'value': country}
    options.append(c_dict)

layout = html.Div([
    html.H1('Country Comparison', style={"textAlign": "center"}),

    html.Div([
        html.Div(dcc.Dropdown(
            id='c1-dropdown', value='Country 1', clearable=False,
            options=options
        ), className='five columns offset-by-one column'),

        html.Div(dcc.Dropdown(
            id='c2-dropdown', value='Country 2', clearable=False,
            persistence=True, persistence_type='memory',
            options=options
        ), className='five columns'),
    ], className='row'),

    dcc.Graph(id='c1-bar', figure={}),
    dcc.Graph(id='c2-bar', figure={}),
])

@app.callback(
    Output('c1-bar','figure'),
    [Input('c1-dropdown', 'value')]
)
def display_country1(value):
    filter_list = []
    filter_list.append(value)

    df2 = df_combined[df_combined['CountryName'].isin(filter_list)].fillna(0)

    myFig = make_subplots(specs=[[{"secondary_y": True}]])


    myFig.add_trace(go.Bar(name='School Closing', x=df2['Date'], y=df2['C1_School closing']), secondary_y=False)
    myFig.add_trace(go.Bar(name='Workplace Closing', x=df2['Date'], y=df2['C2_Workplace closing']), secondary_y=False)
    myFig.add_trace(go.Bar(name='Cancel public events', x=df2['Date'], y=df2['C3_Cancel public events']),
                    secondary_y=False)
    myFig.add_trace(go.Bar(name='Restrictions on gatherings', x=df2['Date'], y=df2['C4_Restrictions on gatherings']),
                    secondary_y=False)
    myFig.add_trace(go.Bar(name='Close public transport', x=df2['Date'], y=df2['C5_Close public transport']),
                    secondary_y=False)
    myFig.add_trace(go.Bar(name='Stay at home requirements', x=df2['Date'], y=df2['C6_Stay at home requirements']),
                    secondary_y=False)
    myFig.add_trace(
        go.Bar(name='Restrictions on internal movement', x=df2['Date'], y=df2['C7_Restrictions on internal movement']),
        secondary_y=False)
    myFig.add_trace(go.Bar(name='International travel controls', x=df2['Date'], y=df2['C8_International travel controls']),
                    secondary_y=False)
    myFig.add_trace(go.Bar(name='Facial Coverings', x=df2['Date'], y=df2['H6_Facial Coverings']), secondary_y=False)

    myFig.add_trace(go.Scatter(name="Deaths per capita per million", x=df2['Date'], y=df2['Deaths per capita per million'], line=dict(color="#0000ff")),
                    secondary_y=True)

    myFig.update_layout(barmode='stack')
    myFig.update_yaxes(title_text="Stringency", secondary_y=False, range=[0,100])
    myFig.update_yaxes(title_text="Deaths per Capita per million", secondary_y=True, range=[0,2800])
    myFig.update_layout(title_text=value, bargap=0)

    return myFig

@app.callback(
    Output(component_id='c2-bar', component_property='figure'),
    [Input(component_id='c2-dropdown', component_property='value')]
)
def display_country2(value):
    filter_list = []
    filter_list.append(value)

    df2 = df_combined[df_combined['CountryName'].isin(filter_list)].fillna(0)

    myFig = make_subplots(specs=[[{"secondary_y": True}]])


    myFig.add_trace(go.Bar(name='School Closing', x=df2['Date'], y=df2['C1_School closing']), secondary_y=False)
    myFig.add_trace(go.Bar(name='Workplace Closing', x=df2['Date'], y=df2['C2_Workplace closing']), secondary_y=False)
    myFig.add_trace(go.Bar(name='Cancel public events', x=df2['Date'], y=df2['C3_Cancel public events']),
                    secondary_y=False)
    myFig.add_trace(go.Bar(name='Restrictions on gatherings', x=df2['Date'], y=df2['C4_Restrictions on gatherings']),
                    secondary_y=False)
    myFig.add_trace(go.Bar(name='Close public transport', x=df2['Date'], y=df2['C5_Close public transport']),
                    secondary_y=False)
    myFig.add_trace(go.Bar(name='Stay at home requirements', x=df2['Date'], y=df2['C6_Stay at home requirements']),
                    secondary_y=False)
    myFig.add_trace(
        go.Bar(name='Restrictions on internal movement', x=df2['Date'], y=df2['C7_Restrictions on internal movement']),
        secondary_y=False)
    myFig.add_trace(go.Bar(name='International travel controls', x=df2['Date'], y=df2['C8_International travel controls']),
                    secondary_y=False)
    myFig.add_trace(go.Bar(name='Facial Coverings', x=df2['Date'], y=df2['H6_Facial Coverings']), secondary_y=False)

    myFig.add_trace(go.Scatter(name="Deaths per Capita per million", x=df2['Date'], y=df2['Deaths per capita per million'], line=dict(color="#0000ff")),
                    secondary_y=True)

    myFig.update_layout(barmode='stack')
    myFig.update_yaxes(title_text="Stringency", secondary_y=False, range=[0,100])
    myFig.update_yaxes(title_text="Deaths per capita per million", secondary_y=True, range=[0,2800])
    myFig.update_layout(title_text=value, bargap=0)

    return myFig