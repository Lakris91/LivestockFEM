"""Add element loads to the system
    Inputs:
        ElementIndex: Index of element to add load to
        ElementPlanes: Local planes for elements generated in topology component
        Direction: Load direction as vector
        LoadSize: Size of load in Newton per meter
        Global: Load direction is glabal not translated to element coordinate system
    Output:
        MatLabElementLoad: MatLab string for defining element load NOTE: Connect even if no element load are added"""

__author__ = "LasseKristensen"

import rhinoscriptsyntax as rs
LEN=ElementIndex
MatLabElementLoad="dL = zeros(nel,2);\n"
if not (len(LEN)==0 or len(Direction)==0 or len(LoadSize)==0 or len(ElementPlanes)==0 or len(Global)==0):
    #Repeat last element of shortest list
    eleLen = len(LEN)
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
            #vec=rs.XformCPlaneToWorld((0,0,0),ElementPlanes[LEN[i]])
            vpt=rs.XformWorldToCPlane(vec,ElementPlanes[LEN[i]])
            opt=rs.XformWorldToCPlane((0,0,0),ElementPlanes[LEN[i]])
            #print rs.EvaluatePlane(ElementPlanes[LEN[i]],[0,0])
            vec=rs.VectorCreate(vpt,opt)
        print vec
        MLx="dL("+str(LEN[i]+1)+",:)=[1 "+str(vec[0]*LoadSize[i])+"];\n"
        MLy="dL("+str(LEN[i]+1)+",:)=[2 "+str(vec[1]*LoadSize[i])+"];\n"
        MatLabElementLoad=MatLabElementLoad+MLx+MLy