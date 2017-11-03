import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino as rh
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
        endPts=[rs.CurveStartPoint(line),rs.CurveEndPoint(line)]
        endPts=rs.SortPoints(endPts)
        lines2.append(rs.AddLine(endPts[0],endPts[1]))
        for endPt in endPts:
            if sortPts.count(endPt)==0:
                sortPts.append(endPt)
    return sortPts, lines2
def EndPtsUnique(lines):
    pts=[]
    for line in lines:
        endPts=[rs.CurveStartPoint(line),rs.CurveEndPoint(line)]
        for endPt in endPts:
            if pts.count(endPt)==0:
                pts.append(endPt)
    return pts
def TextPreview(basepoints,preString,height):
    rs.EnableRedraw(False)
    plane=[]
    for pt in basepoints:
        plane.append(rs.MovePlane(rs.WorldXYPlane(),pt))
    
    sc.doc = rh.RhinoDoc.ActiveDoc
    
    numbering =[]
    for i in range(len(plane)):
        preText = rs.AddText(str(preString[i]), plane[i], height,justification=131074)
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
    StartIndex.append(nodes.index(rs.CurveStartPoint(element)))
    EndIndex.append(nodes.index(rs.CurveEndPoint(element)))

#Preview numbering
midpoints=[rs.CurveMidPoint(element) for element in elements]
EleNum=TextPreview(midpoints,range(len(midpoints)),TxtHeight)
NodNum=TextPreview(nodes,range(len(nodes)),TxtHeight)