import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
from app import app
import datetime
from datetime import date

import pickle

with open("assets/region.pkl", "rb") as f:
    df = pickle.load(f)

with open("assets/r_list.pkl", "rb") as f:
    r_list = pickle.load(f)

with open("assets/bra_regions.pkl", "rb") as f:
    bp = pickle.load(f)

with open("assets/ca_states.pkl", "rb") as f:
    canp = pickle.load(f)

with open("assets/uk_countries.pkl", "rb") as f:
    uk = pickle.load(f)

with open("assets/us_states.pkl", "rb") as f:
    us = pickle.load(f)

uk.columns = ['region', 'population']
us.columns = ['region', 'population']
canp.columns = ['region', 'population']

df_reg = bp.append(uk, ignore_index=True)
df_reg = df_reg.append(us, ignore_index=True)
df_reg = df_reg.append(canp, ignore_index=True)

df = df.merge(df_reg, left_on="RegionName", right_on="region")
df['Deaths per capita per million'] = 1000000 * df['ConfirmedDeaths'] / df['population']
y = ["C1_School closing", "C2_Workplace closing", "C3_Cancel public events", "C4_Restrictions on gatherings", "C5_Close public transport", "C6_Stay at home requirements", "C7_Restrictions on internal movement", "C8_International travel controls", "H6_Facial Coverings"]


df[y] = df[y] * 67.56/19

options = []
for region in r_list:
    r_dict = {'label': region, 'value': region}
    options.append(r_dict)

layout = html.Div([
    html.H1('Region (Sub-national) Comparison - Brazil, Canada, UK, USA', style={"textAlign": "center"}),

    html.Div([
        html.Div(dcc.Dropdown(
            id='c1r-dropdown', value='Region 1', clearable=False,
            options=options
        ), className='five columns offset-by-one column'),

        html.Div(dcc.Dropdown(
            id='c2r-dropdown', value='Region 2', clearable=False,
            persistence=True, persistence_type='memory',
            options=options
        ), className='five columns'),
    ], className='row'),

    dcc.Graph(id='c1r-bar', figure={}),
    dcc.Graph(id='c2r-bar', figure={}),
])

@app.callback(
    Output('c1r-bar','figure'),
    [Input('c1r-dropdown', 'value')]
)
def display_region1(value):
    filter_list = []
    filter_list.append(value)

    df2 = df[df['RegionName'].isin(filter_list)].fillna(0)

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
    myFig.update_yaxes(title_text="Deaths", secondary_y=True, range=[0,3200])
    myFig.update_layout(title_text=value, bargap=0)

    return myFig

@app.callback(
    Output(component_id='c2r-bar', component_property='figure'),
    [Input(component_id='c2r-dropdown', component_property='value')]
)
def region2(value):

    filter_list = []
    filter_list.append(value)

    df2 = df[df['RegionName'].isin(filter_list)].fillna(0)

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
    myFig.update_yaxes(title_text="Stringency Index", secondary_y=False, range=[0,100])
    myFig.update_yaxes(title_text="Deaths", secondary_y=True, range=[0, 3200])
    myFig.update_layout(title_text=value, bargap=0)

    return myFig