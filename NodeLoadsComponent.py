"""Add node loads to the system
    Inputs:
        NodeIndex: Index of node to add load to
        NodeDOFS: Node degrees of freedom from element topology or ad hinge component
        Direction: Load direction as vector
        LoadSize: Size of load in Newton
    Output:
        MatLabNodeLoad: MatLab string for defining node load NOTE: Connect even if no node load are added"""

__author__ = "LasseKristensen"

import rhinoscriptsyntax as rs
LNN=NodeIndex
MatLabNodeLoads="bL = [];"
if len(LNN)<>0 and len(Direction)<>0 and len(LoadSize)<>0 and NodeDOFS<>None:
    #Repeat last element of shortest list
    listDOFS=NodeDOFS.replace("[","").replace("]","").replace(" ","").split(",")
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
    
    MatLabNodeLoads=""
    j=1
    for i,lnn in enumerate(LNN):
        xstring= "bL("+str(j)+",:)=["+str(listDOFS[int(lnn)*3])+" "+str(LoadSize[i]*vecX[i])+"];\n"
        j+=1
        ystring= "bL("+str(j)+",:)=["+str(listDOFS[int(lnn)*3+1])+" "+str(LoadSize[i]*vecY[i])+"];\n"
        j+=1
        MatLabNodeLoads=MatLabNodeLoads+xstring+ystring
