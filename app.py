import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, Event
import base64
#import pandas as pd
import plotly.graph_objs as go
import numpy as np
import math
import json
from io import StringIO

from parseDict_old import plotDict
from datetime import datetime, date

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config.supress_callback_exceptions = True
colors = {
    'text': '#0B4C5F'
}

jsonDict={}

def ScaleFields(val1,val2):
        fields=html.Div(children=[
        html.Div(children='Deformation Scale:', style={'textAlign': 'left','color': '#0B4C5F'}),
        html.Div(dcc.Input(id='defText', type='number',value=val1 )),
        html.Div(children='Forces Scale:', style={'textAlign': 'left','color': '#0B4C5F'}),
        html.Div(dcc.Input(id='forText', type='number',value=val2 ))
        ])
        return fields

#scatterPlot, [minx,maxx], [miny,maxy],unitfactor=makeScatter(jsonDict),
#print(scatterPlot)


app.layout = html.Div(children=[
    html.H1(
        children='LivestockFEM',
        style={
            'textAlign': 'left',
            'color': colors['text']
        }
    ),

    html.Div(children='A simple FEM calculation tool.', style={
        'textAlign': 'left',
        'color': colors['text']
    }),

    #html.Div([
    dcc.Upload(html.Button(children='Upload JSON-file'), id='upload-data', accept='.json'),
    html.Div(id='thePlot'),


    #]),

    html.Div([
            html.Hr(),

            #html.Div(children='Deformation Scale:', style={'textAlign': 'left','color': '#0B4C5F'}),
            html.Div(id='defTextDiv',children=[ScaleFields(1,1)])#, children=dcc.Input(id='defText', type='number'))
            #html.Div(id='defText', style={'textAlign': 'left','color': '#0B4C5F'}),

            #html.Div(children='Forces Scale:', style={'textAlign': 'left','color': '#0B4C5F'}),
            #dcc.Input(id='forcescale',type='number'),
            #html.Div(id='forText', style={'textAlign': 'left','color': '#0B4C5F'}),
            ])

        # html.Div([
    #         html.Hr(),
    #
    #         html.Div(id='defText', children='Deformation Scale:', style={'textAlign': 'left','color': '#0B4C5F'}),
    #         dcc.Input(id='deformscale', type='number'),
    #
    #         html.Div(id='forText', children='Forces Scale:', style={'textAlign': 'left','color': '#0B4C5F'}),
    #         dcc.Input(id='forcescale',type='number')
    #
    #         ])
    #html.Div(id='output-data-upload'),
    #html.Div(id='output-data-upload_2'),
    #html.Div(id='def_input_field')
])

@app.callback(Output(component_id='thePlot', component_property='children'),
              [Input(component_id='upload-data', component_property='contents'),
              Input(component_id='defText', component_property='value'),
              Input(component_id='forText', component_property='value')])
def update_output(list_of_contents, defVal,forVal):
    global jsonDict
    if list_of_contents is not None:
        content_type, content_string = list_of_contents.split(',')
        decoded = base64.b64decode(content_string)
        iostr = StringIO(decoded.decode('utf-8'))
        jsonDict=json.load(iostr)
        jsonDict["PlotScalingDeformation"]=defVal
        jsonDict["PlotScalingForces"]=forVal
        #scatterPlot, xrange, yrange, unitfactor = makeScatter(jsonDict)
        return plotDict(jsonDict)#plotIt(scatterPlot, xrange, yrange, unitfactor)


@app.callback(Output(component_id='defTextDiv', component_property='children'),
              [Input(component_id='upload-data', component_property='contents')])
def update_output(list_of_contents):
    global jsonDict
    if list_of_contents is not None:
        content_type, content_string = list_of_contents.split(',')
        decoded = base64.b64decode(content_string)
        iostr = StringIO(decoded.decode('utf-8'))
        jsonDict=json.load(iostr)
        return ScaleFields(jsonDict["PlotScalingDeformation"],jsonDict["PlotScalingForces"])
        # html.Div(children=[
        #         html.Div(children='Deformation Scale:', style={'textAlign': 'left','color': '#0B4C5F'}),
        #         html.Div(dcc.Input(id='defText', type='number',value=jsonDict["PlotScalingDeformation"] )),
        #         html.Div(children='Forces Scale:', style={'textAlign': 'left','color': '#0B4C5F'}),
        #         html.Div(dcc.Input(id='forText', type='number',value=jsonDict["PlotScalingForces"] ))
        #         ])


    # else:
    #     try:
    #         defvalue=jsonDict["PlotScalingDeformation"]
    #     except:
    #         defvalue=5
    #     print(defvalue)
    #     return html.Div(dcc.Input(id='defText', type='number',value=defvalue))

# @app.callback(Output(component_id='forText', component_property='value'),
#               [Input(component_id='upload-data', component_property='contents')])
# def update_output(list_of_contents):
#     if list_of_contents is not None:
#         content_type, content_string = list_of_contents.split(',')
#         decoded = base64.b64decode(content_string)
#         iostr = StringIO(decoded.decode('utf-8'))
#         #global jsonDict
#         jsonDict=json.load(iostr)
#         print(jsonDict["PlotScalingForces"])
#         return jsonDict["PlotScalingForces"]



# @app.callback(Output(component_id='output-data-upload', component_property='children'),
#               [Input(component_id='upload-data', component_property='contents'),
#               #Input('updateDefScale', 'value')
#               ])
# def update_output(list_of_contents,defScale):
#     if list_of_contents is not None:
#         content_type, content_string = list_of_contents.split(',')
#         decoded = base64.b64decode(content_string)
#         iostr = StringIO(decoded.decode('utf-8'))
#         global jsonDict
#         jsonDict=json.load(iostr)
#         print(defScale)
#         jsonDict["PlotScalingDeformation"]=float(defScale)
#         #print(jsonDict)
#         return plotDict(jsonDict)
#
# @app.callback(Output(component_id='def_input_field', component_property='children'),
#               [Input(component_id='output-data-upload', component_property='children')])
# def scaleBox(inputDict):
#     global jsonDict
#     return html.Div([
#             html.Hr(),
#             html.Div(children='Deformation Scale:',
#             style={'textAlign': 'left','color': '#0B4C5F'}),
#             dcc.Input(id='deformscale',value=jsonDict["PlotScalingDeformation"])
#             #html.Div(children='Forces Scale:',
#             #style={'textAlign': 'left','color': '#0B4C5F'}),
#             #dcc.Input(id='forcescale',value=jsonDict["PlotScalingForces"])
#             ])
#
# @app.callback(Output('updateDefScale', 'value'),
#                [Input(component_id='deformscale', component_property='value')
#                #Input(component_id='forcescale', component_property='value')
#                ])
# def scalePrint(defVal):
#     return defVal
#     #if defVal is not None:
#         #global jsonDict
#         #jsonDict["PlotScalingDeformation"]=float(defVal)
#         #jsonDict["PlotScalingForces"]=float(forVal)
#         #return defVal



if __name__ == '__main__':
    app.run_server(debug=True)
