"""Generates the topology of the the system.
    Inputs:
        InputCurves: The topology curves, polylines or lines
        sortElements: Sort elements euclidean from the midpoint
        sortNodes: Sort the nodes of an element euclidean
    Output:
        Nodes: Node coordinates in meter
        Elements: Lines representing the elements
        ElementPlanes: Local planes for elements for use in the element load component
        ElementStartIndex: Index of start node of element
        ElementEndIndex: Index of end node of element
        NodeDOFS: Degrees of freedom for each node (no hinges)
        ElementNo: Preview of element numbers
        NodeNo: Preview of node numbers
        MatLabNodes: MatLab string for the nodes
        MatLabElement: MatLab string for the elements
        MatLabDOFS: MatLab string for the degrees of freedom (no hinges)"""

__author__ = "LasseKristensen"

import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino as rh
import math
#Deactivate preview for ElementPlanes and Nodes
ghenv.Component.Params.Output[0].Hidden = True
ghenv.Component.Params.Output[2].Hidden = True

#sc.doc = ghdoc
def SortCurvesMid(curves):
    points=[]
    indices=[]
    
    for curve in curves:
        points.append(rs.CurveMidPoint(curve))
    sortedpts=rs.SortPoints(points,True)
    for point in points:
        indices.append(sortedpts.index(point))
    sortin,sortLines = zip(*sorted(zip(indices, curves)))
    return sortLines
def SafeExplodeCrv(inCurves):
    curves=[]
    
    for crv in inCurves:
        if rs.IsPolyline(crv) or rs.IsPolyCurve(crv):
            curves.extend(rs.ExplodeCurves(crv))
        else:
            curves.append(crv)
    return curves
def SortEndPtsUnique(lines):
    sortPts=[]
    lines2=[]
    for line in lines:
        stPt=rs.AddPoint(round(rs.CurveStartPoint(line)[0],3),round(rs.CurveStartPoint(line)[1],3),0)
        enPt=rs.AddPoint(round(rs.CurveEndPoint(line)[0],3),round(rs.CurveEndPoint(line)[1],3),0)
        endPts=[rs.coerce3dpoint(stPt),rs.coerce3dpoint(enPt)]
        endPts=rs.SortPoints(endPts)
        lines2.append(rs.AddLine(endPts[0],endPts[1]))
        for endPt in endPts:
            if sortPts.count(endPt)==0:
                sortPts.append(endPt)
    return sortPts, lines2
def EndPtsUnique(lines):
    pts=[]
    for line in lines:
        stPt=rs.AddPoint(round(rs.CurveStartPoint(line)[0],3),round(rs.CurveStartPoint(line)[1],3),0)
        enPt=rs.AddPoint(round(rs.CurveEndPoint(line)[0],3),round(rs.CurveEndPoint(line)[1],3),0)
        endPts=[rs.coerce3dpoint(stPt),rs.coerce3dpoint(enPt)]
        for endPt in endPts:
            if pts.count(endPt)==0:
                pts.append(endPt)
    return pts
def TextPreview(basepoints,preString):
    rs.EnableRedraw(False)
    plane=[]
    for pt in basepoints:
        plane.append(rs.MovePlane(rs.WorldXYPlane(),pt))
    
    sc.doc = rh.RhinoDoc.ActiveDoc
    
    numbering =[]
    for i in range(len(plane)):
        preText = rs.AddText(str(preString[i]), plane[i], 0.25*(1/rs.UnitScale(4)),justification=131074)
        textGeo = rs.ExplodeText(preText, True)
        for i in textGeo:
            numbering.append(rs.coercegeometry(i))
            rs.DeleteObject(i)
    sc.doc = ghdoc
    rs.EnableRedraw(True)
    return numbering

if len(InputCurves)<>0:
    curves=SafeExplodeCrv(InputCurves)
    
    Elements=[]
    Nodes=[]
    for curve in curves:
        Elements.append(rs.AddLine(rs.CurveStartPoint(curve),rs.CurveEndPoint(curve)))
    
    if sortElements:
        Elements=SortCurvesMid(Elements)
    if sortNodes:
        Nodes,Elements=SortEndPtsUnique(Elements)
    else:
        Nodes=EndPtsUnique(Elements)
    
    ElementStartIndex=[]
    ElementEndIndex=[]
    for element in Elements:
        ElementStartIndex.append(rs.PointArrayClosestPoint(Nodes, rs.CurveStartPoint(element)))
        ElementEndIndex.append(rs.PointArrayClosestPoint(Nodes, rs.CurveEndPoint(element)))
    
    #Preview numbering
    midpoints=[rs.CurveMidPoint(element) for element in Elements]
    ElementNo=TextPreview(midpoints,range(len(midpoints)))
    NodeNo=TextPreview(Nodes,range(len(Nodes)))
    
    #Scale Nodes to Meter
    for repI, node in enumerate(Nodes):
        Nodes[repI]=node*rs.UnitScale(4)
    
    ElementPlanes=[]
    for i in range(len(ElementStartIndex)):
        xVector=rs.VectorUnitize(rs.VectorCreate(Nodes[ElementEndIndex[i]],Nodes[ElementStartIndex[i]]))
        ElementPlanes.append(rs.PlaneFromNormal(Nodes[ElementStartIndex[i]],(0,0,1),xVector))
    
    #To MatLab text
    i=1
    MatLabNodes=""
    for node in Nodes:
        X,Y,Z = node
        NodesString= "X("+str(i)+",:) = ["+str(X)+" "+str(Y)+"];"
        MatLabNodes=MatLabNodes+NodesString+"\n"
        i+=1
    MatLabNodes=MatLabNodes+"nno="+str(i-1)+";"
    
    i=1
    MatLabElements=""
    ESI=ElementStartIndex
    EEI=ElementEndIndex
    for j in range(len(ESI)):
        elementString= "T("+str(i)+",:) = ["+str(ESI[j]+1)+" "+str(EEI[j]+1)+"];"
        MatLabElements=MatLabElements+elementString+"\n"
        i+=1
    MatLabElements=MatLabElements+"nel="+str(i-1)+";"
    
    nodecount=max(ESI+EEI)-min(ESI+EEI)+1
    dofcount=nodecount*3
    
    uniNodes=[]
    doflist=[]
    DOFSlist=[]
    rngstart=1
    #Define no-hinge DOFS
    for i in range(len(ESI)):
        if uniNodes.count(ESI[i])==0:
            uniNodes.append(ESI[i])
            dofstart=range(rngstart,rngstart+3)
            doflist.append(dofstart)
            rngstart=rngstart+3
        else:
            dofstart=doflist[uniNodes.index(ESI[i])]
        
        if uniNodes.count(EEI[i])==0:
            uniNodes.append(EEI[i])
            dofend=range(rngstart,rngstart+3)
            doflist.append(dofend)
            rngstart=rngstart+3
        else:
            dofend=doflist[uniNodes.index(EEI[i])]
        DOFS=dofstart+dofend
        DOFSlist.append(DOFS)
    
    DOFSflat = [item for sublist in DOFSlist for item in sublist]
    
    DegreesOfFreedom=[]
    for defree in DOFSlist:
        DegreesOfFreedom.append(str(defree))
    
    MatLabDOFS=""
    for k, dofree in enumerate(DegreesOfFreedom):
        MatLabDOF= "D("+str(k+1)+",:)="+ dofree.replace(",","")+";\n"
        MatLabDOFS=MatLabDOFS+MatLabDOF
    MatLabDOFS=MatLabDOFS+"nd="+str(max(DOFSflat))+";"
    
    NodeDOFS=[]
    for nodeNo in range(max(max(ESI),max(EEI))+1):
        for l,sdof in enumerate(DOFSlist):
            if nodeNo == ESI[l]:
                NodeDOFS.append(sdof[:3])
                break
            elif nodeNo ==EEI[l]:
                NodeDOFS.append(sdof[3:])
                break
    NodeDOFS=str(NodeDOFS)