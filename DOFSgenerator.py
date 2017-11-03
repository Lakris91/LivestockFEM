import rhinoscriptsyntax as rs
ESI=ElementStartIndex
EEI=ElementEndIndex
nodecount=max(ElementStartIndex+ElementEndIndex)-min(ElementStartIndex+ElementEndIndex)+1
dofcount=nodecount*3
AHE=AddHingeElement
AHN=AddHingeNode
uninodes=[]
doflist=[]
DOFSlist=[]
rngstart=1
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
    
    if len(AHE) == 0:
        for ahn in AHN:
            if ESI[i]==ahn:
                dofstart[2]=0
            if EEI[i]==ahn:
                dofend[2]=0
    
    DOFS=dofstart+dofend
    DOFSlist.append(DOFS)

DOFSflat = [item for sublist in DOFSlist for item in sublist]
while DOFSflat.count(0)<>0:
    m = range(1,len(DOFSflat))
    new=min(set(m)-set(DOFSflat))
    DOFSflat[DOFSflat.index(0)]=new
newDOFSLIST=[]
templist=[]
for dofs in DOFSflat:
    templist.append(dofs)
    if len(templist)==6:
        newDOFSLIST.append(templist)
        templist=[]
print newDOFSLIST