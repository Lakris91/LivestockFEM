import rhinoscriptsyntax as rs
ESI=ElementStartIndex
EEI=ElementEndIndex
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
    DOFS=dofstart+dofend
    DOFSlist.append(DOFS)
print DOFSlist


