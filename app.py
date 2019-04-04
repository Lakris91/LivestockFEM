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
import os
from os import urandom
from io import StringIO
from flask import Flask
from parseDict import plotDict
from datetime import datetime, date
from livestockFEM_v2 import FEM_frame
from html_divs import *
from six.moves.urllib.parse import quote

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
        dofColor=[['#d6a2a2','#a2bbd6'],['#a2d6aa','#d6d3a2']]
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
    html.Div([],id='GloVar_json', style={'display': 'none'}),
    html.Div([],id='GloVar_json_changed', style={'display': 'none'}),
    html.Div([],id='nodes_changed', style={'display': 'none'}),
    html.Div([],id='elements_changed', style={'display': 'none'}),
    html.Div([
        html.H1('LivestockFEM', style={'display': 'inline-block', 'margin-bottom':'0px','vertical-align': 'middle','padding-bottom':'0px'}),
        html.H6('A simple FEM calculation tool.', style={'display': 'inline-block', 'margin-bottom':'0px', 'margin-left':'8px','vertical-align': 'middle','padding':'0px'}),
        html.Div([
            dragndrop('Drag and Drop or ', 'Select Input File'),
            html.Div("",id='download-link-div',style={ 'width':'250px','display': 'inline-block','text-align':'center'}),
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

# Changes the text in the upload area when file is uploaded
@app.callback(Output(component_id='download-link-div', component_property='children'),
              [Input(component_id='upload-data', component_property='contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output(list_of_contents, name, modif):
    if list_of_contents is not None:
        name=name.replace('input_file','result_file')
        if not 'result_file' in name:
            name=name.replace(".json","")+"_result_file.json"
        child=html.Div(html.A('Download Result File',id='download-link',download=name,href="",target="_blank",
            style={ 'width': '200px',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '10px',
                    'textAlign': 'center',
                    'margin': '0px',
                    'display': 'inline-block',
                    'overflow-y': 'auto',
                    'white-space':'nowrap',
                    'padding':'0px',
                    'border-color':'black'}))
        return child


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
               Input(component_id='plotHeight', component_property='value'),
               Input(component_id='GloVar_json_changed', component_property='children')
               ],
              [State(component_id='GloVar_json', component_property='children')])
def update_output(defVal, forVal, vfil,plotHeight,jsonStr_new, jsonStr):
    start = timeit.default_timer()
    if len(jsonStr_new)==2:
        jsonStr=jsonStr_new
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

# ----MATRIX TAB-------------------------------------------------------------------------------------------------------------

@app.callback(Output('hover-data-matrix', 'children'),
    [Input('FEM-Plot', 'hoverData')],
    [State('GloVar_json', 'children')])
def display_hover_data(hoverData,jsonStr):
    resJson=json.loads(jsonStr[1])
    try:
        matrix2=[]
        elementNo=hoverData["points"][0]["customdata"]
        dofs=resJson["ElementStiffnessSmall"][elementNo][0][1:]
        matrix2.append(html.P("Current Element: "+ str(elementNo) + "\n"))
        matrix2.append(html.P("Element Degrees of Freedom: " + " ".join([str(int(dof)) for dof in dofs]) + "\n"))
        matrix2.append(html.Details([html.Summary('View explanation (Degrees of Freedom)'), html.Div([
            html.Div("Each element has 6 degrees of freedom, 3 at each node, movement in the X-direction and the Y-direction along with clockwise rotation around the node. If two elements share a degree of freedom they will not be able to move or rotate independendant of each other."),
            html.Img(src=app.get_asset_url('dof_nohinge_alpha.png')),
            html.Div("If a hinge is added then an additional rotational degree of freedom is added to the node, this means the elements can rotate independant of each other around the node."),
            html.Img(src=app.get_asset_url('dof_yeshinge_alpha.png')),
            ])],style={'backgroundColor':'#e8e8e8','borderWidth': '1px','borderStyle': 'solid','borderRadius': '2px'}))
        matrix2.append(html.Br())
        matrix2.append(html.B("Element Stiffness Matrix:"))
        matrix2.append(html.P("Each row and column represents its Degree of Freedom (DOF), in local coordinate system."))
        matrix2.append(html.Pre(matrixToHtml(resJson["ElementStiffnessSmallLocal"],hoverData,dofs,True,False)))
        matrix2.append(html.P("Transformed to global coordinate system:"))
        matrix2.append(html.Pre(matrixToHtml(resJson["ElementStiffnessSmall"],hoverData,dofs,True,False)))
        matrix2.append(html.Details([html.Summary('View explanation (Element Stiffness Matrix)'), html.Div([
            html.Div("An element stiffness matrix for the local coordinate system, k_local, can be put up column- and rowvise by setting a node displacement = 1 and the rest of node displacements = 0, as shown in the two examples below."),
            html.Img(src=app.get_asset_url('elestiff_ex.png'),style={'width':'40%'}),
            html.Div("The results from the figure above can then be set up in the local element stiffness matrix. "),
            html.Img(src=app.get_asset_url('elestiff_mat.png'),style={'width':'30%'}),
            html.Div("The local stiffness matrix is then transformed to global coordinate system, k, as shown below.\nThe transformation vector A is defined from the normalized (vector where the length equals 1) direction vector of the element, n, the direction vector is found by subtracting the first node from the second, and normalized by dividing it by lenght of the vector."),
            html.Img(src=app.get_asset_url('transform_mat.png'),style={'width':'15%'}),
            ])],style={'backgroundColor':'#e8e8e8','borderWidth': '1px','borderStyle': 'solid','borderRadius': '2px'}))
        matrix2.append(html.Br())
        matrix2.append(html.B("Element Stiffness Matrix Expanded:"))
        matrix2.append(html.P("The Element Stiffness Matrix is expanded to the size of the System Stiffness Matrix based on the degrees of freedom."))
        matrix2.append(html.Details([html.Summary('View Expanded Element Stiffness Matrix'), html.Pre(matrixToHtml(resJson["ElementStiffnessExpanded"],hoverData,dofs,True,True))],style={'backgroundColor':'#e8e8e8','borderWidth': '1px','borderStyle': 'solid','borderRadius': '2px'}))
        matrix2.append(html.Details([html.Summary('View explanation (Expanded Element Stiffness Matrix)'), html.Div([
            html.Div("The element stiffness matrix is expanded to the size of the system stiffness matrix, which have size N x N where N is the total of amount degrees of freedom in the system times.\nIn the unexpanded element stiffness matrix each row and column represents a degree of freedom, each cell of the matrix is insert in the expanded matrix based on the degree of freedom. \nThis expansion can be seen in example below, please note the example only contains 4 degrees of freedom per element, but principle is the same."),
            html.Img(src=app.get_asset_url('expan_ex_1.png')),
            html.Div("Looking at element 2, this element has the degrees of freedom: 1,2,5 and 6, there is 6 degrees of freedom in the system, this means the rows 3 and 4 along with columns 3 and 4 will be left empty (filled with 0) in the expanded matrix."),
            html.Img(src=app.get_asset_url('expan_ex_2.png')),
            ])],style={'backgroundColor':'#e8e8e8','borderWidth': '1px','borderStyle': 'solid','borderRadius': '2px'}))
        matrix2.append(html.Br())
        matrix2.append(html.B("System Stiffness Matrix:"))
        matrix2.append(html.P("Adding the expanded Element Stiffness Matrixes together forms the System Stiffness Matrix."))
        matrix2.append(html.Details([html.Summary('View System Stiffness Matrix'), html.Pre(matrixToHtml(resJson["SystemStiffness"],hoverData,dofs,False,True))],style={'backgroundColor':'#e8e8e8','borderWidth': '1px','borderStyle': 'solid','borderRadius': '2px'}))
        matrix2.append(html.Details([html.Summary('View explanation (Expanded System Stiffness Matrix)'), html.Div([
            html.Div("The system stiffness matrix, are simply the sum of all the expanded element stiffness matrix. This can be illustrated with the previous example."),
            html.Img(src=app.get_asset_url('expan_ex_1.png')),
            html.Img(src=app.get_asset_url('expan_ex_3.png')),
            ])],style={'backgroundColor':'#e8e8e8','borderWidth': '1px','borderStyle': 'solid','borderRadius': '2px'}))
        matrix2.append(html.Pre("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"))
    except:
        matrix2 = ""
    return matrix2

# ----NODES TAB-------------------------------------------------------------------------------------------------------------

@app.callback(Output('click-data-nodes', 'children'),
    [Input('FEM-Plot', 'clickData')])
def display_click_data(clickData):
    if not clickData is None:
        nodeTab=[]
        if "customdata" in clickData["points"][0] and clickData["points"][0]["customdata"]=='isnode':
            nodeNo=clickData["points"][0]["pointNumber"]
            nodeTab.append(html.Div("Current Node: "+ str(nodeNo),id='nodenumber'))
            nodeTab.append(html.Br())
            nodeTab.append(html.Div([
                html.Div(html.B("Coordinates:")),
                html.Div([
                    html.Div("X:",style={'width': '100px', 'display': 'inline-block'}),
                    html.Div(dcc.Input(id="nodeX",type='number',value=None,style={'text-align': 'right','width':'150px'}),id="nodeXdiv",style={'display': 'inline-block'})]),
                html.Div([
                    html.Div("Y:",style={'width': '100px', 'display': 'inline-block'}),
                    html.Div(dcc.Input(id="nodeY",type='number',value=None,style={'text-align': 'right','width':'150px'}),id="nodeYdiv",style={'display': 'inline-block'})])
                ],style={'width':'350px','display': 'inline-block'}))
            nodeTab.append(html.Div([
                html.Div(html.B("Loads: ")),
                html.Div([
                    html.Div("X-direction:",style={'width': '100px', 'display': 'inline-block'}),
                    html.Div(dcc.Input(id="loaddirX",type='number',value=None,style={'text-align': 'right', 'width':'150px'}),id='loaddirXdiv',style={'display': 'inline-block'}),
                    html.Div("N",style={'display': 'inline-block'})]),
                html.Div([
                    html.Div("Y-direction:",style={'width': '100px', 'display': 'inline-block'}),
                    html.Div(dcc.Input(id="loaddirY",type='number',value=None,style={'text-align': 'right', 'width':'150px'}),id='loaddirYdiv',style={'display': 'inline-block'}),
                    html.Div("N",style={'display': 'inline-block'})])
                ],style={'width':'350px','display': 'inline-block'}))
            nodeTab.append(html.Div([
                html.Div(html.B("Supports: ")),
                html.Div(dcc.Checklist(id='supportCheck',options=[{'label': 'X', 'value': 'X'},{'label': 'Y', 'value': 'Y'},{'label': 'Rotation', 'value': 'R'}],values=[]),id="supportsDiv")
                ],style={'width':'350px','display': 'inline-block'}))
            nodeTab.append(html.Br())
            nodeTab.append(html.Br())
            nodeTab.append(html.Div(html.Button('Apply Changes',id='applynode')))
        return nodeTab

@app.callback(Output('nodeXdiv', 'children'),
    [Input('FEM-Plot', 'clickData')])
def update_x_input(clickData):
    return dcc.Input(id="nodeX",type='number',value=clickData["points"][0]["x"],style={'text-align': 'right','width':'150px'})

@app.callback(Output('nodeYdiv', 'children'),
    [Input('FEM-Plot', 'clickData')])
def update_x_input(clickData):
    return dcc.Input(id="nodeY",type='number',value=clickData["points"][0]["y"],style={'text-align': 'right','width':'150px'})

@app.callback(Output('loaddirXdiv', 'children'),
    [Input('FEM-Plot', 'clickData')],
    [State('GloVar_json', 'children'),
    State('GloVar_json_changed', 'children')])
def update_x_input(clickData,jsonStr,jsonStr_new):
    if len(jsonStr_new)==2:
        jsonStr=jsonStr_new
    inJson=json.loads(jsonStr[0])
    loads=np.array(inJson["PyNodeLoad"]).T
    nodedof=float(clickData["points"][0]["pointNumber"]*3)
    if nodedof in loads[0]:
        size=loads[1][loads[0].tolist().index(nodedof)]
        return dcc.Input(id="loaddirX",type='number',value=size,style={'text-align': 'right', 'width':'150px'})
    else:
        return dcc.Input(id="loaddirX",type='number',value=0.0,style={'text-align': 'right', 'width':'150px'})

@app.callback(Output('loaddirYdiv', 'children'),
    [Input('FEM-Plot', 'clickData')],
    [State('GloVar_json', 'children'),
    State('GloVar_json_changed', 'children')])
def update_x_input(clickData,jsonStr,jsonStr_new):
    if len(jsonStr_new)==2:
        jsonStr=jsonStr_new
    inJson=json.loads(jsonStr[0])
    loads=np.array(inJson["PyNodeLoad"]).T
    nodedof=float(clickData["points"][0]["pointNumber"]*3+1)
    if nodedof in loads[0]:
        size=loads[1][loads[0].tolist().index(nodedof)]
        return dcc.Input(id="loaddirY",type='number',value=size,style={'text-align': 'right', 'width':'150px'})
    else:
        return dcc.Input(id="loaddirY",type='number',value=0.0,style={'text-align': 'right', 'width':'150px'})

@app.callback(Output('supportsDiv', 'children'),
    [Input('FEM-Plot', 'clickData')],
    [State('GloVar_json', 'children'),
    State('GloVar_json_changed', 'children')])
def update_x_input(clickData,jsonStr,jsonStr_new):
    if len(jsonStr_new)==2:
        jsonStr=jsonStr_new
    inJson=json.loads(jsonStr[0])
    supports=inJson["PySupport"]
    nodedofx=clickData["points"][0]["pointNumber"]*3
    nodedofy=clickData["points"][0]["pointNumber"]*3+1
    nodedofrot=clickData["points"][0]["pointNumber"]*3+2
    val=[]
    if nodedofx in  supports:
        val.append('X')
    if nodedofy in  supports:
        val.append('Y')
    if nodedofrot in  supports:
        val.append('R')
    check=dcc.Checklist(
        id='supportCheck',
        options=[
            {'label': 'X', 'value': 'X'},
            {'label': 'Y', 'value': 'Y'},
            {'label': 'Rotation', 'value': 'R'}
        ],
        values=val
    )
    return check

@app.callback(Output(component_id='nodes_changed', component_property='children'),
                [Input(component_id='applynode', component_property='n_clicks')],
                [
                State(component_id='nodenumber', component_property='children'),
                State(component_id='nodeX', component_property='value'),
                State(component_id='nodeY', component_property='value'),
                State(component_id='loaddirX', component_property='value'),
                State(component_id='loaddirY', component_property='value'),
                State(component_id='supportCheck', component_property='values'),
                State(component_id='GloVar_json', component_property='children'),
                State(component_id='GloVar_json_changed', component_property='children')
                ])
def update_output(n_clicks,nodenumber,nodeX,nodeY,loaddirX,loaddirY,supportCheck,jsonStr_ori,jsonStr_new):
    if len(jsonStr_new) == 0:
        inJson=json.loads(jsonStr_ori[0])
    else:
        inJson=json.loads(jsonStr_new[0])
    nodeInt=int(nodenumber.replace("Current Node: ",""))
    scale=inJson["UnitScaling"]
    inJson["PyNodes"][nodeInt]=[nodeX/scale,nodeY/scale]
    loaddoflist=(np.array(inJson['PyNodeLoad']).T[0]).tolist()

    if not nodeInt*3 in loaddoflist and float(loaddirX) != 0.0:
        inJson['PyNodeLoad'].append([nodeInt*3,float(loaddirX)])
    elif nodeInt*3 in loaddoflist and float(loaddirX) == 0.0:
        inJson['PyNodeLoad'].pop(loaddoflist.index(nodeInt*3))
    elif nodeInt*3 in loaddoflist:
        inJson['PyNodeLoad'][loaddoflist.index(nodeInt*3)]=[nodeInt*3,float(loaddirX)]

    if not nodeInt*3+1 in loaddoflist and float(loaddirY) != 0.0:
        inJson['PyNodeLoad'].append([nodeInt*3+1,float(loaddirY)])
    elif nodeInt*3+1 in loaddoflist and float(loaddirY) == 0.0:
        inJson['PyNodeLoad'].pop(loaddoflist.index(nodeInt*3+1))
    elif nodeInt*3+1 in loaddoflist:
        inJson['PyNodeLoad'][loaddoflist.index(nodeInt*3+1)]=[nodeInt*3+1,float(loaddirY)]

    if len(inJson['PyNodeLoad'])==0:
        inJson['PyNodeLoad']=[[0,0.0]]

    if nodeInt*3 not in inJson['PySupport'] and 'X' in supportCheck:
        inJson['PySupport'].append(nodeInt*3)
    elif nodeInt*3 in inJson['PySupport'] and 'X' not in supportCheck:
        inJson['PySupport'].remove(nodeInt*3)
    if nodeInt*3+1 not in inJson['PySupport'] and 'Y' in supportCheck:
        inJson['PySupport'].append(nodeInt*3+1)
    elif nodeInt*3+1 in inJson['PySupport'] and 'Y' not in supportCheck:
        inJson['PySupport'].remove(nodeInt*3+1)
    if nodeInt*3+2 not in inJson['PySupport'] and 'R' in supportCheck:
        inJson['PySupport'].append(nodeInt*3+2)
    elif nodeInt*3+2 in inJson['PySupport'] and 'R' not in supportCheck:
        inJson['PySupport'].remove(nodeInt*3+2)

    inJson['PySupport']=sorted(inJson['PySupport'])
    return [json.dumps(inJson)]

# ----ELEMENTS TAB-------------------------------------------------------------------------------------------------------------

@app.callback(Output('click-data-elements', 'children'),
    [Input('FEM-Plot', 'clickData')],
    [State('GloVar_json', 'children'),
    State('GloVar_json_changed', 'children')])
def display_click_data(clickData,jsonStr,jsonStr_new):
    if len(jsonStr_new)==2:
        jsonStr=jsonStr_new

    inJson=json.loads(jsonStr[0])
    units={
        '0.001':'km',
        '1.0':'m',
        '10.0':'dm',
        '100.0':'cm',
        '1000.0':'mm'
        }
    inJson=json.loads(jsonStr[0])
    unit=units[str(inJson["UnitScaling"])]

    elementTab=[]
    if not clickData is None:
        resJson=json.loads(jsonStr[1])
        if "customdata" in clickData["points"][0] and clickData["points"][0]["customdata"]!='isnode':
            elementNo=clickData["points"][0]["customdata"]
            elementTab.append(html.Div("Current Element: "+ str(elementNo),id='elenumber'))
            elementTab.append(html.Br())
            elementTab.append(html.Div([
                html.Div(html.B("Nodes:")),
                html.Div([
                    html.Div("Start Node:",style={'width': '100px', 'display': 'inline-block'}),
                    html.Div(dcc.Input(id="stNo",type='number',value=None,style={'text-align': 'right', 'width':'150px'}),id="eleStart",style={'display': 'inline-block'})]),
                html.Div([
                    html.Div("End Node:",style={'width': '100px', 'display': 'inline-block'}),
                    html.Div(dcc.Input(id="enNo",type='number',value=None,style={'text-align': 'right', 'width':'150px'}),id="eleEnd",style={'display': 'inline-block'})])
            ],style={'width':'350px','display': 'inline-block','height':'150px','vertical-align': 'top'}))
            elementTab.append(html.Div([
                html.Div(html.B("Loads: ")),
                html.Div([
                    html.Div("X-direction:",style={'width': '100px', 'display': 'inline-block'}),
                    html.Div(dcc.Input(id="eleXdir",type='number',value=None,style={'text-align': 'right', 'width':'150px'}),id='eleXdirdiv',style={'display': 'inline-block'}),
                    html.Div("N/m",style={'display': 'inline-block'})]),
                html.Div([
                    html.Div("Y-direction:",style={'width': '100px', 'display': 'inline-block'}),
                    html.Div(dcc.Input(id="eleYdir",type='number',value=None,style={'text-align': 'right', 'width':'150px'}),id='eleYdirdiv',style={'display': 'inline-block'}),
                    html.Div("N/m",style={'display': 'inline-block'})]),
                html.Div(dcc.RadioItems(
                    id='localglobal',
                    options=[
                        {'label': 'Local Coordinates (X-axis parallel to element)', 'value': 'local'},
                        {'label': 'Global Coordines', 'value': 'global'},
                    ],
                    value='local',
                ))
                ],style={'width':'350px','display': 'inline-block','height':'150px','vertical-align': 'top'}))
            elementTab.append(html.Div([
                html.Div(html.B("Beam Parameters: ")),
                html.Div([
                    html.Div("Section Area:",style={'width': '130px', 'display': 'inline-block'}),
                    html.Div(dcc.Input(id="sarea",type='number',value=None,style={'text-align': 'right', 'width':'150px'}),id="areaDiv",style={'display': 'inline-block'}),
                    html.Div(unit+'2',style={'display': 'inline-block'})]),
                html.Div([
                    html.Div("Moment of inertia:",style={'width': '130px', 'display': 'inline-block'}),
                    html.Div(dcc.Input(id="inert",type='number',value=None,style={'text-align': 'right', 'width':'150px'}),id="inertiaDiv",style={'display': 'inline-block'}),
                    html.Div(unit+'4',style={'display': 'inline-block'})]),
                html.Div([html.Div("E-modulus:",style={'width': '130px', 'display': 'inline-block'}),
                    html.Div(dcc.Input(id="emod",type='number',value=None,style={'text-align': 'right', 'width':'150px'}),id="emodulusDiv",style={'display': 'inline-block'}),
                    html.Div("Pa",style={'display': 'inline-block'})])
                ],style={'width':'350px','display': 'inline-block','height':'150px','vertical-align': 'top'}))
            elementTab.append(html.Br())
            elementTab.append(html.Br())
            elementTab.append(html.Div(html.Button('Apply Changes',id='applyelement')))
    return elementTab

@app.callback(Output('eleStart', 'children'),
    [Input('FEM-Plot', 'clickData')],
    [State('GloVar_json', 'children'),
    State('GloVar_json_changed', 'children')])
def update_x_input(clickData,jsonStr,jsonStr_new):
    if len(jsonStr_new)==2:
        jsonStr=jsonStr_new
    inJson=json.loads(jsonStr[0])
    if "customdata" in clickData["points"][0] and clickData["points"][0]["customdata"]!='isnode':
        elements=inJson["PyElements"]
        eleNo=clickData["points"][0]["customdata"]
        return dcc.Input(id="stNo",type='number',value=elements[eleNo][0],style={'text-align': 'right', 'width':'150px'})

@app.callback(Output('eleEnd', 'children'),
    [Input('FEM-Plot', 'clickData')],
    [State('GloVar_json', 'children'),
    State('GloVar_json_changed', 'children')])
def update_x_input(clickData,jsonStr,jsonStr_new):
    if len(jsonStr_new)==2:
        jsonStr=jsonStr_new
    inJson=json.loads(jsonStr[0])
    if "customdata" in clickData["points"][0] and clickData["points"][0]["customdata"]!='isnode':
        elements=inJson["PyElements"]
        eleNo=clickData["points"][0]["customdata"]
        return dcc.Input(id="enNo",type='number',value=elements[eleNo][1],style={'text-align': 'right', 'width':'150px'})

@app.callback(Output('eleXdirdiv', 'children'),
    [Input('FEM-Plot', 'clickData'),
    Input('localglobal','value')],
    [State('GloVar_json', 'children'),
    State('GloVar_json_changed', 'children')])
def update_x_input(clickData,localglobal,jsonStr,jsonStr_new):
    if len(jsonStr_new)==2:
        jsonStr=jsonStr_new
    inJson=json.loads(jsonStr[0])
    if "customdata" in clickData["points"][0] and clickData["points"][0]["customdata"]!='isnode':
        elements=inJson["PyElements"]
        eleNo=clickData["points"][0]["customdata"]
        load=np.round(np.array(inJson['PyElementLoad']))[eleNo]
        if localglobal=='global':
            if load[0]==0.0 and load[1]==0.0:
                return dcc.Input(id="eleXdir",type='number',value=0.0,style={'text-align': 'right', 'width':'150px'})
            nodes=np.array(inJson['PyNodes'])[elements[eleNo]]
            v = nodes[1]-nodes[0]
            if v[0]==0 and v[1]>0:
                ang = math.pi/2
            elif v[0]==0 and v[1]<0:
                ang = -math.pi/2
            else:
                ang = math.atan(v[1]/v[0])
            x=load[0]
            y=load[1]
            load[0]=x*math.cos(ang)-y*math.sin(ang)
            load[1]=x*math.sin(ang)+y*math.cos(ang)
            return dcc.Input(id="eleXdir",type='number',value=round(load[0]),style={'text-align': 'right', 'width':'150px'})
        else:
            return dcc.Input(id="eleXdir",type='number',value=load[0],style={'text-align': 'right', 'width':'150px'})

@app.callback(Output('eleYdirdiv', 'children'),
    [Input('FEM-Plot', 'clickData'),
    Input('localglobal','value')],
    [State('GloVar_json', 'children'),
    State('GloVar_json_changed', 'children')])
def update_x_input(clickData,localglobal,jsonStr,jsonStr_new):
    if len(jsonStr_new)==2:
        jsonStr=jsonStr_new
    inJson=json.loads(jsonStr[0])
    if "customdata" in clickData["points"][0] and clickData["points"][0]["customdata"]!='isnode':
        elements=inJson["PyElements"]
        eleNo=clickData["points"][0]["customdata"]
        load=np.round(np.array(inJson['PyElementLoad']))[eleNo]
        if localglobal=='global':
            if load[0]==0.0 and load[1]==0.0:
                return dcc.Input(id="eleXdir",type='number',value=0.0,style={'text-align': 'right', 'width':'150px'})
            nodes=np.array(inJson['PyNodes'])[elements[eleNo]]
            v = nodes[1]-nodes[0]
            if v[0]==0 and v[1]>0:
                ang = math.pi/2
            elif v[0]==0 and v[1]<0:
                ang = -math.pi/2
            else:
                ang = math.atan(v[1]/v[0])
            x=load[0]
            y=load[1]
            load[0]=x*math.cos(ang)-y*math.sin(ang)
            load[1]=x*math.sin(ang)+y*math.cos(ang)
            return dcc.Input(id="eleYdir",type='number',value=round(load[1]),style={'text-align': 'right', 'width':'150px'})
        else:
            return dcc.Input(id="eleYdir",type='number',value=load[1],style={'text-align': 'right', 'width':'150px'})

@app.callback(Output('areaDiv', 'children'),
    [Input('FEM-Plot', 'clickData')],
    [State('GloVar_json', 'children'),
    State('GloVar_json_changed', 'children')])
def update_x_input(clickData,jsonStr,jsonStr_new):
    if len(jsonStr_new)==2:
        jsonStr=jsonStr_new
    inJson=json.loads(jsonStr[0])
    if "customdata" in clickData["points"][0] and clickData["points"][0]["customdata"]!='isnode':
        materials=inJson["PyMaterial"]
        scale=inJson["UnitScaling"]
        eleNo=clickData["points"][0]["customdata"]
        mat=materials[eleNo][1]*(scale**2)
        return dcc.Input(id="sarea",type='number',value=mat,style={'text-align': 'right', 'width':'150px'})

@app.callback(Output('inertiaDiv', 'children'),
    [Input('FEM-Plot', 'clickData')],
    [State('GloVar_json', 'children'),
    State('GloVar_json_changed', 'children')])
def update_x_input(clickData,jsonStr,jsonStr_new):
    if len(jsonStr_new)==2:
        jsonStr=jsonStr_new
    inJson=json.loads(jsonStr[0])
    if "customdata" in clickData["points"][0] and clickData["points"][0]["customdata"]!='isnode':
        materials=inJson["PyMaterial"]
        scale=inJson["UnitScaling"]
        eleNo=clickData["points"][0]["customdata"]
        mat=materials[eleNo][2]*(scale**4)
        return dcc.Input(id="inert",type='number',value=mat,style={'text-align': 'right', 'width':'150px'})

@app.callback(Output('emodulusDiv', 'children'),
    [Input('FEM-Plot', 'clickData')],
    [State('GloVar_json', 'children'),
    State('GloVar_json_changed', 'children')])
def update_x_input(clickData,jsonStr,jsonStr_new):
    if len(jsonStr_new)==2:
        jsonStr=jsonStr_new
    inJson=json.loads(jsonStr[0])
    if "customdata" in clickData["points"][0] and clickData["points"][0]["customdata"]!='isnode':
        materials=inJson["PyMaterial"]
        eleNo=clickData["points"][0]["customdata"]
        return dcc.Input(id="emod",type='number',value=materials[eleNo][0],style={'text-align': 'right', 'width':'150px'})

@app.callback(Output(component_id='elements_changed', component_property='children'),
                [Input(component_id='applyelement', component_property='n_clicks')],
                [
                State(component_id='elenumber', component_property='children'),
                State(component_id='stNo', component_property='value'),
                State(component_id='enNo', component_property='value'),
                State(component_id='eleXdir', component_property='value'),
                State(component_id='eleYdir', component_property='value'),
                State(component_id='localglobal', component_property='value'),
                State(component_id='sarea', component_property='value'),
                State(component_id='inert', component_property='value'),
                State(component_id='emod', component_property='value'),
                State(component_id='GloVar_json', component_property='children'),
                State(component_id='GloVar_json_changed', component_property='children')
                ])
def update_output(n_clicks,elenumber,stNo,enNo,eleXdir,eleYdir,localglobal,sarea,inert,emod,jsonStr_ori,jsonStr_new):
    if len(jsonStr_new) == 0:
        inJson=json.loads(jsonStr_ori[0])
    else:
        inJson=json.loads(jsonStr_new[0])

    eleInt=int(elenumber.replace("Current Element: ",""))
    scale=inJson["UnitScaling"]

    inJson["PyElements"][eleInt]=[stNo,enNo]

    if localglobal == 'local':
        inJson['PyElementLoad'][eleInt]=[eleXdir,eleYdir]
    else:
        if float(eleXdir)==0.0 and float(eleYdir)==0.0:
            inJson['PyElementLoad'][eleInt]=[0.0,0.0]
        else:
            nodes=np.array(inJson['PyNodes'])[inJson["PyElements"][eleInt]]
            v = nodes[1]-nodes[0]
            if v[0]==0 and v[1]>0:
                ang = -math.pi/2
            elif v[0]==0 and v[1]<0:
                ang = math.pi/2
            else:
                ang = -math.atan(v[1]/v[0])
            load=[eleXdir,eleYdir]
            x,y=load
            load[0]=x*math.cos(ang)-y*math.sin(ang)
            load[1]=x*math.sin(ang)+y*math.cos(ang)
            inJson['PyElementLoad'][eleInt]=load

    inJson['PyMaterial'][eleInt]=[emod,sarea/(scale**2),inert/(scale**4)]
    return [json.dumps(inJson)]

# ----UPDATE DICTIONARY-------------------------------------------------------------------------------------------------------------
@app.callback(Output(component_id='GloVar_json_changed', component_property='children'),
                [
                Input(component_id='nodes_changed', component_property='children'),
                Input(component_id='elements_changed', component_property='children')
                ],
                [
                State(component_id='GloVar_json', component_property='children'),
                State(component_id='GloVar_json_changed', component_property='children')
                ])
def update_dict(nodes_changed,elements_changed,jsonStr_ori,jsonStr_new):
    if len(jsonStr_ori) == 0:
        return []
    if len(jsonStr_new) == 0:
        inJson=json.loads(jsonStr_ori[0])
    else:
        inJson=json.loads(jsonStr_new[0])

    if len(nodes_changed)==1:
        nodeDict=json.loads(nodes_changed[0])
        for key in nodeDict:
            if key in ['PyNodes','PyNodeLoad','PySupport']:
                inJson[key]=nodeDict[key]

    if len(elements_changed)==1:
        elementDict=json.loads(elements_changed[0])
        for key in elementDict:
            if key in ['PyElements','PyElementLoad','PyMaterial']:
                inJson[key]=elementDict[key]

    resultDict = FEM_frame(inJson).outDict
    return json.dumps(inJson), json.dumps(resultDict)

# ----RESULTS TAB-------------------------------------------------------------------------------------------------------------

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

# ----SUPPORTS TAB-------------------------------------------------------------------------------------------------------------

@app.callback(Output('supportTab', 'children'),
    [Input('GloVar_json_changed', 'children')],
    [State('GloVar_json', 'children')])
def update_output2(jsonStr_new,jsonStr_ori):
    if len(jsonStr_ori) == 0:
        return []
    if len(jsonStr_new) == 0:
        inJson=json.loads(jsonStr_ori[0])
        resJson=json.loads(jsonStr_ori[1])
    else:
        inJson=json.loads(jsonStr_new[0])
        resJson=json.loads(jsonStr_new[1])
    tableContent=[html.Tr([
                html.Th("Node No."),
                html.Th("X-reaction"),
                html.Th("Y-reaction"),
                html.Th("Moment-reaction")])]
    sumx=0
    sumy=0
    summ=0
    for i,nod in enumerate(inJson['PyNodes']):
        xrec=""
        yrec=""
        mrec=""
        if i*3 in inJson['PySupport']:
            reac=int(round(resJson['Reactions'][inJson['PySupport'].index(i*3)]))
            sumx+=reac
            xrec=str(reac)+" N"
        if i*3+1 in inJson['PySupport']:
            reac=int(round(resJson['Reactions'][inJson['PySupport'].index(i*3+1)]))
            sumy+=reac
            yrec=str(reac)+" N"
        if i*3+2 in inJson['PySupport']:
            reac=int(round(resJson['Reactions'][inJson['PySupport'].index(i*3+2)]))
            summ+=reac
            mrec=str(reac)+" Nm"
        if xrec=="" and yrec=="" and mrec=="":
            continue

        tableContent.append(
            html.Tr([
                html.Td(i,style={'text-align':'center'}),
                html.Td(xrec,style={'text-align':'right'}),
                html.Td(yrec,style={'text-align':'right'}),
                html.Td(mrec,style={'text-align':'right'}),
            ]))
    tableContent.append(
        html.Tr([
            html.Th("SUM",style={'text-align':'center'}),
            html.Th(sumx,style={'text-align':'right'}),
            html.Th(sumy,style={'text-align':'right'}),
            html.Th(summ,style={'text-align':'right'}),
        ]))

    tabDiv = html.Div([
        html.Details([
            html.Summary('View explanation (Supports and Reactions forces)'),
            html.Div([
                html.Div("There are 4 types of supports: Fixed, Pinned, Roller and Simple."),
                html.Div([
                    html.B("Fixed:"),
                    html.Br(),
                    html.Img(src=app.get_asset_url('fixed.png')),
                    html.Img(src=app.get_asset_url('fixed_reactions.png')),
                    html.P("""Fixed supports, also called rigid or cantilevered support, supports the structure in both the X-direction, Y-direction and against rotation (moments).
                    Making the structure unable to move up or down and side to side in the supported node, and prevents the structure from rotating around the node.\n
                    To prevent the structure from moving and rotating in the node, the support counter acts (reacts) on the forces (loads) applied to the structure.
                    Positive X-reactions means the structure would move left in the node if it was not supported. Positive Y-reactions means the structure will move downwards in the node if it was not supported.
                    Positive Moment-reactions means the structure will rotate clockwise around the node if it was not supported. This means the sum of the reactions in the Y-direction
                    for the entire system is equal to the sum of the loads in the Y-direction fot the system, the same is the case for reactions in the X-direction.\nExamples of real life fixed supports can be seen below.""",style={'width':'90%'}),
                    html.Img(src=app.get_asset_url('fixed_examples.png'))
                    ]),
                html.Div([
                    html.Br(),
                    html.B("Pinned:"),
                    html.Br(),
                    html.Img(src=app.get_asset_url('pinned.png')),
                    html.Img(src=app.get_asset_url('pinned_reactions.png')),
                    html.P("""Pinned supports, supports the structure in both the X-direction and Y-direction but not against rotation (moments). Making the structure unable to move up or down and side to side in the supported node,
                    but lets the structure rotate around the node.\nTo prevent the structure from moving, the suppport counter acts (reacts) on the forces (loads) applied to the structure.
                    As with the fixed support positive X-reactions means the structure would move left in the node if it was not supported and positive Y-reactions means the structure will move downwards in the node if it was not supported. \n
                    Examples of real life pinned supports can be seen below.""",style={'width':'90%'}),
                    html.Img(src=app.get_asset_url('pinned_examples.png'))
                    ]),
                html.Div([
                    html.Br(),
                    html.B("Roller:"),
                    html.Br(),
                    html.Img(src=app.get_asset_url('roller.png')),
                    html.Img(src=app.get_asset_url('roller_reactions.png')),
                    html.P("""Roller supports, supports the structure in only one direction either the X-direction or the Y-direction and do not supports against rotation (moments).
                    Making the structure unable to move either up or down or side to side in the supported node, but lets the structure rotate around the node.\n
                    To prevent the structure from moving, the suppport counter acts (reacts) on the forces (loads) applied to the structure.
                    As with the fixed support positive X-reactions means the structure would move left in the node if it was not supported and positive Y-reactions means the structure will move downwards in the node if it was not supported.
                    Eventhough often illustrated as supports with wheels under it, it is rarely the case, instead it is mostly used for bridge bearings letting the move slightly back and forth to accomodate fluctuations and vibrations.\n
                    Examples of real life pinned supports can be seen below.""",style={'width':'90%'}),
                    html.Img(src=app.get_asset_url('roller_examples.png'))
                    ]),
                html.Div([
                    html.Br(),
                    html.B("Simple:"),
                    html.Br(),
                    html.Img(src=app.get_asset_url('simple.png')),
                    html.Img(src=app.get_asset_url('simple_reactions.png')),
                    html.P("""Simple support, rarely used, supports the structure in only one direction either the X-direction or the Y-direction and supports against rotation (moments).
                    Making the structure unable to move either up or down or side to side in the supported node, prevents the structure from rotating around the node. \n
                    As mentioned this is rarely used, the best example are unhinged shock absorber, hydraulic pumbs or elliptic springs like on a horse carriage, see example below, these makes the carriage only able to move up and down. """,style={'width':'90%'}),
                    html.Img(src=app.get_asset_url('simple_examples.png'))
                    ]),
            ])],
            style={'backgroundColor':'#e8e8e8','borderWidth': '1px','borderStyle': 'solid','borderRadius': '2px'}),
        html.Br(),
        html.Table(tableContent),
        html.Br(),
        html.Details([
            html.Summary('View explanation (Reactions calculations)'),
            html.Div([
                html.Div(html.Img(src=app.get_asset_url('dof_nohinge_alpha.png'))),
                html.P("""Looking at the example above, we got the system stiffness matrix K which can be seen below, to see how this is found go to the Matrix tab. \n
                From the K matrix the Kff is found by removing the rows and columns corresponding to the supported degrees of freedom (DOF),
                in this case node 1 and 4 are supported in X- and Y-direction, corresponding to DOF 1,2,10 and 11 these are therefore the rows and columns that are removed.\n
                The matrix Kuf (marked with blue) is found by taking the rows of supported DOF, 1,2,10 and 11, and removing the columns corresponding to the support DOF.\n
                We also have the load vector R which consist of the loads corresponding to the DOF, as we can see the only load in the system, is placed in DOF number 5, with the size P in the opposite direction of the DOF.
                For elementloads the reactions are calculated for the single elements, the reactions are then added to the load vector. By removing the supported DOFS, 1,2,10 and 11, we get the vector Rf.\n
                """,style={'width':'90%'}),
                html.Div(html.Img(src=app.get_asset_url('k_matrix.png'),style={'width':'800px'})),
                html.Div(html.Img(src=app.get_asset_url('kff_mat.png'),style={'width':'800px'})),
                html.Div(html.Img(src=app.get_asset_url('kuf_mat.png'),style={'width':'750px'})),
                html.Div(html.Img(src=app.get_asset_url('loadvec.png'),style={'width':'800px'})),
                html.P("""To find the reactions we first need to calculate the displacement in all the unsupported nodes, Vf, this is done by taking the inverse matrix of Kff and dot it witf Rf as seen below.\n
                The contribution from all the free DOFS to the reactions, Ru, is then found by taking the dot product of Kuf and Vf. To get the full reactions Ru are added together with discarded loads (the loads marked red) from the loadvector, R,
                this is only needed if any loads are acting directly on the supported DOF, which is not the case in this example.
                """,style={'width':'90%'}),
                html.Div(html.Img(src=app.get_asset_url('dispreac_calc.png'),style={'width':'800px'})),
            ])],
            style={'backgroundColor':'#e8e8e8','borderWidth': '1px','borderStyle': 'solid','borderRadius': '2px'}),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
    ])
    return tabDiv

# ----LOADS TAB-------------------------------------------------------------------------------------------------------------

@app.callback(Output('loadsTab', 'children'),
    [Input('GloVar_json_changed', 'children')],
    [State('GloVar_json', 'children')])
def update_output2(jsonStr_new,jsonStr_ori):
    if len(jsonStr_ori) == 0:
        return []
    if len(jsonStr_new) == 0:
        inJson=json.loads(jsonStr_ori[0])
        resJson=json.loads(jsonStr_ori[1])
    else:
        inJson=json.loads(jsonStr_new[0])
        resJson=json.loads(jsonStr_new[1])
    tableContent=[html.Tr([
                html.Th("Node No.",style={'text-align':'center'}),
                html.Th("X-load",style={'text-align':'right'}),
                html.Th("Y-load",style={'text-align':'right'}),
                html.Th("",style={'text-align':'right'}),
                html.Th("",style={'text-align':'right'}),
                html.Th("",style={'text-align':'right'}),
                html.Th("",style={'text-align':'right'}),
                html.Th("",style={'text-align':'right'}),
                ])]
    sumx=0
    sumy=0
    summ=0
    ldof=(np.array(inJson['PyNodeLoad'])[:,0]).tolist()
    lsize=(np.array(inJson['PyNodeLoad'])[:,1]).tolist()

    for i,nod in enumerate(inJson['PyNodes']):
        xload=""
        yload=""
        mload=""
        if i*3 in ldof:
            loadsize=int(round(inJson['PyNodeLoad'][ldof.index(i*3)][1]))
            sumx+=loadsize
            xload=str(loadsize)+" N"
        if i*3+1 in ldof:
            loadsize=int(round(inJson['PyNodeLoad'][ldof.index(i*3+1)][1]))
            sumy+=loadsize
            yload=str(loadsize)+" N"
        if xload=="" and yload=="" and mload=="":
            continue

        tableContent.append(
            html.Tr([
                html.Td(i,style={'text-align':'center'}),
                html.Td(xload,style={'text-align':'right'}),
                html.Td(yload,style={'text-align':'right'}),
                html.Td("",style={'text-align':'right'}),
                html.Td("",style={'text-align':'right'}),
                html.Td("",style={'text-align':'right'}),
                html.Td("",style={'text-align':'right'}),
                html.Td("",style={'text-align':'right'}),
            ]))
    tableContent.append(
        html.Tr([
            html.Th("SUM",style={'text-align':'center'}),
            html.Th(str(sumx)+" N",style={'text-align':'right'}),
            html.Th(str(sumy)+" N",style={'text-align':'right'}),
            html.Th("",style={'text-align':'right'}),
            html.Th("",style={'text-align':'right'}),
            html.Th("",style={'text-align':'right'}),
            html.Th("",style={'text-align':'right'}),
            html.Th("",style={'text-align':'right'}),
        ]))
    tableContent.append(
        html.Tr([
            html.Th("Element No.",style={'text-align':'center'}),
            html.Th("Global X-load*length",style={'text-align':'right'}),
            html.Th("Global Y-load*length",style={'text-align':'right'}),
            html.Th("Global X-load",style={'text-align':'right'}),
            html.Th("Global Y-load",style={'text-align':'right'}),
            html.Th("Local X-load",style={'text-align':'right'}),
            html.Th("Local Y-load",style={'text-align':'right'}),
            html.Th("Element Length",style={'text-align':'right'}),
            ]))
    sumxm=0
    sumym=0
    eleLoads=np.array(inJson['PyElementLoad'])
    for i,ele in enumerate(inJson['PyElements']):
        if np.linalg.norm(np.array(eleLoads)[i])==0.0:
            continue
        nodes=np.array(inJson['PyNodes'])[ele]
        elelength=np.linalg.norm(nodes[1]-nodes[0])
        load=eleLoads[i]
        localx=int(round(eleLoads[i][0]))
        localy=int(round(eleLoads[i][1]))

        v = nodes[1]-nodes[0]
        if v[0]==0 and v[1]>0:
            ang = math.pi/2
        elif v[0]==0 and v[1]<0:
            ang = -math.pi/2
        else:
            ang = math.atan(v[1]/v[0])
        x,y=load
        load[0]=x*math.cos(ang)-y*math.sin(ang)
        load[1]=x*math.sin(ang)+y*math.cos(ang)

        globalx=int(round(load[0]))
        globaly=int(round(load[1]))
        globalxm=int(round(load[0]*elelength))
        globalym=int(round(load[1]*elelength))

        sumxm+=globalxm
        sumym+=globalym

        tableContent.append(
            html.Tr([
                html.Td(i,style={'text-align':'center'}),
                html.Td("" if globalxm == 0 else str(globalxm)+" N",style={'text-align':'right'}),
                html.Td("" if globalym == 0 else str(globalym)+" N",style={'text-align':'right'}),
                html.Td("" if globalx == 0 else str(globalx)+" N/m",style={'text-align':'right'}),
                html.Td("" if globaly == 0 else str(globaly)+" N/m",style={'text-align':'right'}),
                html.Td("" if localx == 0 else str(localx)+" N/m",style={'text-align':'right'}),
                html.Td("" if localy == 0 else str(localy)+" N/m",style={'text-align':'right'}),
                html.Td(str(round(elelength,3))+" m",style={'text-align':'right'}),
            ]))
    tableContent.append(
        html.Tr([
            html.Th("SUM",style={'text-align':'center'}),
            html.Th(str(sumxm)+" N",style={'text-align':'right'}),
            html.Th(str(sumym)+" N",style={'text-align':'right'}),
            html.Th("",style={'text-align':'right'}),
            html.Th("",style={'text-align':'right'}),
            html.Th("",style={'text-align':'right'}),
            html.Th("",style={'text-align':'right'}),
            html.Th("",style={'text-align':'right'}),
        ]))
    tableContent.append(
        html.Tr([
            html.Th("TOTAL SUM",style={'text-align':'center'}),
            html.Th(str(sumxm+sumx)+" N",style={'text-align':'right'}),
            html.Th(str(sumym+sumy)+" N",style={'text-align':'right'}),
            html.Th("",style={'text-align':'right'}),
            html.Th("",style={'text-align':'right'}),
            html.Th("",style={'text-align':'right'}),
            html.Th("",style={'text-align':'right'}),
            html.Th("",style={'text-align':'right'}),
        ]))

    tabDiv = html.Div([
        html.Br(),
        html.Table(tableContent),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
    ])
    return tabDiv

# ----SAVE RESULTS FILE------------------------------------------------------------------------------------------------------------
@app.callback(
    dash.dependencies.Output('download-link', 'href'),
    [
    Input(component_id='defText', component_property='value'),
    Input(component_id='forText', component_property='value'),
    Input(component_id='GloVar_json_changed', component_property='children')
    ],
  [State(component_id='GloVar_json', component_property='children')])
def update_download_link(defVal,forVal,jsonStr_new, jsonStr):
    if len(jsonStr_new)==2:
        jsonStr=jsonStr_new
    if jsonStr is not None:
        jsonDict = json.loads(jsonStr[0])
        resultDict = json.loads(jsonStr[1])
        if not (jsonDict['PlotScalingDeformation'] == defVal and jsonDict['PlotScalingForces'] == forVal):
            jsonDict['PlotScalingDeformation'] = defVal
            jsonDict['PlotScalingForces'] = forVal
            resultDict = FEM_frame(jsonDict).outDict

    json_string = json.dumps(resultDict).replace(', "',',\n "').replace("{","{\n ").replace("}","\n}")
    json_string = "data:text/json;charset=utf-8,%EF%BB%BF" + quote(json_string)
    return json_string

if __name__ == '__main__':
    app.run_server(debug=True)
