import os
import subprocess
import Grasshopper as GH
import rhinoscriptsyntax as rs
import getpass
import math
import Rhino as rh
import scriptcontext as sc
import Grasshopper as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path

def combineEleLoads(PyElementLoad):
    PyElementLoad=tree_to_list(PyElementLoad)
    PEL = [[float(co[0]),float(co[1])] for co in strToList(PyElementLoad[0])]
    for i in range(1,len(PyElementLoad)):
        PEL = [[float(co[0])+PEL[j][0],float(co[1])+PEL[j][1]] for j,co in enumerate(strToList(PyElementLoad[i]))]
    return str(PEL)

def combineNodLoads(PyNodeLoad):
    PyNodeLoad=tree_to_list(PyNodeLoad)
    PNL=[]
    InList=[]
    for nload in PyNodeLoad:
        for DOF,lsize in strToList(nload):
            if InList.count(int(DOF))==0:
                InList.append(int(DOF))
                PNL.append([int(DOF),float(lsize)])
            else:
                PNL[InList.index(int(DOF))]= [int(DOF),PNL[InList.index(int(DOF))][1]+float(lsize)]
    PNL=str(PNL)
    return PNL

def defineEleLoad(ElementIndex,PyNodes,PyElements,Direction,LoadSize,Global):
    ElementPlanes=generatePlanes(PyNodes,PyElements)
    EI=ElementIndex
    PyElementLoad=[]
    if ElementPlanes:
        PyElementLoad0=[[0.0,0.0]]*len(ElementPlanes)
    if not (len(EI)==0 or len(Direction)==0 or len(LoadSize)==0 or len(ElementPlanes)==0 or len(Global)==0):
        #Repeat last element of shortest list
        eleLen = len(EI)
        Direction.extend([Direction[-1]]*(eleLen-len(Direction)))
        LoadSize.extend([LoadSize[-1]]*(eleLen-len(LoadSize)))
        Global.extend([Global[-1]]*(eleLen-len(Global)))
        Direction=Direction[:eleLen]
        LoadSize=LoadSize[:eleLen]
        Global=Global[:eleLen]
        vecX=[]
        vecY=[]
        vecOri=[]
        for i,dir in enumerate(Direction):
            #Unitize 2D vector
            vec=rs.VectorUnitize([dir[0],dir[1],0])
            if Global[i]:
                line=rs.AddLine((0,0,0),vec)
                vpt=rs.XformWorldToCPlane(vec,ElementPlanes[EI[i]])
                opt=rs.XformWorldToCPlane((0,0,0),ElementPlanes[EI[i]])
                vec=rs.VectorCreate(vpt,opt)
            PyElementLoad0[ElementIndex[i]]=[vec[0]*LoadSize[i],vec[1]*LoadSize[i]]
        PyElementLoad = str(PyElementLoad0)
    return PyElementLoad

def defineHinge(PyElements,PyNodes,PyDOFS,AddHingeNode,AddHingeElement):
    ESI=[]
    EEI=[]
    if PyElements:
        for elements in strToList(PyElements):
            ESI.append(int(elements[0]))
            EEI.append(int(elements[1]))
    
    AHE=AddHingeElement
    AHN=AddHingeNode
    
    if len(AHN)<>0 and len(EEI)<>0 and len(ESI)<>0 and PyDOFS<>None:
        Nodes=[[float(no[0])*1/rs.UnitScale(4),float(no[1])*1/rs.UnitScale(4),0.0] for no in strToList(PyNodes)]
        Elem=[[int(no[0]),int(no[1])] for no in strToList(PyElements)]
        
        CirPos=[]
        CirSize=0.25*(1/rs.UnitScale(4))/10
        
        #Repeat last element of shortest list
        if len(AHE)<>0 and len(AHN)<>0:
            maxlen = max(len(AHE),len(AHN))
            AHE.extend([AHE[-1]]*(maxlen-len(AHE)))
            AHN.extend([AHN[-1]]*(maxlen-len(AHN)))
        
        DOFSlist=[]
        for pd in strToList(PyDOFS):
            DOFSlist.append(map(int,pd))
        
        DOFSflat = [item for sublist in DOFSlist for item in sublist]
        #print DOFSlist
        if len(AHN)<>0:
            #Add position of hinge
            for j in range(len(DOFSlist)):
                if len(AHE) == 0:
                    for ahn in AHN:
                        if j == 0:CirPos.append(rs.AddPoint(Nodes[ahn]))
                        if ESI[j]==ahn:
                            DOFSlist[j][2]=-1
                        if EEI[j]==ahn:
                            DOFSlist[j][5]=-1
                else:
                    for k,ahe in enumerate(AHE):
                        if ahe==j:
                            if ESI[j]==AHN[k]:
                                pos=rs.AddPoint(Nodes[ESI[j]])
                                vec = rs.VectorCreate(Nodes[EEI[j]],Nodes[ESI[j]])
                                vec=rs.VectorUnitize(vec)*CirSize
                                CirPos.append(rs.MoveObject(pos,vec))
                                DOFSlist[j][2]=-1
                            if EEI[j]==AHN[k]:
                                pos=rs.AddPoint(Nodes[EEI[j]])
                                vec = rs.VectorCreate(Nodes[ESI[j]],Nodes[EEI[j]])
                                vec=rs.VectorUnitize(vec)*CirSize
                                CirPos.append(rs.MoveObject(pos,vec))
                                DOFSlist[j][5]=-1
            #print DOFSlist
            DOFSflat = [item for sublist in DOFSlist for item in sublist]
            #Add hinge
            indices = [b for b, a in enumerate(DOFSflat) if a == -1]
            lowest =[c for c in range(len(DOFSflat)) if DOFSflat.count(c)==0]
            for lowI,indi in enumerate(indices):
                DOFSflat[indi]=lowest[lowI]
            newDOFSLIST=[]
            templist=[]
            for dofs in DOFSflat:
                templist.append(dofs)
                if len(templist)==6:
                    newDOFSLIST.append(templist)
                    templist=[]
            DOFSlist = newDOFSLIST
        PyDOFS=[]
        for defree in DOFSlist:
            PyDOFS.append(defree)
        PyDOFS=str(PyDOFS)
    else:
        PyDOFS=[]
    return PyDOFS,CirSize,CirPos

def defineMaterials(ElementIndex,PyElements,E,SectionArea,Inertia):
    if len(ElementIndex)==0:
        ElementIndex=range(len(strToList(PyElements)))
    PyMaterial=[]
    Materials=[]
    if not (len(E)==0 or len(SectionArea)==0 or len(Inertia)==0):
        #Repeat last element in list to get equal list lenght
        maxlen = len(ElementIndex)
        SectionArea.extend([SectionArea[-1]]*(maxlen-len(SectionArea)))
        E.extend([E[-1]]*(maxlen-len(E)))
        Inertia.extend([Inertia[-1]]*(maxlen-len(Inertia)))
        SectionArea=SectionArea[:maxlen]
        E=E[:maxlen]
        Inertia=Inertia[:maxlen]
        
        MatList=[]
        for i in range(maxlen):
            Materials.append("E-module="+str(E[i])+" Area="+str(SectionArea[i])+" Inertia="+str(Inertia[i]))
            MatList.append([E[i],SectionArea[i],Inertia[i]])
        PyMaterial=str(MatList)
    return Materials,PyMaterial

def defineNodLoad(NodeIndex,PyElements,PyDOFS,Direction,LoadSize):
    LNN=NodeIndex
    PyNodeLoads="[[0,0.0]]"
    if len(LNN)<>0 and len(Direction)<>0 and len(LoadSize)<>0 and len(PyDOFS)<>0 and len(PyElements)<>0:
        #Repeat last element of shortest list
        nodeLen = len(LNN)
        Direction.extend([Direction[-1]]*(nodeLen-len(Direction)))
        LoadSize.extend([LoadSize[-1]]*(nodeLen-len(LoadSize)))
        Direction=Direction[:nodeLen]
        LoadSize=LoadSize[:nodeLen]
        
        vecX=[]
        vecY=[]
        for dir in Direction:
            #Unitize 2D vector
            vec=rs.VectorUnitize([dir[0],dir[1],0])
            vecX.append(vec[0])
            vecY.append(vec[1])
        
        PyNodeLoads=[]
        PyDOFS=strToList(PyDOFS)
        for i,NI in enumerate(NodeIndex):
            for j,PE in enumerate(strToList(PyElements)):
                if PE.count(str(NI))!=0:
                    ind = PE.index(str(NI))*3
                    PyNodeLoads.append([int(PyDOFS[j][ind]),LoadSize[i]*vecX[i]])
                    PyNodeLoads.append([int(PyDOFS[j][ind+1]),LoadSize[i]*vecY[i]])
                    break
        for PNL in PyNodeLoads:
            if PNL[1]==0.0:
                PyNodeLoads.remove(PNL)
        PyNodeLoads=str(PyNodeLoads)
    return PyNodeLoads

def defineSupports(NodesIndex,PyElements,PyDOFS,LockX,LockY,LockRotation):
    PySupport=[]
    if len(NodesIndex)<>0 and len(LockX)<>0 and len(LockY)<>0 and len(LockRotation)<>0 and PyDOFS<>None:
        #Repeat last element of shortest list
        nodeLen = len(NodesIndex)
        LockX.extend([LockX[-1]]*(nodeLen-len(LockX)))
        LockY.extend([LockY[-1]]*(nodeLen-len(LockY)))
        LockRotation.extend([LockRotation[-1]]*(nodeLen-len(LockRotation)))
        #Idiot proofing
        LockX= LockX[:nodeLen]
        LockY= LockY[:nodeLen]
        LockRotation= LockRotation[:nodeLen]
        
        PySupport=[]
        PyDOFS=strToList(PyDOFS)
        for i,NI in enumerate(NodesIndex):
            for j,PE in enumerate(strToList(PyElements)):
                if PE.count(str(NI))!=0:
                    ind = PE.index(str(NI))*3
                    if LockX[i]:
                        PySupport.append(int(PyDOFS[j][ind]))
                    if LockY[i]:
                        PySupport.append(int(PyDOFS[j][ind+1]))
                    if LockRotation[i]:
                        PySupport.append(int(PyDOFS[j][ind+2]))
        PySupport=str(PySupport)
    return PySupport

def defineTopology(InputCurves,sortElements,sortNodes):
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
        
        #Scale Nodes to Meter
        for repI, node in enumerate(Nodes):
            Nodes[repI]=node*rs.UnitScale(4)
        
        #To Python text
        PyNodes="["
        for node in Nodes:
            PyNodes+=str([node[0],node[1]])+","
        PyNodes=PyNodes[:-1]+"]"
        
        #Preview data
        for repI, node in enumerate(Nodes):
            Nodes[repI]=node*(1/rs.UnitScale(4))
        TextSize=0.25*(1/rs.UnitScale(4))
        ElementMid=[rs.CurveMidPoint(Ele) for Ele in Elements]
        NRange=range(len(Nodes))
        ERange=range(len(Elements))
        
        PyElements="["
        ESI=ElementStartIndex
        EEI=ElementEndIndex
        for i in range(len(ESI)):
            PyElements+=str([ESI[i],EEI[i]])+","
        PyElements=PyElements[:-1]+"]"
        
        nodecount=max(ESI+EEI)-min(ESI+EEI)+1
        dofcount=nodecount*3
        
        uniNodes=[]
        doflist=[]
        DOFSlist=[]
        rngstart=0
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
        
        PyDOFS=str(DOFSlist)
    return Elements,PyNodes,PyElements,PyDOFS,Nodes,ElementMid,NRange,ERange,TextSize

def EvalForces(Geometry,Plot,PlusPosition,PlotScaling):
    Scaling=1/PlotScaling
    Forces=[]
    Lines=[]
    for i,fPl in enumerate(Plot):
        dist=[]
        line=[]
        fVerts=rs.PolylineVertices(fPl)
        if len(fVerts)==2:
            fVerts=rs.DivideCurve(rs.AddLine(fVerts[0],fVerts[1]),20)
        PlusSide=LineSide(Geometry[i],PlusPosition[i])
        for fVert in fVerts:
            cloPt=rs.EvaluateCurve(Geometry[i],rs.CurveClosestPoint(Geometry[i],fVert))
            dis=rs.Distance(fVert,cloPt)*Scaling*(LineSide(Geometry[i],fVert)/PlusSide)
            if dis!=0:
                line.append(rs.AddLine(fVert,cloPt))
            dist.append(dis)
        Forces.append(dist)
        Lines.append(line)
    return Forces,Lines

def flattenTree(dataTree):
    dataTree.Flatten(GH_Path(0))
    return dataTree

def generatePlanes(PyNodes,PyElements):
    Nodes=[[float(no[0]),float(no[1]),0.0] for no in strToList(PyNodes)]
    Elements=[[int(el[0]),int(el[1])] for el in strToList(PyElements)]
    ElementPlanes=[]
    for Ele in Elements:
        xVector=rs.VectorUnitize(rs.VectorCreate(Nodes[Ele[1]],Nodes[Ele[0]]))
        ElementPlanes.append(rs.PlaneFromNormal(Nodes[Ele[0]],(0,0,1),xVector))
    return ElementPlanes

def LineSide(line,point):
    x1,y1,_ = rs.CurveStartPoint(line)
    x2,y2,_ = rs.CurveEndPoint(line)
    x,y,_ = point
    d=(x-x1)*(y2-y1)-(y-y1)*(x2-x1)
    if d!=0:
        d=int(d/abs(d))
    return d

def OriGeo(NodStr,EleStr): 
    scale=rs.UnitScale(rs.UnitSystem(),4)
    lines=[]
    nodes=[[float(co[0])*scale,float(co[1])*scale,0.0] for co in strToList(NodStr)]
    elements=[[int(co[0]),int(co[1])] for co in strToList(EleStr)]
    for el in elements:
        lines.append(rs.AddLine(nodes[el[0]],nodes[el[1]]))
    Nodes=[]
    for nod in nodes:
        Nodes.append(rs.AddPoint(nod))
    return lines,Nodes

def PlotFunc(PtList,deform):
    scale=rs.UnitScale(rs.UnitSystem(),4)
    PtList=PtList.replace("\n","").split("|")
    endlines=[]
    plLine=[]
    plPts=[]
    for i,PtL in enumerate(PtList):
        PtL=PtL.split("_")
        pt=PtL[0].split(",")
        plPts.append((float(pt[0])*scale,float(pt[1])*scale,0.0))
        if len(PtL)!=1:
            if deform:
                plLine.append(rs.AddPolyline(plPts))
            else:
                plLine.append(rs.AddPolyline(plPts[1:-1]))
                if rs.Distance(plPts[0],plPts[1])!=0:
                    endlines.append(rs.AddLine(plPts[0],plPts[1]))
                if rs.Distance(plPts[-1],plPts[-2])!=0:
                    endlines.append(rs.AddLine(plPts[-1],plPts[-2]))
            pt=PtL[1].split(",")
            plPts=[(float(pt[0])*scale,float(pt[1])*scale,0.0)]
        elif i==len(PtList)-1:
            if deform:
                plLine.append(rs.AddPolyline(plPts))
            else:
                if rs.Distance(plPts[0],plPts[1])!=0:
                    endlines.append(rs.AddLine(plPts[0],plPts[1]))
                if rs.Distance(plPts[-1],plPts[-2])!=0:
                    endlines.append(rs.AddLine(plPts[-1],plPts[-2]))
                plLine.append(rs.AddPolyline(plPts[1:-1]))
    return plLine,endlines

def plusSign(plusStr):
    scale=rs.UnitScale(rs.UnitSystem(),4)
    pluspts=[[-0.02,0.125,0],[0.02,0.125,0],[0.02,0.02,0],[0.125,0.02,0],[0.125,-0.02,0],
    [0.02,-0.02,0],[0.02,-0.125,0],[-0.02,-0.125,0],[-0.02,-0.02,0],[-0.125,-0.02,0],
    [-0.125,0.02,0],[-0.02,0.02,0],[-0.02,0.125,0]]
    position=[]
    for ptsStr in plusStr.replace("\n","").split("|"):
        pt=ptsStr.split(",")
        position.append([float(pt[0])*scale,float(pt[1])*scale,0.0])
    plusses=[]
    for posi in position:
        pluspos=[]
        for pluspt in pluspts:
            scaledpt=[pluspt[0]*(0.5/rs.UnitScale(4)),pluspt[1]*(0.5/rs.UnitScale(4))]
            xcoord = posi[0]+scaledpt[0]
            ycoord = posi[1]+scaledpt[1]
            pluspos.append(rs.AddPoint(xcoord,ycoord,0))
        plusses.append(rs.AddPolyline(pluspos))
    return plusses,position

def previewEleLoads(PyNodes,PyElements,PyElementLoad,Scale):
    toMM = rs.UnitScale(rs.UnitSystem(),4)
    nodes = strToList(PyNodes)
    
    plpoints=[]
    pllines=[]
    vectors=[]
    
    eleLoads = strToList(PyElementLoad)
    for ei, ele in enumerate(strToList(PyElements)):
        lx,ly = eleLoads[ei]
        #string to float
        x0,y0,x1,y1 = [float(co) for co in nodes[int(ele[0])]+nodes[int(ele[1])]]
        plane=rs.PlaneFromNormal((x0*toMM,y0*toMM,0),(0,0,1),((x1-x0)*toMM,(y1-y0)*toMM,0))
        plpoint=[]
        vector=[]
        
        for i in range(11):
            xi = x0+(x1-x0)*(float(i)/10.00)
            yi = y0+(y1-y0)*(float(i)/10.00)
            pt=rs.AddPoint((xi*toMM,yi*toMM,0))
            plpt=rs.EvaluatePlane(rs.MovePlane(plane,pt),[-float(lx)*Scale,-float(ly)*Scale])
            vec=rs.VectorCreate(pt,plpt)
            if rs.VectorLength(vec)!=0:
                vector.append(vec)
                plpoint.append(plpt)
        if len(vector)!=0:
            plpoints.append(plpoint)
            vectors.append(vector)
            pllines.append(rs.AddPolyline(plpoint))
    if len(vectors)!=0:
        plpoints=raggedListToDataTree(plpoints)
        vectors=raggedListToDataTree(vectors)
    return plpoints,pllines,vectors

def previewNodLoads(PyNodes,PyNodeLoads,Scale):
    radius = rs.UnitScale(rs.UnitSystem(),4)/4*Scale
    toMM = rs.UnitScale(rs.UnitSystem(),4)
    nodes = strToList(PyNodes)
    
    npoints=[]
    nvectors=[]

    alist=[0]*len(nodes)
    blist=[0]*len(nodes)
    for dof,lsize in strToList(PyNodeLoads):
        node=int(int(dof)/3)
        if alist[node]==0:
            nx,ny=nodes[node]
            nx=float(nx)*toMM
            ny=float(ny)*toMM
            blist[node]=(nx,ny,0)
        else:
            nx,ny,_=alist[node]
        dir=int(dof)%3
        if dir ==0:
            nx=nx-float(lsize)*Scale
        elif dir==1:
            ny=ny-float(lsize)*Scale
        alist[node]=(nx,ny,0)
    for j,al in enumerate(alist):
        if al != 0:
            npoints.append(rs.AddPoint(al))
            nvectors.append(rs.VectorCreate(blist[j],al))
    return npoints,nvectors,radius

def previewSupports(PyNodes,NodesIndex,LockRotation,LockX,LockY):
    scale=rs.UnitScale(rs.UnitSystem(),4)
    radius = scale/4
    nodes=[[float(no[0])*scale,float(no[1])*scale,0.0]for no in strToList(PyNodes)]
    rotpoints=[]
    xpoints=[]
    ypoints=[]
    for i, ni in enumerate(NodesIndex):
        if LockRotation[i]:
            rotpoints.append(rs.AddPoint(nodes[ni]))
        if LockX[i]:
            xpoints.append(rs.AddPoint(nodes[ni]))
        if LockY[i]:
            ypoints.append(rs.AddPoint(nodes[ni]))
    return radius,xpoints,ypoints,rotpoints

def raggedListToDataTree(raggedList):
    rl = raggedList
    result = DataTree[object]()
    for i in range(len(rl)):
        temp = []
        for j in range(len(rl[i])):
            temp.append(rl[i][j])
        #print i, " - ",temp
        path = GH_Path(i)
        result.AddRange(temp, path)
    return result

def readResults(resultfile,PyNodes,PyElements,PlotScalingForces):
    if os.path.isfile(resultfile):
        result=open(resultfile,"r")
        resultstring=result.readlines()
        result.close()
        
        Displacements=[float(dis) for dis in resultstring[0].split(",")]
        ReactionForces=[float(rf) for rf in resultstring[1].split(",")]
        
        Plus,PlusPos=plusSign(resultstring[7])
        DeformationPlot,_=PlotFunc(resultstring[5],True)
        Geometry,_=OriGeo(PyNodes,PyElements)
        
        NormalPlot,NEnds=PlotFunc(resultstring[6],False)
        NForces,NLines=EvalForces(Geometry,NormalPlot,PlusPos,PlotScalingForces)
        NormalForces=raggedListToDataTree(NForces)
        NormalLines=raggedListToDataTree(NLines)
        NormalPlot=Plus+NormalPlot+NEnds
        
        ShearPlot,SEnds=PlotFunc(resultstring[8],False)
        SForces,SLines=EvalForces(Geometry,ShearPlot,PlusPos,PlotScalingForces)
        ShearForces=raggedListToDataTree(SForces)
        ShearLines=raggedListToDataTree(SLines)
        ShearPlot=Plus+ShearPlot+SEnds
        
        MomentPlot,MEnds=PlotFunc(resultstring[10],False)
        MForces,MLines=EvalForces(Geometry,MomentPlot,PlusPos,PlotScalingForces)
        MomentForces=raggedListToDataTree(MForces)
        MomentLines=raggedListToDataTree(MLines)
        MomentPlot=Plus+MomentPlot+MEnds
        return Displacements, DeformationPlot, ReactionForces, NormalForces, NormalPlot,NormalLines, ShearForces, ShearPlot,ShearLines,MomentForces,MomentPlot,MomentLines
    else:
        return None

def run_template(template_to_run):
    info = subprocess.STARTUPINFO()
    info.dwFlags = 1
    info.wShowWindow = 0
    py_exe = str(sc.sticky["PythonExe"])
    thread = subprocess.Popen([py_exe, r'C:\livestock3d\data\livestockFEM\livestockFEMtemplate.py'], startupinfo = info)
    thread.wait()
    thread.kill()
    resultfile="C:/livestock3d/data/livestockFEM/result_file.txt"
    return resultfile

def strToList(string):
    string=string.replace(" ","")
    list=[]
    for str in string[2:-2].split("],["):
        list.append(str.split(","))
    return list

def subdivideElement(ElementIndex,PyNodes,PyElements,PyDOFS,PyMaterial,Div):
    toMM = rs.UnitScale(rs.UnitSystem(),4)
    deci=int(math.log10(toMM))
    NewElementIndices=[]
    
    for EleInd in ElementIndex:
        PN =[[float(co[0]),float(co[1])] for co in strToList(PyNodes)]
        PE =[[int(co[0]),int(co[1])] for co in strToList(PyElements)]
        PD = [[int(co[i]) for i in range(6)] for co in strToList(PyDOFS)]
        if PyMaterial:
            PM =[[float(co[0]),float(co[1]),float(co[2])] for co in strToList(PyMaterial)]
        eleCount=len(PE)
        PyMaterials=[]
        for ei, ele in enumerate(PE):
            if ei == EleInd:
                sti=ele[0]
                eni=ele[1]
                stdof=PD[ei][:3]
                endof=PD[ei][3:]
                dfadd= max([item for sublist in PD for item in sublist])-(len(PN)*3-1)
                
                for j in range(Div):
                    if PyMaterial:
                        [PM.append(PM[ei]) for _ in range(Div-1)]
                        PyMaterials=str(PM)
                    if j ==0:
                        en=len(PN)
                        PE[ei]=[sti,en]
                        PD[ei]=stdof+[en*3+dfadd,en*3+1+dfadd,en*3+2+dfadd]
                        NewElementIndices.append(ei)
                    elif j<Div-1:
                        st=len(PN)+(j-1)
                        en=len(PN)+j
                        PE.append([st,en])
                        PD.append([st*3+dfadd,st*3+1+dfadd,st*3+2+dfadd,en*3+dfadd,en*3+1+dfadd,en*3+2+dfadd])
                        NewElementIndices.append(eleCount-1+j)
                    else:
                        st=len(PN)+(j-1)
                        PE.append([st,eni])
                        PD.append([st*3+dfadd,st*3+1+dfadd,st*3+2+dfadd]+endof)
                        NewElementIndices.append(eleCount-1+j)
                PyElements=str(PE)
                PyDOFS=str(PD)
                                
                x0,y0,x1,y1 = PN[sti]+PN[eni]
                for i in range(1,Div):
                    xi = round(x0+(x1-x0)*(float(i)/float(Div)),deci)
                    yi = round(y0+(y1-y0)*(float(i)/float(Div)),deci)
                    pt=",["+str(xi)+","+str(yi)+"]"
                    PyNodes=PyNodes[:len(PyNodes)-1] + pt + PyNodes[len(PyNodes)-1:]
    return NewElementIndices,PyNodes,PyElements,PyDOFS,PyMaterials

def tree_to_list(input, retrieve_base = lambda x: x[0]):
    # written by Giulio Piacentino, giulio@mcneel.com
    # Returns a list representation of a Grasshopper DataTree
    def extend_at(path, index, simple_input, rest_list):
        target = path[index]
        if len(rest_list) <= target: rest_list.extend([None]*(target-len(rest_list)+1))
        if index == path.Length - 1:
            rest_list[target] = list(simple_input)
        else:
            if rest_list[target] is None: rest_list[target] = []
            extend_at(path, index+1, simple_input, rest_list[target])
    all = []
    for i in range(input.BranchCount):
        path = input.Path(i)
        extend_at(path, 0, input.Branch(path), all)
    return retrieve_base(all)

def writeInputFile(PyNodes,PyElements,PyDOFS,PyMaterial,PySupport,PyNodeLoad,PyElementLoad,PlotScalingDeformation,PlotScalingForces,PlotDivisions):
    if PyNodeLoad is None:
        PyNodeLoad="[[0,0.0]]"
    if PyElementLoad is None:
        PyElementLoad=str([[0,0.0]]*len(strToList(PyElements)))
    
    input_path = 'C:/livestock3d/data/livestockFEM/input_file.txt'
    
    file = open(input_path, 'w')
    file.write(PyNodes+ '\n')
    file.write(PyElements+ '\n')
    file.write(PyDOFS+ '\n')
    file.write(PyMaterial+ '\n')
    file.write(PySupport+ '\n')
    file.write(PyNodeLoad+ '\n')
    file.write(PyElementLoad+ '\n')
    file.write(str(PlotScalingDeformation)+ '\n')
    file.write(str(PlotScalingForces*(1/rs.UnitScale(rs.UnitSystem(),4)))+ '\n')
    file.write(str(PlotDivisions-1)+ '\n')
    file.close()
    
    return input_path
