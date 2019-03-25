import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import base64
import plotly.graph_objs as go
import numpy as np
import math
import json
import timeit
import sys
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
app = dash.Dash(name=__name__, server=server, external_stylesheets=external_stylesheets)
app.config.supress_callback_exceptions = True
app.title = 'LivestockFEM'


np.set_printoptions(threshold=sys.maxsize,linewidth=sys.maxsize)

# Help Functions ---------------------------------------------------------------

def matrixToHtml(matlist,hoverData,dofs,element=True,system=True):
    htmlList=[]

    try:
        if element:
            matlist = matlist[hoverData["points"][0]["customdata"]]

        matStr=str(np.round(np.array(matlist)).astype(int)).replace("[["," ").replace("[","").replace("]]","").replace(" -1 ","DOF ")
        matStr=matStr.replace("\n","").replace("]","\n")
        cellLen=int(len(matStr.replace("\n",""))/(len(matlist)**2))
        dofColor=[['#a2bbd6','#a2d6aa'],['#d6d3a2','#d6a2a2']]
        for i, row in enumerate(matStr.split("\n")):
            for j,pos in enumerate(range(0,len(row),cellLen)):
                cell=row[pos:pos+cellLen]
                if pos == 0 and i == 0:
                    htmlList.append(html.U(html.B(cell[1:]+"|")))
                elif pos == 0:
                    htmlList.append(html.B(cell[1:]+"|"))
                elif i == 0:
                    htmlList.append(html.U(html.B(cell)))
                elif (float(i-1) in dofs and float(j-1) in dofs) and system:
                    dColor=dofColor[int(dofs.index(float(i-1))/3)][int(dofs.index(float(j-1))/3)]
                    htmlList.append(html.B(cell,style={'background-color': dColor}))
                elif element and not system:
                    htmlList.append(html.B(cell,style={'background-color': dofColor[int((i-1)/3)][int((j-1)/3)]}))
                else:
                    htmlList.append(cell)
            htmlList.append("\n")
    except:
        matStr=""
    return htmlList

# Layout -----------------------------------------------------------------------

app.layout = html.Div(children=[
    # Hidden div inside the app that stores a variable instead of using Global that won't work on the server
    html.Div(id='GloVar_json', style={'display': 'none'}),
    html.Div(id='test', style={'display': 'none'}),
    html.Div([
        html.H1('LivestockFEM', style={'display': 'inline-block', 'margin-bottom':'0px','vertical-align': 'middle','padding-bottom':'0px'}),
        html.H6('A simple FEM calculation tool.', style={'display': 'inline-block', 'margin-bottom':'0px', 'margin-left':'8px','vertical-align': 'middle','padding':'0px'}),
        html.Div(children=[
        dragndrop('upload-data', 'Drag and Drop or ', 'Select Input File'),
        ],style={'display': 'inline-block', 'margin-bottom':'0px', 'margin-left':'8px','vertical-align': 'middle','padding-bottom':'0px'})
    ],style={'margin':'0px','padding':'0px'}),



    html.Div(id='checkboxes', style={'padding': 5,'margin-bottom':'0px','margin-top':'0px'}),
    html.Div(id='thePlot'),
    html.Div([html.Div(id='tabDiv', children=[])])
])

# Callbacks --------------------------------------------------------------------

# Upload file parse data to json and store in hidden Div variable
@app.callback(Output(component_id='GloVar_json', component_property='children'),
              [Input(component_id='upload-data', component_property='contents')])
def update_output(list_of_contents):
    if list_of_contents is not None:
        content_type, content_string = list_of_contents.split(',')
        decoded = base64.b64decode(content_string)
        iostr = StringIO(decoded.decode('utf-8'))
        jsonDict = json.load(iostr)
        resultDict = FEM_frame(jsonDict).outDict
        return str(jsonDict).replace("'", '"'), str(resultDict).replace("'", '"')

# Generates the tabs when the GloVar_json is changed
@app.callback(Output(component_id='tabDiv', component_property='children'),
              [Input(component_id='GloVar_json', component_property='children')])
def update_output(jsonStr):
    if jsonStr is not None:
        return generateTabs()

# Changes the text in the upload area when file is uploaded
@app.callback(Output(component_id='upload-data', component_property='children'),
              [Input(component_id='upload-data', component_property='contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output(list_of_contents, name, modif):
    if list_of_contents is not None:
        return html.Div([html.I("'"+name+"' "), ' last modified: ', html.I(str(datetime.fromtimestamp(modif)).split('.')[0]), ' is loaded. ', html.A('Load another input file?')])
    else:
        return html.Div(['Drag and Drop or ', html.A('Select Input File')])

# Generates viewfilter when GloVar_json is updated
@app.callback(Output(component_id='checkboxes', component_property='children'),
              [Input(component_id='GloVar_json', component_property='children')])
def update_output(jsonStr):
    if jsonStr is not None:
        jsonDict = json.loads(jsonStr[0])
        return viewFilter(jsonDict)

# Generates the plot based on input from deformation scale or force scale or viewfilter
@app.callback(Output(component_id='thePlot', component_property='children'),
              [Input(component_id='defText', component_property='value'),
               Input(component_id='forText', component_property='value'),
               Input(component_id='viewfilter', component_property='values'),
               Input(component_id='plotHeight', component_property='value')
               ],
              [State(component_id='GloVar_json', component_property='children')])
def update_output(defVal, forVal, vfil,plotHeight, jsonStr):
    start = timeit.default_timer()
    if jsonStr is not None:
        jsonDict = json.loads(jsonStr[0])
        resultDict = json.loads(jsonStr[1])
        print(1, defVal, forVal, vfil)
        if jsonDict['PlotScalingDeformation'] == defVal and jsonDict['PlotScalingForces'] == forVal:
            print('Without calc:', timeit.default_timer()-start)
            return plotDict(resultDict, vfil,plotHeight)
        else:
            jsonDict['PlotScalingDeformation'] = defVal
            jsonDict['PlotScalingForces'] = forVal
            resultDict = FEM_frame(jsonDict).outDict
            print('With calc:', timeit.default_timer()-start)
            return plotDict(resultDict, vfil,plotHeight)

# Generates the contents of the tabs
@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'nodes':
        return tab1()
    elif tab == 'elements':
        return tab2()
    elif tab == 'supports':
        return tab3()
    elif tab == 'loads':
        return tab4()
    elif tab == 'matrix':
        return tab5()
    else:
        return tab6()

@app.callback(Output('hover-data', 'children'),
    [Input('FEM-Plot', 'hoverData')],
    [State('GloVar_json', 'children')])
def display_hover_data(hoverData,jsonStr):
    resJson=json.loads(jsonStr[1])
    try:
        elementNo=hoverData["points"][0]["customdata"]
        dofs=resJson["ElementStiffnessSmall"][elementNo][0][1:]
        matrix2=["Current Element: "+ str(elementNo) + "\n"]
        matrix2.extend("Element Degrees of Freedom: " + " ".join([str(int(dof)) for dof in dofs]) + "\n")
        matrix2.extend("\nElement Stiffness Matrix, each row and column represents its Degree of Freedom (DOF):\n")
        matrix2.extend(matrixToHtml(resJson["ElementStiffnessSmall"],hoverData,dofs,True,False))
        matrix2.extend(["\nElement Stiffness Matrix Expanded, the Element Stiffness Matrix is expanded to the size of the System Stiffness Matrix based on the degree of freedom:\n"])
        matrix2.extend(matrixToHtml(resJson["ElementStiffnessExpanded"],hoverData,dofs,True,True))
        matrix2.extend(["\nSystem Stiffness Matrix, adding the expanded Element Stiffness Matrixes together forms the System Stiffness Matrix:\n"])
        matrix2.extend(matrixToHtml(resJson["SystemStiffness"],hoverData,dofs,False,True))
    except:
        matrix2 = ""
    return matrix2

@app.callback(Output('results-div', 'children'),
    [Input('result-dropdown', 'value'),
    Input('GloVar_json', 'children')])
def update_output2(value,jsonStr):
    resJson=json.loads(jsonStr[1])


    if value=='overview':
        maxDisp=np.max(np.array(resJson["DefDist"]))
        maxMoment=np.max(np.absolute(np.array(resJson["MomentForcesPt"])))
        maxNormal=np.max(np.absolute(np.array(resJson["NormalForce1"])))
        maxShear=np.max(np.absolute(np.array(resJson["ShearForce2"])))
        resDiv = html.Div([
            html.H3('Results overview:'),
            html.Table([
                html.Tr([
                    html.Td("Max Displacement:"),
                    html.Td(str(int(maxDisp)),style={'textAlign':'right'}),
                    html.Td("mm")
                ],style={'padding': '0px'}),
                html.Tr([
                    html.Td("Max Absolute Bending Moment:"),
                    html.Td(str(int(maxMoment)),style={'textAlign':'right'}),
                    html.Td("Nm")
                ],style={'padding': '0px'}),
                html.Tr([
                    html.Td("Max Absolute Normal Forces:"),
                    html.Td(str(int(maxNormal)),style={'textAlign':'right'}),
                    html.Td("N/m2")
                ],style={'padding': '0px'}),
                html.Tr([
                    html.Td("Max Absolute Shear Forces:"),
                    html.Td(str(int(maxShear)),style={'textAlign':'right'}),
                    html.Td("N/m2")
                ],style={'padding': '0px'})
            ])
        ])
    else:
        resDiv="Please wait for this to implemented"
    return resDiv

if __name__ == '__main__':
    app.run_server(debug=True)
