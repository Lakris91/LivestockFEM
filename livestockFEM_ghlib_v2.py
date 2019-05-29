import os
import subprocess
import rhinoscriptsyntax as rs
import math
import copy
import json
import Rhino as rh
import Grasshopper as gh
from Grasshopper.Kernel.Data import GH_Path


def checkIndex(FEMdata, nodes = [], elements=[]):
    nCheck = False
    eCheck = False
    nodesClean = []
    elementsClean = []
    for node in nodes:
        if node >= 0 and node < len(FEMdata['PyNodes']):
            nodesClean.append(node)
        else:
            nCheck = True
    for element in elements:
        if element >= 0 and element < len(FEMdata['PyElements']):
            elementsClean.append(element)
        else:
            eCheck = True
    return nCheck,eCheck,nodesClean,elementsClean

def defineEleLoad(ElementIndex,FEMdata,Direction,LoadSize,Global):
    ElementPlanes=generatePlanes(FEMdata["PyNodes"],FEMdata["PyElements"])
    if len(ElementIndex)==0:
        ElementIndex=range(len(FEMdata["PyElements"]))
    EI=ElementIndex
    PyElementLoad=[]
    if ElementPlanes:
        PyElementLoad0=[[0.0,0.0]]*len(FEMdata["PyElements"])
        if not "PyElementLoad" in FEMdata:
            FEMdata["PyElementLoad"] = [[0.0,0.0]]*len(FEMdata["PyElements"])
    if not (len(Direction)==0 or len(LoadSize)==0 or len(ElementPlanes)==0 or len(Global)==0):
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
        eleLoad = []
        for i in range(len(FEMdata["PyElementLoad"])):
            eleLoad.append([FEMdata["PyElementLoad"][i][0]+PyElementLoad0[i][0],FEMdata["PyElementLoad"][i][1]+PyElementLoad0[i][1]])
        FEMdata["PyElementLoad"]=eleLoad
    return FEMdata

def defineHinge(FEMdata,AddHingeNode,AddHingeElement):
    ESI=[]
    EEI=[]

    for elements in FEMdata["PyElements"]:
        ESI.append(elements[0])
        EEI.append(elements[1])

    AHE=AddHingeElement
    AHN=AddHingeNode
    if len(AHN)==0:
        AHN = range(len(FEMdata["PyNodes"]))
    if len(EEI)!=0 and len(ESI)!=0:
        Nodes=[[no[0]*1/rs.UnitScale(4),no[1]*1/rs.UnitScale(4),0.0] for no in FEMdata["PyNodes"]]
        Elem=FEMdata["PyElements"]

        CirPos=[]
        CirSize=0.05*(1/rs.UnitScale(4))

        #Repeat last element of shortest list
        if len(AHE)!=0 and len(AHN)!=0:
            maxlen = max(len(AHE),len(AHN))
            AHE.extend([AHE[-1]]*(maxlen-len(AHE)))
            AHN.extend([AHN[-1]]*(maxlen-len(AHN)))

        DOFSlist=FEMdata["PyDOFS"]

        DOFSflat = [item for sublist in DOFSlist for item in sublist]

        if len(AHN)!=0:
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
        FEMdata["PyDOFS"]=PyDOFS
    return FEMdata,CirSize,CirPos

def defineMaterials(ElementIndex,FEMdata,E,SectionArea,Inertia,proName,matName):
    if "PyMaterial" in FEMdata:
        PyMaterial=FEMdata["PyMaterial"]
    else:
        PyMaterial=[[]]*len(FEMdata["PyElements"])

    if len(ElementIndex)==0:
        ElementIndex=[i for i,pym in enumerate(PyMaterial) if len(pym)==0]
    if len(SectionArea) == 0:
        SectionArea=[0.00132*(rs.UnitScale(rs.UnitSystem(),4)**2)]
    if len(Inertia) == 0:
        Inertia=[0.000003178*(rs.UnitScale(rs.UnitSystem(),4)**4)]
    if len(proName)==0:
        proName=["Unknown"]
    if len(matName)==0:
        matName=["Unknown"]

    maxlen = len(ElementIndex)
    SectionArea.extend([SectionArea[-1]]*(maxlen-len(SectionArea)))
    E.extend([E[-1]]*(maxlen-len(E)))
    Inertia.extend([Inertia[-1]]*(maxlen-len(Inertia)))
    proName.extend([proName[-1]]*(maxlen-len(proName)))
    matName.extend([matName[-1]]*(maxlen-len(matName)))
    SectionArea=SectionArea[:maxlen]
    E=E[:maxlen]
    Inertia=Inertia[:maxlen]
    proName=proName[:maxlen]
    matName=matName[:maxlen]

    Materials=[]
    for i in range(len(PyMaterial)):
        if i in ElementIndex:
            j=ElementIndex.index(i)
            area=SectionArea[j]/(rs.UnitScale(rs.UnitSystem(),4)**2)
            inertia=Inertia[j]/(rs.UnitScale(rs.UnitSystem(),4)**4)
            PyMaterial[ElementIndex[j]]=[E[j],area,inertia,proName[j],matName[j]]
        if len(PyMaterial[i])==0:
            Materials.append(' ')
        else:
            Materials.append('{}/{}\nE-modulus: {:.2e} Pa\nSectionArea: {:.2e} m2\nInertia: {:.2e} m4'.format(PyMaterial[i][3],PyMaterial[i][4],PyMaterial[i][0],PyMaterial[i][1],PyMaterial[i][2]))
    FEMdata["PyMaterial"]=PyMaterial
    return Materials,FEMdata,0.04*(1/rs.UnitScale(4))

def defineNodLoad(FEMdata,NodeIndex,Direction,LoadSize):
    if len(NodeIndex)==0:
        NodeIndex=range(len(FEMdata["PyNodes"]))

    if len(Direction)!=0 and len(LoadSize)!=0:
        #Repeat last element of shortest list
        nodeLen = len(NodeIndex)
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
        for i,NI in enumerate(NodeIndex):
            for j,PE in enumerate(FEMdata["PyElements"]):
                if PE.count(NI)!=0:
                    ind = PE.index(NI)*3
                    PyNodeLoads.append([int(FEMdata["PyDOFS"][j][ind]),LoadSize[i]*vecX[i]])
                    PyNodeLoads.append([int(FEMdata["PyDOFS"][j][ind+1]),LoadSize[i]*vecY[i]])
                    break
        for PNL in PyNodeLoads:
            if PNL[1]==0.0:
                PyNodeLoads.remove(PNL)

        if "PyNodeLoad" in FEMdata:
            for jj in PyNodeLoads:
                for i,ii in enumerate(FEMdata["PyNodeLoad"]):
                    inlist=ii[0] == jj[0]
                    if inlist:
                        FEMdata["PyNodeLoad"][i][1]+=jj[1]
                        break
                if not inlist:
                    FEMdata["PyNodeLoad"].append(jj)
        else:
            FEMdata["PyNodeLoad"]=PyNodeLoads
    return FEMdata

def defineSupports(NodesIndex,FEMdata,LockX,LockY,LockRotation):
    if len(NodesIndex)!=0 and len(LockX)!=0 and len(LockY)!=0 and len(LockRotation)!=0 and FEMdata!=None:
        if not "PySupport" in FEMdata:
            FEMdata["PySupport"]=[]
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
        PyDOFS=FEMdata["PyDOFS"]
        for i,NI in enumerate(NodesIndex):
            for j,PE in enumerate(FEMdata["PyElements"]):
                if PE.count(NI)!=0:
                    ind = PE.index(NI)*3
                    if LockX[i]:
                        PySupport.append(PyDOFS[j][ind])
                    if LockY[i]:
                        PySupport.append(PyDOFS[j][ind+1])
                    if LockRotation[i]:
                        PySupport.append(PyDOFS[j][ind+2])
        for pys in set(PySupport):
            if not pys in FEMdata["PySupport"]:
                FEMdata["PySupport"].append(pys)
        FEMdata["PySupport"] = sorted(FEMdata["PySupport"])
    return FEMdata

def defineTopology(InputCurves,sortElements,sortNodes,tol):
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
                if len(rs.ExplodeCurves(crv))==0:
                    curves.append(crv)
                else:
                    curves.extend(rs.ExplodeCurves(crv))
            else:
                curves.append(crv)
        return curves
    def EndPtsUnique(lines,sort,deci):
        deci0 = int(math.log10(rs.UnitScale(2,rs.UnitSystem())))
        deci = int(deci+math.log10(rs.UnitScale(4,rs.UnitSystem())))
        sortPts=[]
        lines2=[]
        for line in lines:
            stPt=rs.AddPoint(round(round(rs.CurveStartPoint(line)[0],deci0),deci),round(round(rs.CurveStartPoint(line)[1],deci0),deci),0)
            enPt=rs.AddPoint(round(round(rs.CurveEndPoint(line)[0],deci0),deci),round(round(rs.CurveEndPoint(line)[1],deci0),deci),0)
            endPts=[rs.coerce3dpoint(stPt),rs.coerce3dpoint(enPt)]
            if sort:
                endPts=rs.SortPoints(endPts)
            lines2.append(rs.AddLine(endPts[0],endPts[1]))
            for endPt in endPts:
                if sortPts.count(endPt)==0:
                    sortPts.append(endPt)
        return sortPts, lines2

    if len(InputCurves)!=0:
        curves=SafeExplodeCrv(InputCurves)
        FEMdata={}
        Elements=[]
        Nodes=[]
        for curve in curves:
            st = list(rs.CurveStartPoint(curve))[:2]+[0.0]
            en = list(rs.CurveEndPoint(curve))[:2]+[0.0]
            Elements.append(rs.AddLine(st,en))

        if sortElements:
            Elements=SortCurvesMid(Elements)

        Nodes,Elements=EndPtsUnique(Elements,sortNodes,tol)

        ElementStartIndex=[]
        ElementEndIndex=[]
        for element in Elements:
            ElementStartIndex.append(rs.PointArrayClosestPoint(Nodes, rs.CurveStartPoint(element)))
            ElementEndIndex.append(rs.PointArrayClosestPoint(Nodes, rs.CurveEndPoint(element)))

        #Scale Nodes to Meter
        for repI, node in enumerate(Nodes):
            Nodes[repI]=node*rs.UnitScale(4)

        #To Python text
        FEMdata["PyNodes"]=[]
        for node in Nodes:
            FEMdata["PyNodes"].append([node[0],node[1]])

        FEMdata["PyElements"]=[]
        ESI=ElementStartIndex
        EEI=ElementEndIndex
        for i in range(len(ESI)):
            FEMdata["PyElements"].append([ESI[i],EEI[i]])

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
        FEMdata["PyDOFS"]=DOFSlist
    return FEMdata

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

def generatePlanes(PyNodes,PyElements):
    ElementPlanes=[]
    for Ele in PyElements:
        xVector=rs.VectorUnitize(rs.VectorCreate(PyNodes[Ele[1]]+[0.0],PyNodes[Ele[0]]+[0.0]))
        ElementPlanes.append(rs.PlaneFromNormal(PyNodes[Ele[0]]+[0.0],(0,0,1),xVector))
    return ElementPlanes

def inertiaCalc(geom,optList,comMethod):
    if rs.ObjectType(geom[0])==4:
        geom = rs.AddPlanarSrf(geom)
    pln=rs.CurvePlane(rs.JoinCurves(rs.DuplicateEdgeCurves(geom))[0])
    pts = rs.CullDuplicatePoints(rs.BoundingBox(geom,pln))

    geom = rs.OrientObject(geom,[pts[0],pts[-1],pts[1]],[[0,0,0],[1,0,0],[0,1,0]])
    geom=rs.coercebrep(geom)
    props = rh.Geometry.AreaMassProperties.Compute(geom)

    Istrong=0
    Iweak=float('inf')
    for moms in props.CentroidCoordinatesSecondMoments:
        if moms<(1/rs.UnitScale(2,rs.UnitSystem())):
            continue
        Istrong=max(Istrong,moms)
        Iweak=min(Iweak,moms)
    area = props.Area
    NameList = []
    AreaList = []
    InertiaStrong = []
    InertiaWeak = []
    deviaList = []
    NameList,AreaList, InertiaStrong,InertiaWeak,_ = searchProfile("","")
    for i in range(len(NameList)):
        if not len(optList)==0 and NameList[i] not in optList:
            continue

        areadevia=(min(AreaList[i],area)/max(AreaList[i],area))*100
        inerSdevia=(min(InertiaStrong[i],Istrong)/max(InertiaStrong[i],Istrong))*100

        if comMethod==1:
            devia=(areadevia+inerSdevia)/2
        elif comMethod==2:
            devia=inerSdevia
        elif comMethod==3:
            devia=areadevia
        else:
            inerWdevia=(min(InertiaWeak[i],Iweak)/max(InertiaWeak[i],Iweak))*100
            devia=(areadevia+inerSdevia+inerWdevia)/3
        deviaList.append(round(devia,2))
    deviaList, NameList = zip(*sorted(zip(deviaList, NameList)))
    return area, Istrong, Iweak, deviaList[::-1], NameList[::-1]

def LineSide(line,point):
    x1,y1,_ = rs.CurveStartPoint(line)
    x2,y2,_ = rs.CurveEndPoint(line)
    x,y,_ = point
    d=(x-x1)*(y2-y1)-(y-y1)*(x2-x1)
    if d!=0:
        d=int(d/abs(d))
    return d

def OriGeo(FEMdata):
    scale=rs.UnitScale(rs.UnitSystem(),4)
    lines=[]
    nodes=[[co[0]*scale,co[1]*scale,0.0] for co in FEMdata["PyNodes"]]
    planes=generatePlanes(FEMdata["PyNodes"],FEMdata["PyElements"])
    pln=[]
    for i, el in enumerate(FEMdata["PyElements"]):
        pln.append(rs.MovePlane(planes[i],nodes[el[0]]))
        lines.append(rs.AddLine(nodes[el[0]],nodes[el[1]]))
    Nodes=[]
    for nod in nodes:
        Nodes.append(rs.AddPoint(nod))
    return lines,Nodes,pln

def PlotFunc(PtList,plotDivisions,forces):
    maxVal=0
    intForces=[]
    intPts=[]
    for i, force in enumerate(forces):
        if len(forces[0])!=plotDivisions+2:
            intForce=[]
            for j in range(plotDivisions+2):
                intForce.append((float(j)/float(plotDivisions+1))*(force[-1]-force[0])+force[0])
            intForce=[intForce[0]]+intForce+[intForce[-1]]
            maxVal=max(maxVal,max(abs(min(intForce)),abs(max(intForce))))
            intForces.append(intForce)

            subt = rs.PointSubtract(PtList[i][2],PtList[i][1])
            intPt=[]
            for k in range(plotDivisions+2):
                intPt.append(rs.PointAdd(rs.PointScale(subt, float(k)/float(plotDivisions+1)),PtList[i][1]))
            intPt=[PtList[i][0]]+intPt+[PtList[i][-1]]
            intPts.append(intPt)
        else:
            maxVal=max(maxVal,max(abs(min(force)),abs(max(force))))
            intForces.append([force[0]]+force+[force[-1]])
            intPts=PtList
    plLines=[]
    colort=[]
    for j,sublist in enumerate(intPts):
        lineList=[]
        colorList=[]
        for i,subsub in enumerate(sublist):
            if i!=0:
                #print subsub,sublist[i-1]
                lineList.append(rs.AddLine(subsub,sublist[i-1]))
                #print intForces[j][i]
                average=(intForces[j][i]+intForces[j][i-1])/2
                #print average,(average-(-maxVal))/(maxVal-(-maxVal))
                if maxVal!=0.0:
                    colorList.append((average-(-maxVal))/(maxVal-(-maxVal)))
                else:
                    colorList.append(0.0)
        plLines.append(lineList)
        colort.append(colorList)
    return plLines,colort

def plusSign(position):
    scale=rs.UnitScale(rs.UnitSystem(),4)
    pluspts=[[-0.02,0.125,0],[0.02,0.125,0],[0.02,0.02,0],[0.125,0.02,0],[0.125,-0.02,0],
    [0.02,-0.02,0],[0.02,-0.125,0],[-0.02,-0.125,0],[-0.02,-0.02,0],[-0.125,-0.02,0],
    [-0.125,0.02,0],[-0.02,0.02,0],[-0.02,0.125,0]]

    plusses=[]
    for posi in position:
        pluspos=[]
        for pluspt in pluspts:
            scaledpt=[pluspt[0]*(0.5/rs.UnitScale(4)),pluspt[1]*(0.5/rs.UnitScale(4))]
            xcoord = posi[0]+scaledpt[0]
            ycoord = posi[1]+scaledpt[1]
            pluspos.append(rs.AddPoint(xcoord,ycoord,0))
        plusses.append(rs.AddPolyline(pluspos))
    return plusses

def prettyJSON(dict,sort_keys=True,indent=2):
    ind=" "*indent
    dictStr="{\n"
    for k in sorted(dict):
        dictStr=dictStr + ind + "\""+str(k) +"\"" +": \n"+ ind*2 + str(dict[k]).replace("'","\"").replace("], [","],\n"+ ind*3 +"[").replace("[[","[\n"+ ind*3 +"[").replace("]]","]\n"+ ind*2 +"]")+",\n"
    dictStr = dictStr[:-2]+ ind+ "\n}"
    return dictStr

def previewEleLoads(FEMdata,Scale):
    toMM = rs.UnitScale(rs.UnitSystem(),4)
    plpoints=[]
    pllines=[]
    vectors=[]

    eleLoads = FEMdata["PyElementLoad"]
    for ei, ele in enumerate(FEMdata["PyElements"]):
        lx = eleLoads[ei][0]/(1000/toMM)
        ly = eleLoads[ei][1]/(1000/toMM)

        x0,y0 = FEMdata["PyNodes"][ele[0]]
        x1,y1 = FEMdata["PyNodes"][ele[1]]

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

def previewNodLoads(FEMdata,Scale):
    radius = rs.UnitScale(rs.UnitSystem(),4)/4*Scale
    toMM = rs.UnitScale(rs.UnitSystem(),4)

    npoints=[]
    nvectors=[]

    alist=[0]*len(FEMdata["PyNodes"])
    blist=[0]*len(FEMdata["PyNodes"])
    for dof,lsize in FEMdata["PyNodeLoad"]:
        lsize = lsize/(1000/toMM)
        node=int(dof/3)
        if alist[node]==0:
            nx,ny=FEMdata["PyNodes"][node]
            nx=nx*toMM
            ny=ny*toMM
            blist[node]=(nx,ny,0)
        else:
            nx,ny,_=alist[node]
        dir=dof%3
        if dir ==0:
            nx=nx-lsize*Scale
        elif dir==1:
            ny=ny-lsize*Scale
        alist[node]=(nx,ny,0)
    for j,al in enumerate(alist):
        if al != 0:
            npoints.append(rs.AddPoint(al))
            nvectors.append(rs.VectorCreate(blist[j],al))
    return npoints,nvectors,radius

def previewSupports(FEMdata):
    scale=rs.UnitScale(rs.UnitSystem(),4)

    NodesIndex=[]
    NodesCoord=[]
    Locks=[]
    for sup in FEMdata["PySupport"]:
        for i,dof in enumerate(FEMdata["PyDOFS"]):
            if sup in dof:
                pos = dof.index(sup)
                node=FEMdata["PyElements"][i][int(math.floor(pos/3))]
                if not node in NodesIndex:
                    NodesIndex.append(FEMdata["PyElements"][i][int(math.floor(pos/3))])
                    NodesCoord.append(FEMdata["PyNodes"][FEMdata["PyElements"][i][int(math.floor(pos/3))]])
                    Locks.append([False,False,False])
                if pos%3 == 0:
                    Locks[NodesIndex.index(node)][0]=True
                if pos%3 == 1:
                    Locks[NodesIndex.index(node)][1]=True
                if pos%3 == 2:
                    Locks[NodesIndex.index(node)][2]=True

    bboxmaxX=max([x for x,y in FEMdata["PyNodes"]])*scale
    bboxminX=min([x for x,y in FEMdata["PyNodes"]])*scale
    bboxmaxY=max([y for x,y in FEMdata["PyNodes"]])*scale
    bboxminY=min([y for x,y in FEMdata["PyNodes"]])*scale
    fixed=[(-0.15,0.0),(-0.15,-0.30),(0.15,-0.30),(0.15,-0.0),(-0.15,0.0)]
    pinned=[(0.15, -0.3), (-0.15, -0.3), (-0.02, -0.04), (-0.035, -0.035), (-0.050, 0.0), (-0.035, 0.035), (0.0, 0.050), (0.035, 0.035), (0.050, 0.0), (0.035, -0.035), (0.02, -0.04), (0.15, -0.3)]
    roller=[(-0.035, 0.035), (0.0, 0.050), (0.035, 0.035), (0.050, 0.0), (0.035, -0.035), (0.02, -0.04), (0.15, -0.3), (0.075, -0.3),
    (0.04, -0.315), (0.025, -0.35), (0.04, -0.385), (0.075, -0.4), (0.11, -0.385), (0.125, -0.35), (0.11, -0.315), (0.075, -0.3),
    (-0.075, -0.3), (-0.11, -0.315), (-0.125, -0.35), (-0.11, -0.385), (-0.075, -0.4), (-0.04, -0.385), (-0.025, -0.35), (-0.04, -0.315),
    (-0.075, -0.3), (-0.15, -0.3), (-0.02, -0.04), (-0.035, -0.035), (-0.050, 0.0), (-0.035, 0.035)]
    simple=[(0.15,-0.1),(0.15,0.0),(-0.15,0.0),(-0.15,-0.1),(-0.075,-0.1),(-0.11,-0.115),(-0.125,-0.15),(-0.11,-0.185),(-0.075,-0.2),(-0.15,-0.2),
    (-0.15,-0.3),(0.15,-0.3),(0.15,-0.2),(0.075,-0.2),(-0.074,-0.2),(-0.04,-0.185),(-0.025,-0.15),(-0.04,-0.115),(-0.074,-0.1),(0.074,-0.1),
    (0.04,-0.115),(0.025,-0.15),(0.04,-0.185),(0.075,-0.199),(0.11,-0.185),(0.125,-0.15),(0.11,-0.115),(0.075,-0.1),(0.15,-0.1)]
    fixed=[(x*scale,y*scale) for x,y in fixed]
    pinned=[(x*scale,y*scale) for x,y in pinned]
    roller=[(x*scale,y*scale) for x,y in roller]
    simple=[(x*scale,y*scale) for x,y in simple]
    NodesCoord=[(x*scale,y*scale) for x,y in NodesCoord]

    pllines=[]
    for i, no in enumerate(NodesCoord):
        x,y=no
        xbound = abs(x-bboxmaxX)>abs(x-bboxminX)
        ybound = abs(y-bboxmaxY)>=abs(y-bboxminY)
        bound = [abs(y-bboxminY),abs(y-bboxmaxY),abs(x-bboxminX),abs(x-bboxmaxX)].index(min(abs(x-bboxmaxX),abs(x-bboxminX),abs(y-bboxmaxY),abs(y-bboxminY)))
        print(xbound)
        print(ybound)
        loco = Locks[i].count(True)
        if loco == 1:
            if Locks[i][0]==True:
                if xbound:
                    pllines.append(rs.AddPolyline([(ly+x,lx+y,0.0) for lx,ly in roller]))
                else:
                    pllines.append(rs.AddPolyline([(-ly+x,lx+y,0.0) for lx,ly in roller]))
            elif Locks[i][1]==True:
                if ybound:
                    pllines.append(rs.AddPolyline([(lx+x,ly+y,0.0) for lx,ly in roller]))
                else:
                    pllines.append(rs.AddPolyline([(lx+x,-ly+y,0.0) for lx,ly in roller]))
        elif loco == 2:
            if Locks[i][0]==True and Locks[i][1]==True:
                if bound==0:
                    pllines.append(rs.AddPolyline([(lx+x,ly+y,0.0) for lx,ly in pinned]))
                elif bound==1:
                    pllines.append(rs.AddPolyline([(lx+x,-ly+y,0.0) for lx,ly in pinned]))
                elif bound==2:
                    pllines.append(rs.AddPolyline([(ly+x,lx+y,0.0) for lx,ly in pinned]))
                elif bound==3:
                    pllines.append(rs.AddPolyline([(-ly+x,-lx+y,0.0) for lx,ly in pinned]))
            elif Locks[i][0]==True and Locks[i][2]==True:
                if xbound:
                    pllines.append(rs.AddPolyline([(ly+x,lx+y,0.0) for lx,ly in simple]))
                else:
                    pllines.append(rs.AddPolyline([(-ly+x,lx+y,0.0) for lx,ly in simple]))
            elif Locks[i][1]==True and Locks[i][2]==True:
                if ybound:
                    pllines.append(rs.AddPolyline([(lx+x,ly+y,0.0) for lx,ly in simple]))
                else:
                    pllines.append(rs.AddPolyline([(lx+x,-ly+y,0.0) for lx,ly in simple]))
        elif loco == 3:
            if bound==0:
                pllines.append(rs.AddPolyline([(lx+x,ly+y,0.0) for lx,ly in fixed]))
            elif bound==1:
                pllines.append(rs.AddPolyline([(lx+x,-ly+y,0.0) for lx,ly in fixed]))
            elif bound==2:
                pllines.append(rs.AddPolyline([(ly+x,lx+y,0.0) for lx,ly in fixed]))
            elif bound==3:
                pllines.append(rs.AddPolyline([(-ly+x,-lx+y,0.0) for lx,ly in fixed]))
    return pllines

def previewTopology(FEMdata,subDiv=False):
    scale=(1/rs.UnitScale(4))
    Nodes=[rs.AddPoint((x*scale,y*scale,0.0)) for x,y in FEMdata["PyNodes"]]
    Elements=[rs.AddLine(Nodes[st],Nodes[en]) for st,en in FEMdata["PyElements"]]
    TextSize=0.25*(1/rs.UnitScale(4))*(min([rs.CurveLength(el) for el in Elements])/(3*scale))
    if subDiv:
        TextSize*=2
    ElementMid=[rs.CurveMidPoint(Ele) for Ele in Elements]
    NRange=range(len(Nodes))
    ERange=range(len(Elements))
    return Elements,Nodes,ElementMid,NRange,ERange,TextSize

def raggedListToDataTree(raggedList):
    rl = raggedList
    result = gh.DataTree[object]()
    for i in range(len(rl)):
        temp = []
        for j in range(len(rl[i])):
            temp.append(rl[i][j])
        path = GH_Path(i)
        result.AddRange(temp, path)
    return result

def readResults(resultfile):
    if os.path.isfile(resultfile):
        file=open(resultfile,"r")
        resDict=json.loads(file.read())
        file.close()
        scale=rs.UnitScale(rs.UnitSystem(),4)
        Displacements=[dis*scale for dis in resDict["Displacements"]]
        ReactionForces=resDict["Reactions"]
        PlusPos=resDict["PlusPos"]
        Plus=plusSign(PlusPos)

        DeformationPlot,defColor=PlotFunc(resDict["DOFPlot"],resDict["PlotDivisions"],[dist[2] for dist in resDict["DefDist"]])
        DeformationPlot=raggedListToDataTree(DeformationPlot)
        defColor=raggedListToDataTree(defColor)
        NormalPlot,norColor=PlotFunc(resDict["ForcePlot1"],resDict["PlotDivisions"],resDict["NormalForce1"])
        NormalForces=raggedListToDataTree(resDict["NormalForce1"])
        NormalPlot=raggedListToDataTree(NormalPlot)
        norColor=raggedListToDataTree(norColor)
        ShearPlot,sheColor=PlotFunc(resDict["ForcePlot2"],resDict["PlotDivisions"],resDict["ShearForce2"])
        ShearForces=raggedListToDataTree(resDict["ShearForce2"])
        ShearPlot=raggedListToDataTree(ShearPlot)
        sheColor=raggedListToDataTree(sheColor)

        MomentPlot,momColor=PlotFunc(resDict["ForcePlot3"],resDict["PlotDivisions"],resDict[ "MomentForcesPt"])
        MomentPlot=raggedListToDataTree(MomentPlot)
        MomentForces=raggedListToDataTree(resDict["MomentForcesPt"])
        momColor=raggedListToDataTree(momColor)
        return Displacements, DeformationPlot, defColor, ReactionForces, NormalForces, NormalPlot, norColor, ShearForces, ShearPlot, sheColor,MomentForces,MomentPlot, momColor, Plus, resDict["DeformTooLarge"]
    else:
        return None

def run_template(template_to_run,input_file,py_exe):
    info = subprocess.STARTUPINFO()
    info.dwFlags = 1
    info.wShowWindow = 0
    success=True
    if not py_exe is None:
        try:
            thread = subprocess.Popen([py_exe,template_to_run, input_file], startupinfo = info)
            thread.wait()
            thread.kill()
        except:
            success=False
    else:
        try:
            thread = subprocess.Popen(["python3",template_to_run, input_file], startupinfo = info)
            thread.wait()
            thread.kill()
        except:
            try:
                thread = subprocess.Popen(["python",template_to_run, input_file], startupinfo = info)
                thread.wait()
                thread.kill()
            except:
                try:
                    thread = subprocess.Popen(["py",template_to_run, input_file], startupinfo = info)
                    thread.wait()
                    thread.kill()
                except:
                    success=False
    if "input_file.json" in os.path.split(input_file)[1]:
        resPath = input_file.replace("input_file.json","result_file.json")
    else:
        resPath = input_file.replace(".json","result_file.json")
    return resPath,success

def searchMaterial(MatName):
    values=open(gh.Folders.DefaultUserObjectFolder+"Livestock\\lsFEM\\dependables\\MaterialProperties.csv","r")
    valstring=values.readlines()
    values.close()

    strFound=False
    NameList=[]
    CatList=[]
    EMod=[]
    Weight=[]

    if MatName is None:
        MatName=""

    for string in valstring:
        strlist=string.split(";")
        if not strlist[0]=="#":
            if MatName.replace(" ","").lower() in strlist[2].replace(" ","").lower():
                NameList.append(strlist[2])
                CatList.append(strlist[1])
                EMod.append(float(strlist[3])*10000000)
                Weight.append(float(strlist[5])*1000)
                strFound=True
    return NameList, CatList, EMod, Weight,strFound

def searchProfile(SecName,Region):
    values=open(gh.Folders.DefaultUserObjectFolder+"Livestock\\lsFEM\\dependables\\CrossSectionValues.csv","r")
    valstring=values.readlines()
    values.close()
    unitScale=(1/rs.UnitScale(3))
    strFound=False
    NameList=[]
    AreaList=[]
    InertiaStrong=[]
    InertiaWeak=[]

    if SecName is None:
        SecName=""
    if Region is None:
        Region=""

    for string in valstring:
        strlist=string.split(";")
        if not strlist[0]=="#":
            if Region.replace(" ","").lower() in strlist[1].replace(" ","").lower():
                if SecName.replace(" ","").lower() in strlist[3].replace(" ","").lower():
                    NameList.append(strlist[3])
                    AreaList.append(float(strlist[16])*unitScale**2)
                    InertiaStrong.append(float(strlist[19])*unitScale**4)
                    InertiaWeak.append(float(strlist[24])*unitScale**4)
                    strFound=True
    return NameList, AreaList, InertiaStrong, InertiaWeak,strFound

def subdivideElement(ElementIndex,FEMdata,Div):
    if Div==0 or Div==1:
        return [],FEMdata
    NewElementIndices=[]
    for EleInd in ElementIndex:
        NewElementIndicesEle=[]
        PN = FEMdata["PyNodes"]
        PE = FEMdata["PyElements"]
        PD = FEMdata["PyDOFS"]
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
                    if "PyMaterial" in FEMdata and j!=0:
                        FEMdata["PyMaterial"].append(FEMdata["PyMaterial"][ei])
                    if "PyElementLoad" in FEMdata and j!=0:
                        FEMdata["PyElementLoad"].append(FEMdata["PyElementLoad"][ei])
                    if j ==0:
                        en=len(PN)
                        PE[ei]=[sti,en]
                        PD[ei]=stdof+[en*3+dfadd,en*3+1+dfadd,en*3+2+dfadd]
                        NewElementIndicesEle.append(ei)
                    elif j<Div-1:
                        st=len(PN)+(j-1)
                        en=len(PN)+j
                        PE.append([st,en])
                        PD.append([st*3+dfadd,st*3+1+dfadd,st*3+2+dfadd,en*3+dfadd,en*3+1+dfadd,en*3+2+dfadd])
                        NewElementIndicesEle.append(eleCount-1+j)
                    else:
                        st=len(PN)+(j-1)
                        PE.append([st,eni])
                        PD.append([st*3+dfadd,st*3+1+dfadd,st*3+2+dfadd]+endof)
                        NewElementIndicesEle.append(eleCount-1+j)

                FEMdata["PyElements"]=PE
                FEMdata["PyDOFS"]=PD

                x0,y0,x1,y1 = PN[sti]+PN[eni]
                for i in range(1,Div):
                    xi = x0+(x1-x0)*(float(i)/float(Div))
                    yi = y0+(y1-y0)*(float(i)/float(Div))
                    pt=",["+str(xi)+","+str(yi)+"]"
                    FEMdata["PyNodes"].append([xi,yi])
        NewElementIndices.append(NewElementIndicesEle)
    return raggedListToDataTree(NewElementIndices),FEMdata

def supportGuess(FEMdata):
    eleList=FEMdata["PyElements"]
    nodeList=FEMdata["PyNodes"]
    adjDict={}
    supNodes=[]
    xl=[]
    yl=[]
    rl=[]
    for node in eleList:
        for no in node:
            if no in adjDict:
                adjDict[no]=adjDict[no]+1
            else:
                adjDict[no]=1
    for key in adjDict:
        if adjDict[key]==1:
            supNodes.append(key)
            xl.append(True)
            yl.append(True)
            rl.append(True)
    if len(supNodes)>=2:
        return supNodes,FEMdata,xl,yl,rl

    xlist = [n[0] for n in nodeList]
    xmax = max(xlist)
    xmin = min(xlist)
    ymin = min([n[1] for n in nodeList])
    rightDist=float('inf')
    leftDist=float('inf')
    for i,n in enumerate(nodeList):
        ldist=math.sqrt((xmin-n[0])**2+(ymin-n[1])**2)
        if ldist < leftDist:
            leftDist=ldist
            leftNode=i
    for i,n in enumerate(nodeList):
        if i == leftNode:
            continue
        rdist=math.sqrt((xmax-n[0])**2+(ymin-n[1])**2)
        if rdist < rightDist:
            rightDist=rdist
            rightNode=i
    return [leftNode,rightNode],FEMdata,[True,False],[True,True],[False,False]

def writeInputFile(FEMdata,PlotScalingDeformation,PlotScalingForces,PlotDivisions,ProjectName,Folder):
    eleLoadPreview=[]
    supportPreview=[]
    materialPreview=[]
    if "PyElementLoad" not in FEMdata:
        if "PyNodeLoad" not in FEMdata:
            FEMdata=defineEleLoad([],FEMdata,[(0,-1,0)],[103.62],[True])
            eleLoadPreview = previewEleLoads(FEMdata,PlotScalingForces)
        else:
            FEMdata=defineEleLoad([],FEMdata,[],[],[])
    if not "PyNodeLoad" in FEMdata:
        FEMdata["PyNodeLoad"]=[[0,0.0]]
    if not "PySupport" in FEMdata:
        guess=supportGuess(FEMdata)
        FEMdata=defineSupports(guess[0],guess[1],guess[2],guess[3],guess[4])
        supportPreview=previewSupports(FEMdata)
    if "PyMaterial" not in FEMdata or any([len(mat)==0 for mat in FEMdata["PyMaterial"]]):
        Materials,FEMdata,textSize=defineMaterials([],FEMdata,[210000000000.0],[],[],["IPE120"],["S235"])
        materialPreview=[Materials,textSize]

    if len(Folder) == 0:
        try:
            Folder=[os.path.split(rh.RhinoDoc.ActiveDoc.Path)[0]]
        except:
            Folder=[""]
        if Folder==[""]:
            Folder=[os.path.expanduser("~\\Desktop")]

    if len(ProjectName) == 0:
        ProjectName = ["untitled"]

    input_path = os.path.join(Folder[0], ProjectName[0] + "_input_file.json")

    FEMdata["PlotScalingDeformation"]=PlotScalingDeformation
    FEMdata["PlotScalingForces"]=round(PlotScalingForces*10000)/10000
    FEMdata["PlotDivisions"]=PlotDivisions-1
    FEMdata["UnitScaling"]=rs.UnitScale(rs.UnitSystem(),4)

    try:
        with open(input_path, 'w') as file:
            file.write(prettyJSON(FEMdata))
        print "Input file saved to this location: "+ input_path
    except:
        input_path=[]
    return input_path,FEMdata,eleLoadPreview,supportPreview,materialPreview
