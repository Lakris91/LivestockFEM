import dash_core_components as dcc
import dash_html_components as html

def dragndrop(text):
    dd=html.Div([
        dcc.Upload(
            id='upload-data',
            children=text,
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
    ])
    return dd

def generateTabs():
    tab_height='40px'
    tabDef=html.Div([
    dcc.Tabs(id='tabs', value='scaling',style={'width':'50%', 'height':tab_height,'font-size': '16px','padding':1}, children=[
    dcc.Tab(label='Scaling', value='scaling',style={'padding': '6px'},selected_style={'padding': '6px'}),
    dcc.Tab(label='Topology', value='topology',style={'padding': '6px'},selected_style={'padding': '6px'}),
    dcc.Tab(label='Supports', value='support',style={'padding': '6px'},selected_style={'padding': '6px'}),
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
                            html.Div('View filter:'),
                            html.Div(dcc.Checklist(
                                id='viewfilter',
                                options=[
                                    {'label': 'Nodes', 'value': 'Nodes'},
                                    {'label': 'Elements', 'value': 'Elements'},
                                    {'label': 'Deformation', 'value': 'DOFPlot'},
                                    {'label': 'Normal Forces', 'value': 'ForcePlot1'},
                                    {'label': 'Shear Forces', 'value': 'ForcePlot2'},
                                    {'label': 'Bending Moments', 'value': 'ForcePlot3'}],
                                values=['Nodes','Elements','DOFPlot'],
                                labelStyle={'display': 'inline-block'},
                            ))
                            ],
                            className='four columns'
                        ),
                        html.Div(
                            [
                            html.Div('Deformation Scale:'),
                            dcc.Input(id='defText', type='number',value=jsonDict['PlotScalingDeformation'], selectionDirection='forward' )
                            ],
                            style={'display': 'inline-block'},
                        ),
                        html.Div(
                            [
                            html.Div('Forces Scale:'),
                            dcc.Input(id='forText', type='number',value=jsonDict['PlotScalingForces'], selectionDirection='forward' )
                            ],
                            style={'display': 'inline-block'},
                        )
                    ],
                )
    return viewCheck

def tab1():
    tabDiv= html.Div([
            html.H3('This is tab1')
            ])
    return tabDiv

def tab2():
    tabDiv= html.Div([
            html.H3('This is tab2')
            ])
    return tabDiv

def tab3():
    tabDiv= html.Div([
            html.H3('This is tab3')
            ])
    return tabDiv

def tab4():
    tabDiv= html.Div([
            html.H3('This is tab4')
            ])
    return tabDiv
