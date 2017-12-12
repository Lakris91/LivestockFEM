"""Add hinges in specified nodes.
    Inputs:
        ElementStartIndex: Index of start node of element
        ElementEndIndex: Index of end node of element
        NodeDOFS: Degrees of freedom for each node (no hinges)
        AddHingeNode: Index of node to add hinge to
        AddHingeElement: If no input hinges are introduced in all specified nodes, else hinge only introduced if matching with specified element(by index).
    Output:
        DegreesOfFreedom: Degrees of freedom for each element
        NodeDOFS: Degrees of freedom for each node
        MatLabDOFS: MatLab string for the degrees of freedom (with hinges)"""

__author__ = "LasseKristensen"

import rhinoscriptsyntax as rs
ESI=ElementStartIndex
EEI=ElementEndIndex
AHE=AddHingeElement
AHN=AddHingeNode

if len(AHN)<>0 and len(EEI)<>0 and len(ESI)<>0 and NodeDOFS<>None:
    #Repeat last element of shortest list
    if len(AHE)<>0 and len(AHN)<>0:
        maxlen = max(len(AHE),len(AHN))
        AHE.extend([AHE[-1]]*(maxlen-len(AHE)))
        AHN.extend([AHN[-1]]*(maxlen-len(AHN)))
    
    NodeDOFS=NodeDOFS.replace("[[","").replace("]]","").split("], [")
    DOFSlist=[]
    for i in range(len(ESI)):
        DOFSlist.append(map(int,NodeDOFS[ESI[i]].split(","))+map(int,NodeDOFS[EEI[i]].split(",")))
    
    DOFSflat = [item for sublist in DOFSlist for item in sublist]
    
    if len(AHN)<>0:
        #Add position of hinge
        for j in range(len(DOFSlist)):
            if len(AHE) == 0:
                for ahn in AHN:
                    if ESI[j]==ahn:
                        DOFSlist[j][2]=0
                    if EEI[j]==ahn:
                        DOFSlist[j][5]=0
            else:
                for ahe in AHE:
                    if ahe==j:
                        for ahn in AHN:
                            if ESI[j]==ahn:
                                DOFSlist[j][2]=0
                            if EEI[j]==ahn:
                                DOFSlist[j][5]=0
        DOFSflat = [item for sublist in DOFSlist for item in sublist]
        #Add hinge
        indices = [b for b, a in enumerate(DOFSflat) if a == 0]
        lowest =[c+1 for c in range(len(DOFSflat)) if DOFSflat.count(c+1)==0]
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


