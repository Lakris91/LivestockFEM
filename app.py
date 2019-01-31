import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, Event
import base64
import plotly.graph_objs as go
import numpy as np
import math
import json
import timeit
from os import urandom
from io import StringIO
from flask import Flask
from parseDict import plotDict
from datetime import datetime, date
from livestockFEM_v2 import FEM_frame
from html_divs import *


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = Flask(__name__)
server.secret_key = urandom(16)
app = dash.Dash(name = __name__, server = server, external_stylesheets=external_stylesheets)

#app = dash.Dash(name = __name__, external_stylesheets=external_stylesheets)
app.config.supress_callback_exceptions = True
app.title = 'LivestockFEM'

# Layout -----------------------------------------------------------------------

app.layout = html.Div(children=[
    # Hidden div inside the app that stores the intermediate value
    html.Div(id='GloVar_json', style={'display': 'none'}),
    html.Div(id='GloVar_resultDict', style={'display': 'none'}),

    html.Div([
    html.H1('LivestockFEM', style={'display': 'inline-block'}),
    html.H6('A simple FEM calculation tool.', style={'display': 'inline-block'})
    ]),

    dragndrop(html.Div(['Drag and Drop or ', html.A('Select Input File')])),

    html.Div(id='checkboxes',style={'padding': 10}),
    html.Div(id='thePlot'),
    html.Div([ html.Div(id='defTextDiv',children=[]) ])
])


# Callbacks -----------------------------------------------------------------------

@app.callback(Output(component_id='GloVar_json', component_property='children'),
              [Input(component_id='upload-data', component_property='contents')])
def update_output(list_of_contents):
    if list_of_contents is not None:
        content_type, content_string = list_of_contents.split(',')
        decoded = base64.b64decode(content_string)
        iostr = StringIO(decoded.decode('utf-8'))
        jsonDict=json.load(iostr)
        resultDict = FEM_frame(jsonDict).outDict
        return str(jsonDict).replace("'",'"'),str(resultDict).replace("'",'"')

@app.callback(Output(component_id='defTextDiv', component_property='children'),
              [Input(component_id='GloVar_json', component_property='children')])
def update_output(jsonStr):
    if jsonStr is not None:
        return generateTabs()

@app.callback(Output(component_id='upload-data', component_property='children'),
             [Input(component_id='upload-data', component_property='contents')],
             [State('upload-data', 'filename'),
              State('upload-data', 'last_modified')])
def update_output(list_of_contents,name,modif):
   if list_of_contents is not None:
       return html.Div([html.I("'"+name+"' "), ' last modified: ', html.I(str(datetime.fromtimestamp(modif)).split('.')[0]) ,' is loaded. ' , html.A('Load another input file?')])
   else:
       return html.Div(['Drag and Drop or ', html.A('Select Input File')])

@app.callback(Output(component_id='checkboxes', component_property='children'),
              [Input(component_id='GloVar_json', component_property='children')])
def update_output(jsonStr):
    if jsonStr is not None:
        jsonDict = json.loads(jsonStr[0])
        return viewFilter(jsonDict)

@app.callback(Output(component_id='thePlot', component_property='children'),
              [Input(component_id='defText', component_property='value'),
              Input(component_id='forText', component_property='value'),
              Input(component_id='viewfilter', component_property='values')],
              [State(component_id='GloVar_json', component_property='children')])
def update_output(defVal,forVal,vfil, jsonStr):
    start = timeit.default_timer()
    if jsonStr is not None:
        jsonDict = json.loads(jsonStr[0])
        resultDict = json.loads(jsonStr[1])
        print(1,defVal,forVal,vfil)
        if jsonDict['PlotScalingDeformation']==defVal and jsonDict['PlotScalingForces']==forVal:
            print('Without calc:',timeit.default_timer()-start)
            return plotDict(resultDict,vfil)
        else:
            jsonDict['PlotScalingDeformation']=defVal
            jsonDict['PlotScalingForces']=forVal
            resultDict =  FEM_frame(jsonDict).outDict
            print('With calc:',timeit.default_timer()-start)
            return plotDict(resultDict,vfil)

@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'scaling':
        return tab1()
    elif tab == 'topology':
        return  tab2()
    elif tab == 'support':
        return  tab3()
    else:
        return  tab4()

#if __name__ == '__main__':
#    app.run_server(debug=True)
