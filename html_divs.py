import dash_core_components as dcc
import dash_html_components as html

def dragndrop(idStr,text,linkText=''):
    dd = dcc.Upload(
            id=idStr,
            children=html.Div(['\n','\n',text, html.A(linkText)]),
            accept='.json',
            style={
                'width': '40%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px',
                'display': 'inline-block',
                'overflow-y': 'auto',
                'white-space':'nowrap'
                #'overflow':'hidden'
                #'resize': 'horizontal',
                #'overflow': 'auto'
            },
        )
    return dd

def generateTabs():
    tab_height='40px'
    tabDef=html.Div([
    dcc.Tabs(id='tabs', value='nodes',style={'width':'1000px', 'height':tab_height,'font-size': '16px','padding':1}, children=[
    dcc.Tab(label='Nodes', value='nodes',style={'padding': '6px'},selected_style={'padding': '6px'}),
    dcc.Tab(label='Elements', value='elements',style={'padding': '6px'},selected_style={'padding': '6px'}),
    dcc.Tab(label='Supports', value='supports',style={'padding': '6px'},selected_style={'padding': '6px'}),
    dcc.Tab(label='Loads', value='loads',style={'padding': '6px'},selected_style={'padding': '6px'}),
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
                        {'label': 'Deformation', 'value': 'DOFPlot'},
                        {'label': 'Normal Forces', 'value': 'ForcePlot1'},
                        {'label': 'Shear Forces', 'value': 'ForcePlot2'},
                        {'label': 'Bending Moments', 'value': 'ForcePlot3'}],
                    values=['Nodes','Elements','DOFPlot'],
                    labelStyle={'display': 'inline-block'},
                )
                ],
                style={ 'width': '25%','display': 'inline-block','height':'75px','vertical-align': 'middle', 'padding':'10px'}
                #className='three columns'
            ),
            html.Div(
                [
                html.Div('Deformation Scale:',style={'borderStyle': 'line','height':'30px'}),
                dcc.Input(id='defText', type='number',value=jsonDict['PlotScalingDeformation'], selectionDirection='forward', debounce=True , style={'height':'25px'})
                ],
                style={'display': 'inline-block','height':'75px','vertical-align': 'middle', 'padding':'10px'},
            ),
            html.Div(
                [
                html.Div('Forces Scale:',style={'borderStyle': 'line','height':'30px'}),
                dcc.Input(id='forText', type='number',value=jsonDict['PlotScalingForces'], selectionDirection='forward',debounce=True, style={'height':'25px'} )
                ],
                style={'display': 'inline-block','height':'75px','vertical-align': 'middle', 'padding':'10px'},
            ),
            html.Div(
                [
                html.Div('Plot Height:',style={'display': 'inline-block','height':'30px'}),
                html.Div(dcc.Slider(id='plotHeight', min=100, max=2000, value=500, step=50))
                ],
                style={'display': 'inline-block','width': '25%','height':'75px','vertical-align': 'middle', 'padding':'10px'},
            )
        ],
    )
    return viewCheck

def plotHeight():
    print("blah")

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

def tab5():
    tabDiv= html.Div([
            html.H3('This is tab5')
            ])
    return tabDiv
