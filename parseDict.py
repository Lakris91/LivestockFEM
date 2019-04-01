import numpy as np
from livestockFEM_v2 import FEM_frame
import plotly.graph_objs as go
import math
import dash_core_components as dcc
import dash_html_components as html
import timeit


def plotDict(outDict,Plots=['Nodes','Elements','SupportViz','HingeViz','NodeloadViz','ElementloadViz','DOFPlot','ForcePlot1','ForcePlot2','ForcePlot3'],plotHeight=350):
    plotNames={ 'Nodes':'Nodes',
                'Elements':'Elements',
                'DOFPlot':'Deformation',
                'ForcePlot1':'Normal Forces',
                'ForcePlot2':'Shear Forces',
                'ForcePlot3':'Bending Moments',
                'SupportViz':'Supports',
                'HingeViz':'Hinges',
                'NodeloadViz':'Node Loads',
                'ElementloadViz':'Element Loads'
                }

    plotColors={'Nodes':'rgba(50,50,50,0.7)',
                'Elements':'rgba(50,50,50,0.7)',
                'DOFPlot':'#E0A914',
                'ForcePlot1':'#0F84B5',
                'ForcePlot2':'#64B227',
                'ForcePlot3':'#E50428',
                'SupportViz':'rgba(50,50,50,0.7)',
                'HingeViz':'#7d2ca5',
                'NodeloadViz':'#b20000',
                'ElementloadViz':'#2d7000'
                }
    units={
    '0.001':'kilometer',
    '1.0':'meter',
    '10.0':'decimeter',
    '100.0':'centimeter',
    '1000.0':'millimeter'
    }
    unitfactor=outDict['UnitScaling']
    scatterPlot=[]
    elementNo=[]
    start = timeit.default_timer()
    #Nodes Plot
    nodes=np.array(outDict['Nodes'])*outDict['UnitScaling']
    minx=np.min(nodes,axis=0)[0]
    maxx=np.max(nodes,axis=0)[0]
    miny=np.min(nodes,axis=0)[1]
    maxy=np.max(nodes,axis=0)[1]

    num=np.arange(len(nodes))
    if 'Nodes' in Plots:
        scatterPlot.append(go.Scatter(x=nodes[:,0],y=nodes[:,1],name=plotNames['Nodes'],mode='markers+text',marker=dict(color=plotColors['Nodes']),text=num,textposition='top center' ))
        scatterPlot[-1]['customdata']=['isnode']*len(nodes[:,0])
        #scatterPlot.append(go.Scatter(x=nodes[:,0],y=nodes[:,1],name=plotNames['Nodes'],mode='markers+text',marker=dict(color=plotColors['Nodes'],symbol='triangle-se',size=10),text=num,textposition='top center' ))
    #Elements Plots
    if 'Elements' in Plots:
        elenum=[]
        elex=np.array([])
        eley=np.array([])
        for elei,ele in enumerate(outDict['Topology']):
            elenum+=[None,elei,None]
            elex=np.append(elex,np.insert(ele,1,np.average(ele,axis=0),axis=0)[:,0])
            eley=np.append(eley,np.insert(ele,1,np.average(ele,axis=0),axis=0)[:,1])
            if elei != len(outDict['Topology']):
                elenum.append(None)
                elex=np.append(elex,None)
                eley=np.append(eley,None)
        scatterPlot.append(go.Scatter(x=elex,y=eley,name=plotNames['Elements'],line=dict(color=plotColors['Elements'],dash = 'dot'),mode='lines+text',
                    text=np.array(elenum),textposition='top center'))
        scatterPlot[-1]['customdata']=elenum
    if 'SupportViz' in Plots:
        for i,sup in enumerate(outDict['SupportViz']):
            scatterPlot.append(go.Scatter(x=np.array(sup).T[0],y=np.array(sup).T[1],name=plotNames['SupportViz'],line=dict(color=plotColors['SupportViz']),mode='lines',fill="toself",showlegend=False,hoverinfo='none'))
    if 'HingeViz' in Plots:
        for i, hin in enumerate(np.array(outDict["HingeViz"])):
            scatterPlot.append(go.Scatter(x=hin[:,0],y=hin[:,1],name=plotNames['HingeViz'],line=dict(color=plotColors['SupportViz']),mode='lines',fill="toself",showlegend=False,hoverinfo='none'))
    if 'NodeloadViz' in Plots:
        for i, nl in enumerate(np.array(outDict["NodeloadViz"])):
            minx=min(minx,np.min(nl[:,0]))
            maxx=max(maxx,np.max(nl[:,0]))
            miny=min(miny,np.min(nl[:,1]))
            maxy=max(maxy,np.max(nl[:,1]))
            size=int(np.linalg.norm(nl[2]-nl[-1])*(1/outDict['ForceScale']))
            scatterPlot.append(go.Scatter(x=nl[:,0],y=nl[:,1],name=plotNames['NodeloadViz'],line=dict(color=plotColors['NodeloadViz']),mode='lines+text',text=[None,None,None,None,None,str(size)+'N'],textposition='top center',showlegend=not(bool(i)),hoverinfo='none'))
    if 'ElementloadViz' in Plots:
        for i,nl0 in enumerate(outDict["ElementloadViz"]):
            for j,nl in enumerate(nl0):
                nl=np.array(nl)
                minx=min(minx,np.min(nl[:,0]))
                maxx=max(maxx,np.max(nl[:,0]))
                miny=min(miny,np.min(nl[:,1]))
                maxy=max(maxy,np.max(nl[:,1]))
                if j == 4:
                    size=int(np.linalg.norm(nl[2]-nl[-1])*(1/outDict['ForceScale']))
                    scatterPlot.append(go.Scatter(x=nl[:,0],y=nl[:,1],name=plotNames['ElementloadViz'],line=dict(color=plotColors['ElementloadViz']),mode='lines+text',text=[None,None,None,None,None,str(size)+'N/m'],textposition='top center',showlegend=not(bool(i)),hoverinfo='none'))
                else:
                    scatterPlot.append(go.Scatter(x=nl[:,0],y=nl[:,1],name=plotNames["ElementloadViz"],line=dict(color=plotColors["ElementloadViz"]),mode='lines',showlegend=False,hoverinfo='none'))

    #Deformation and forces plots
    for namei,plot in enumerate(Plots):
        if plot == 'Nodes' or plot == 'Elements' or plot == 'SupportViz' or plot == 'HingeViz' or plot == 'NodeloadViz' or plot == 'ElementloadViz':
            continue
        if bool(outDict["DeformTooLarge"]) and plot =='DOFPlot':
            continue
        plotlist = np.array(outDict[plot])
        forcex=np.array([])
        forcey=np.array([])
        x0=plotlist[:,:,0]
        y0=plotlist[:,:,1]
        minx=min(minx,np.min(x0))
        maxx=max(maxx,np.max(x0))
        miny=min(miny,np.min(y0))
        maxy=max(maxy,np.max(y0))
        for i in range(len(x0)):
            if plot =='DOFPlot':
                elementNo.append([i]*len(x0[i]))
                scatterPlot.append(go.Scatter(x=x0[i],y=y0[i],text = outDict["DefDist"][i][2], hoverinfo = 'text',name=plotNames[plot],line=dict(color=plotColors[plot],width = 2),mode='lines',showlegend=not(bool(i)),visible=True))
                scatterPlot[-1]['customdata']=[i]*len(x0[i])
            elif plot =='ForcePlot1':
                scatterPlot.append(go.Scatter(x=x0[i],y=y0[i],text = [0]+outDict["NormalForce1"][i]+[0], hoverinfo = 'text',name=plotNames[plot],line=dict(color=plotColors[plot],width = 1),mode='lines',fill="toself",hoveron='points',showlegend=not(bool(i)),visible=True))
                scatterPlot[-1]['customdata']=[i]*len(x0[i])
            elif plot =='ForcePlot2':
                scatterPlot.append(go.Scatter(x=x0[i],y=y0[i],text = [0]+outDict["ShearForce2"][i]+[0] , hoverinfo = 'text',name=plotNames[plot],line=dict(color=plotColors[plot],width = 1),mode='lines',fill="toself",hoveron='points',showlegend=not(bool(i)),visible=True))
                scatterPlot[-1]['customdata']=[i]*len(x0[i])
            elif plot =='ForcePlot3':
                scatterPlot.append(go.Scatter(x=x0[i],y=y0[i],text = [0]+outDict["MomentForcesPt"][i]+[0], hoverinfo = 'text',name=plotNames[plot],line=dict(color=plotColors[plot],width = 1),mode='lines',fill="toself",hoveron='points',showlegend=not(bool(i)),visible=True))
                scatterPlot[-1]['customdata']=[i]*len(x0[i])
    if round((minx%(unitfactor/2))*(1000/unitfactor))==0.0:minx-=(unitfactor/2)
    if round((maxx%(unitfactor/2))*(1000/unitfactor))==0.0:maxx+=(unitfactor/2)
    if round((miny%(unitfactor/2))*(1000/unitfactor))==0.0:miny-=(unitfactor/2)
    if round((maxy%(unitfactor/2))*(1000/unitfactor))==0.0:maxy+=(unitfactor/2)

    minx=math.floor(minx/(unitfactor/2))*(unitfactor/2)
    miny=math.floor(miny/(unitfactor/2))*(unitfactor/2)
    maxx=math.ceil(maxx/(unitfactor/2))*(unitfactor/2)
    maxy=math.ceil(maxy/(unitfactor/2))*(unitfactor/2)

    xrange=[minx,maxx]
    yrange=[miny,maxy]
    stop = timeit.default_timer()
    print('Scatter: ', stop - start)
    start = timeit.default_timer()
    femPlot=html.Div([
        dcc.Graph(
            id='FEM-Plot',
            style={
                    'borderWidth': '1px',
                    'borderStyle': 'solid',
                    'borderRadius': '0px',
                    'border-color': 'rgb(220, 220, 220)',
                    'background-color': '#fafafa',
                    'margin': '10px',
                    'resize': 'vertical',
                    'overflow': 'auto',
                    #'width': "95%"
                },
            figure={
                'data': scatterPlot,
                'layout': go.Layout(
                    autosize=True,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    height=plotHeight,
                    xaxis={'title': units[str(unitfactor)],
                            'range' : xrange,
                            'zeroline':False,
                            'scaleanchor' : 'y',
                            'tickvals':[minx+val*(unitfactor/2) for val in range(1+int((maxx-minx)/(unitfactor/2)))],
                            'tickangle':45
                            },
                    yaxis={'title': units[str(unitfactor)],
                            'range' : yrange,
                            'zeroline':False,
                            'tickvals':[miny+val*(unitfactor/2) for val in range(1+int((maxy-miny)/(unitfactor/2)))],
                            'position':0.015
                            },
                    yaxis2={'title': units[str(unitfactor)],
                            'range' : yrange,
                            'zeroline':False,
                            'tickvals':[miny+val*(unitfactor/2) for val in range(1+int((maxy-miny)/(unitfactor/2)))],
                            'anchor':'free',
                            'overlaying':'y',
                            'side':'left',
                            #'tickvals':list(range(yrange[0],yrange[1],max(1,int(unitfactor/2)))),
                            },
                    margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                    legend={'x': 0, 'y': -0.1,'orientation':'h'},
                    hovermode='closest',
                ),
            }
        )
    ])
    stop = timeit.default_timer()
    print('Plot: ', stop - start)
    if bool(outDict["DeformTooLarge"]):
        femPlot.children.append(html.H4("Deformations too large to be plotted, please make sure your structure is supported in both the x-direction and the y-direction at least once.",style={'background-color': 'yellow'}))
    return femPlot
