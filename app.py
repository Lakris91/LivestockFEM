import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, Event
import base64
import plotly.graph_objs as go
import numpy as np
import math
import json
from os import urandom
from io import StringIO
from flask import Flask
from parseDict import plotDict
from datetime import datetime, date

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = Flask(__name__)
server.secret_key = urandom(16)
app = dash.Dash(name = __name__, server = server, external_stylesheets=external_stylesheets)

#app = dash.Dash(name = __name__, external_stylesheets=external_stylesheets)
app.config.supress_callback_exceptions = True
app.title = 'LivestockFEM'

colors = {
    'text': '#0B4C5F'
}

jsonDict={}

def generateTabs():
    tab_height='40px'
    tabDef=html.Div([
    dcc.Tabs(id="tabs", value='scaling',style={'width':'50%', 'height':tab_height,'font-size': '16px','padding':1}, children=[
    dcc.Tab(label='Scaling', value='scaling',style={'padding': '6px'},selected_style={'padding': '6px'}),
    dcc.Tab(label='Topology', value='topology',style={'padding': '6px'},selected_style={'padding': '6px'}),
    dcc.Tab(label='Supports', value='support',style={'padding': '6px'},selected_style={'padding': '6px'}),
    dcc.Tab(label='Results', value='result',style={'padding': '6px'},selected_style={'padding': '6px'})
    ]),
    html.Div(id='tabs-content')
    ])
    return tabDef

# Layout -----------------------------------------------------------------------

app.layout = html.Div(children=[
    html.Div([
    html.H1('LivestockFEM', style={'display': 'inline-block'}),
    html.H6('A simple FEM calculation tool.', style={'display': 'inline-block'})
    ]),

    html.Div([
        dcc.Upload(
            id='upload-data',
            children=html.Div(['Drag and Drop or ', html.A('Select Input File')]),
            accept='.json',
            style={
                'width': '25%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px',
                'display': 'inline-block'
            },
        ),
        html.Div(id='loadButton',style={'display': 'inline-block'}),
    ]),

    html.Div(id='checkboxes',style={'padding': 10}),
    html.Div(id='thePlot'),

    html.Div([
            #html.Hr(),
            html.Div(id='defTextDiv',children=[])
            ])
])


# Callbacks -----------------------------------------------------------------------

@app.callback(Output(component_id='loadButton', component_property='children'),
              [Input(component_id='upload-data', component_property='contents')])
def update_output(list_of_contents):
    global jsonDict
    if list_of_contents is not None:
        content_type, content_string = list_of_contents.split(',')
        decoded = base64.b64decode(content_string)
        iostr = StringIO(decoded.decode('utf-8'))
        jsonDict=json.load(iostr)
        return html.Button(id='loadData', children='Load Input Data')

@app.callback(Output(component_id='defTextDiv', component_property='children'),
              [Input(component_id='loadData', component_property='n_clicks')])
def update_output(n_clicks):
    return generateTabs()

#@app.callback(Output(component_id='upload-data', component_property='children'),
#              [Input(component_id='upload-data', component_property='contents')],
#              [State('upload-data', 'filename'),
#               State('upload-data', 'last_modified')])
#def update_output(list_of_contents,name,modif):
#    if list_of_contents is not None:
#        return html.Div([html.I("'"+name+"' "), " last modified: ", html.I(str(datetime.fromtimestamp(modif)).split(".")[0]) ," is loaded. " , html.A('Load another input file?')])
#    else:
#        return html.Div(['Drag and Drop or ', html.A('Select Input File')])



@app.callback(Output(component_id='checkboxes', component_property='children'),
              [Input(component_id='loadData', component_property='n_clicks')])
def update_output(n_clicks):
    viewCheck=  html.Div(
                    [
                        html.Div(
                            [
                            html.Div('View filter:'),
                            html.Div(dcc.Checklist(
                                id='viewfilter',
                                options=[
                                    #{'label': 'Nodes', 'value': },
                                    #{'label': 'Elements', 'value': },
                                    {'label': 'Deformation', 'value': "DOFPlot"},
                                    {'label': 'Normal Forces', 'value': "ForcePlot1"},
                                    {'label': 'Shear Forces', 'value': "ForcePlot2"},
                                    {'label': 'Bending Moments', 'value': "ForcePlot3"}],
                                values=['DOFPlot'],
                                labelStyle={'display': 'inline-block'},
                            ))
                            ],
                            className='three columns'
                        ),
                        html.Div(
                            [
                            html.Div('Deformation Scale:'),
                            dcc.Input(id='defText', type='number',value=jsonDict["PlotScalingDeformation"], selectionDirection='forward' )
                            ],
                            style={'display': 'inline-block'},
                        ),
                        html.Div(
                            [
                            html.Div('Forces Scale:'),
                            dcc.Input(id='forText', type='number',value=jsonDict["PlotScalingForces"], selectionDirection='forward' )
                            ],
                            style={'display': 'inline-block'},
                        )
                    ],
                )
    return viewCheck

@app.callback(Output(component_id='thePlot', component_property='children'),
              [Input(component_id='defText', component_property='value'),
              Input(component_id='forText', component_property='value'),
              Input(component_id='viewfilter', component_property='values')
              ])
def update_output(defVal,forVal,vfil):
    global jsonDict
    print(1,defVal,forVal,vfil)
    jsonDict["PlotScalingDeformation"]=defVal
    jsonDict["PlotScalingForces"]=forVal
    return plotDict(jsonDict,vfil)

@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'scaling':
        return html.Div([
                html.H3('Scaling something')
                ])
    elif tab == 'result':
        return  html.Div([
                html.H3('This is the results')
                ])
    else:
        return  html.Div([
                html.H3('Du er da lidt for nysgerrig')
                ])

#if __name__ == '__main__':
#    app.run_server(debug=True)
