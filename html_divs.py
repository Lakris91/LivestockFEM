import dash_core_components as dcc
import dash_html_components as html
import math

def dragndrop(text,linkText=''):
    dd = html.Div(
            dcc.Upload(
                id='upload-data',
                children=['\n','\n',text, html.A(linkText)],
                accept='.json',
                style={
                    'width': '700px',
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
                    'padding':'0px'
                },
            ),style={'display': 'inline-block'})
    return dd

def generateTabs():
    tab_height='40px'
    tabDef=html.Div([
    dcc.Tabs(id='tabs', value='nodes',style={'width':'1000px', 'height':tab_height,'font-size': '16px'}, children=[
    dcc.Tab(label='Nodes', value='nodes',style={'padding': '6px'},selected_style={'padding': '6px'}),
    dcc.Tab(label='Elements', value='elements',style={'padding': '6px'},selected_style={'padding': '6px'}),
    dcc.Tab(label='Supports', value='supports',style={'padding': '6px'},selected_style={'padding': '6px'}),
    dcc.Tab(label='Loads', value='loads',style={'padding': '6px'},selected_style={'padding': '6px'}),
    dcc.Tab(label='Matrix', value='matrix',style={'padding': '6px'},selected_style={'padding': '6px'}),
    dcc.Tab(label='Results', value='result',style={'padding': '6px'},selected_style={'padding': '6px'})
    ]),
    html.Div(id='tabs-content')
    ])
    return tabDef

def viewFilter(jsonDict):
    viewCheck = html.Div(
        [
            html.Div(
                [
                html.Div('View filter:',style={'display': 'inline-block','height':'30px'}),
                dcc.Checklist(
                    id='viewfilter',
                    options=[
                        {'label': 'Nodes', 'value': 'Nodes'},
                        {'label': 'Elements', 'value': 'Elements'},
                        {'label': 'Supports', 'value': 'SupportViz'},
                        {'label': 'Hinges', 'value': 'HingeViz'},
                        {'label': 'Node Loads','value': 'NodeloadViz'},
                        {'label': 'Element Loads','value': 'ElementloadViz'},
                        {'label': 'Deformation', 'value': 'DOFPlot'},
                        {'label': 'Normal Forces', 'value': 'ForcePlot1'},
                        {'label': 'Shear Forces', 'value': 'ForcePlot2'},
                        {'label': 'Bending Moments', 'value': 'ForcePlot3'}],
                    values=['Nodes','Elements','SupportViz','HingeViz','NodeloadViz','ElementloadViz','DOFPlot'],
                    labelStyle={'display': 'inline-block'},
                )
                ],
                style={ 'width': '55%','display': 'inline-block','height':'60px','vertical-align': 'middle', 'padding':'1px'}
            ),
            html.Div(
                [
                html.Div('Deformation View Scale:',style={'borderStyle': 'line','height':'30px'}),
                dcc.Input(id='defText', type='number',value=jsonDict['PlotScalingDeformation'], selectionDirection='forward', debounce=True , style={'height':'25px'})
                ],
                style={'display': 'inline-block','height':'60px','vertical-align': 'middle', 'padding':'1px'},
            ),
            html.Div(
                [
                html.Div('Forces/Loads View Scale:',style={'borderStyle': 'line','height':'30px'}),
                dcc.Input(id='forText', type='number',value=jsonDict['PlotScalingForces'],step=10**-math.ceil(math.log10(1/jsonDict['PlotScalingForces'])), selectionDirection='forward',debounce=True, style={'height':'25px'} )
                ],
                style={'display': 'inline-block','height':'60px','vertical-align': 'middle', 'padding':'1px'},
            ),
            html.Div(
                [
                html.Div('Plot Size:',style={'display': 'inline-block','height':'30px'}),
                html.Div(dcc.Slider(id='plotHeight', min=50, max=1200, value=350, step=50))
                ],
                style={'display': 'inline-block','width': '12%','height':'60px','vertical-align': 'middle', 'padding':'1px', 'padding-left':'15px'},
            )
        ],
    )
    return viewCheck

def tab1():
    tabDiv = html.Div([
        dcc.Markdown("**Click on a node to see information.**"),
        html.Div(id='click-data-nodes')
        ])
    return tabDiv

def tab2():
    tabDiv = html.Div([
        dcc.Markdown("**Click on an element to see information.**"),
        html.Div(id='click-data-elements')
        ])
    return tabDiv

def tab3():
    tabDiv= html.Div([
            html.H3('This is tab3')
            ])
    return tabDiv

def tab4():
    tabDiv= html.Div([
                html.H3('This is tab6'),
                html.Table([
                    html.Tr([
                        html.Th("Firstname"),
                        html.Th(""),
                        html.Th(""),
                    ],style={'padding': '0px'}),
                    html.Tr([
                        html.Td("Jill"),
                        html.Td("Amith"),
                        html.Td("13"),
                    ],style={'padding': '0px'}),
                    html.Tr([
                        html.Td("Jack"),
                        html.Td("Lastname",style={'padding': '0px'}),
                        html.Td("20",style={'padding': '0px'}),
                    ])
                ])
            ])
    return tabDiv

def tab5():
    tabDiv = html.Div([
        dcc.Markdown("**Hover the mouse over an element to see it's stiffness Matrix.**"),
        html.Div(id='hover-data-matrix',style={'overflow-x':'auto'})
        ])
    return tabDiv

def tab6():
    tabDiv=html.Div([
        dcc.Dropdown(
            id='result-dropdown',
            options=[
                {'label': 'Overview', 'value': 'overview'},
                {'label': 'Displacements', 'value': 'Displacements'},
                {'label': 'Bending Moments', 'value': 'MomentForcesPt'},
                {'label': 'Normal Forces', 'value': 'NormalForce1'},
                {'label': 'Shear Forces', 'value': 'ShearForce2'}
            ],
            value='overview',
            clearable=False,
            style={'width':'1000px'}
        ),
        html.Div(id='results-div',children=["Test"])
    ])
    return tabDiv

def resultsDiv(resJson):
    if value=='overview':
        resDiv = html.Div([
            html.H3('Results overview:'),
            html.Table([
                html.Tr([
                    html.Td("Max Displacement:"),
                    html.Td("1565",style={'textAlign':'right'}),
                ],style={'padding': '0px'}),
                html.Tr([
                    html.Td("Max Absolute Bending Moment:"),
                    html.Td("1234",style={'textAlign':'right'}),
                ],style={'padding': '0px'}),
                html.Tr([
                    html.Td("Max Absolute Normal Forces:"),
                    html.Td("567",style={'textAlign':'right'}),
                ],style={'padding': '0px'}),
                html.Tr([
                    html.Td("Max Absolute Shear Forces:"),
                    html.Td("789",style={'textAlign':'right'}),
                ],style={'padding': '0px'})
            ])
        ])
    else:
        resDiv="Please wait for this to implemented"
