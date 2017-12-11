import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino as rh
import math
#Deactivate preview for ElePlanes and Nodes
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

curves=SafeExplodeCrv(incurves)

elements=[]
nodes=[]
for curve in curves:
    elements.append(rs.AddLine(rs.CurveStartPoint(curve),rs.CurveEndPoint(curve)))

if sortEle:
    elements=SortCurvesMid(elements)
if sortNod:
    nodes,elements=SortEndPtsUnique(elements)
else:
    nodes=EndPtsUnique(elements)

StartIndex=[]
EndIndex=[]
for element in elements:
    StartIndex.append(rs.PointArrayClosestPoint(nodes, rs.CurveStartPoint(element)))
    EndIndex.append(rs.PointArrayClosestPoint(nodes, rs.CurveEndPoint(element)))

#Preview numbering
midpoints=[rs.CurveMidPoint(element) for element in elements]
EleNum=TextPreview(midpoints,range(len(midpoints)))
NodNum=TextPreview(nodes,range(len(nodes)))

#Scale Nodes to Meter
for repI, node in enumerate(nodes):
    nodes[repI]=node*rs.UnitScale(4)

ElePlanes=[]
for i in range(len(StartIndex)):
    xVector=rs.VectorUnitize(rs.VectorCreate(nodes[EndIndex[i]],nodes[StartIndex[i]]))
    ElePlanes.append(rs.PlaneFromNormal(nodes[StartIndex[i]],(0,0,1),xVector))

#To MatLab text
i=1
MatLabNodes=""
for node in nodes:
    X,Y,Z = node
    nodesString= "X("+str(i)+",:) = ["+str(X)+" "+str(Y)+"];"
    MatLabNodes=MatLabNodes+nodesString+"\n"
    i+=1
MatLabNodes=MatLabNodes+"nno="+str(i-1)+";"

i=1
MatLabElements=""
ESI=StartIndex
EEI=EndIndex
for j in range(len(ESI)):
    elementString= "T("+str(i)+",:) = ["+str(ESI[j]+1)+" "+str(EEI[j]+1)+"];"
    MatLabElements=MatLabElements+elementString+"\n"
    i+=1
MatLabElements=MatLabElements+"nel="+str(i-1)+";"


ESI=StartIndex
EEI=EndIndex
nodecount=max(ESI+EEI)-min(ESI+EEI)+1
dofcount=nodecount*3

uninodes=[]
doflist=[]
DOFSlist=[]
rngstart=1
#Define no-hinge DOFS
for i in range(len(ESI)):
    if uninodes.count(ESI[i])==0:
        uninodes.append(ESI[i])
        dofstart=range(rngstart,rngstart+3)
        doflist.append(dofstart)
        rngstart=rngstart+3
    else:
        dofstart=doflist[uninodes.index(ESI[i])]
    
    if uninodes.count(EEI[i])==0:
        uninodes.append(EEI[i])
        dofend=range(rngstart,rngstart+3)
        doflist.append(dofend)
        rngstart=rngstart+3
    else:
        dofend=doflist[uninodes.index(EEI[i])]
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