"""Specify the supports of the system.
    Inputs:
        NodesIndex: Index of nodes with support
        NodeDOFS: Degrees of freedom for each node
        LockX: Lock displacement in x-direction
        LockY: Lock displacement in y-direction
        LockRotation: Lock rotation in node (cantilevered)
    Output:
        SupportDOFS: Each degrees of freedom that are locked/supported
        MatLabSupport: MatLab string for defining the supports"""

__author__ = "LasseKristensen"

SNN=NodesIndex
#Repeat last element of shortest list
if len(SNN)<>0 and len(LockX)<>0 and len(LockY)<>0 and len(LockRotation)<>0 and NodeDOFS<>None:
    listDOFS=NodeDOFS.replace("[","").replace("]","").replace(" ","").split(",")
    nodeLen = len(SNN)
    LockX.extend([LockX[-1]]*(nodeLen-len(LockX)))
    LockY.extend([LockY[-1]]*(nodeLen-len(LockY)))
    LockRotation.extend([LockRotation[-1]]*(nodeLen-len(LockRotation)))
    #Idiot proofing
    LockX= LockX[:nodeLen]
    LockY= LockY[:nodeLen]
    LockRotation= LockRotation[:nodeLen]
    
    SupportDOFS=[]
    for i,snn in enumerate(SNN):
        dofsInd=range(snn*3,snn*3+3)
        if LockX[i]:
            SupportDOFS.append(listDOFS[dofsInd[0]])
        if LockY[i]:
            SupportDOFS.append(listDOFS[dofsInd[1]])
        if LockRotation[i]:
            SupportDOFS.append(listDOFS[dofsInd[2]])
    print SupportDOFS
    
    MatLabSupport=""
    for j,DOF in enumerate(SupportDOFS):
        MatLabSupport=MatLabSupport+"U("+str(j+1)+")="+DOF+";\n"
