import numpy as np
from livestockFEM_v2 import FEM_frame
import plotly.graph_objs as go
import math
import dash_core_components as dcc
import dash_html_components as html

def plotDict(jsonDict):
    fem=FEM_frame(jsonDict)
    unit="millimeter"
    unitfactor=0.001

    scatterPlot=[]
    #Nodes Plot
    nodes=fem.X*fem.plotScale
    num=np.arange(len(nodes))
    scatterPlot.append(go.Scatter(x=nodes[:,0],y=nodes[:,1],name='Nodes',mode='markers+text',text=num,textposition='top center' ))
    #Elements Plots
    elenum=[]
    elex=np.array([])
    eley=np.array([])
    for elei,ele in enumerate(fem.outDict["Topology"]):
        elenum+=[None,elei,None]
        elex=np.append(elex,np.insert(ele,1,np.average(ele,axis=0),axis=0)[:,0])
        eley=np.append(eley,np.insert(ele,1,np.average(ele,axis=0),axis=0)[:,1])
        if elei != len(fem.outDict["Topology"]):
            elenum.append(None)
            elex=np.append(elex,None)
            eley=np.append(eley,None)
    scatterPlot.append(go.Scatter(x=elex,y=eley,name='Elements',mode='lines+text',
                text=np.array(elenum),textposition='top center'))

    Plots=["DOFPlot","ForcePlot1","ForcePlot2","ForcePlot3"]
    names=["Deformation","Normal Forces","Shear Forces", "Bending Moments"]
    minx=float('inf')
    maxx=-float('inf')
    miny=float('inf')
    maxy=-float('inf')
    for namei,plot in enumerate(Plots):
        plotlist = np.array(fem.outDict[plot])
        forcex=np.array([])
        forcey=np.array([])
        x0=plotlist[:,:,0]
        y0=plotlist[:,:,1]
        for i in range(len(x0)):
            forcex=np.append(forcex,x0[i])
            forcey=np.append(forcey,y0[i])
            minx=min(minx,np.min(x0[i]))
            maxx=max(maxx,np.max(x0[i]))
            miny=min(miny,np.min(y0[i]))
            maxy=max(maxy,np.max(y0[i]))
            if i!=len(x0)-1:
                forcex=np.append(forcex,np.array(None))
                forcey=np.append(forcey,np.array(None))
        scatterPlot.append(go.Scatter(x=forcex,y=forcey,name=names[namei],mode='lines',visible=True))


    minx=int((math.floor(minx*unitfactor)*1/unitfactor)+(1/unitfactor/2))
    miny=int((math.floor(miny*unitfactor)*1/unitfactor)-(1/unitfactor/2))
    maxx=int((math.ceil(maxx*unitfactor)*1/unitfactor))
    maxy=int((math.ceil(maxy*unitfactor)*1/unitfactor))

    femPlot=html.Div([
    #html.Hr(),
    dcc.Graph(
        id='life-exp-vs-gdp',
        figure={
            'data': scatterPlot,
            'layout': go.Layout(
                autosize=True,
                #width=800,
                #height=800,
                xaxis={'title': unit,
                        'range' : [minx,maxx],
                        'zeroline':False,
                        'scaleanchor' : "y",
                        'tickvals':list(range(minx,maxx,int(1/unitfactor/2)))
                        },
                yaxis={'title': unit,
                        'range' : [miny,maxy],
                        'zeroline':False,
                        'tickvals':list(range(miny,maxy,int(1/unitfactor/2)))
                        },
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
        }
    )
    ])

    return femPlot
