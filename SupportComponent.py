
listDOFS=NodeDOFS.replace("[","").replace("]","").replace(" ","").split(",")
SNN=SupportNodesNo
#Repeat last element of shortest list
if len(SNN)<>0 and len(LockX)<>0 and len(LockY)<>0 and len(LockRot)<>0:
    nodeLen = len(SNN)
    LockX.extend([LockX[-1]]*(nodeLen-len(LockX)))
    LockY.extend([LockY[-1]]*(nodeLen-len(LockY)))
    LockRot.extend([LockRot[-1]]*(nodeLen-len(LockRot)))
#Idiot sikring
LockX= LockX[:nodeLen]
LockY= LockY[:nodeLen]
LockRot= LockRot[:nodeLen]

SupportDOFS=[]
for i,snn in enumerate(SNN):
    dofsInd=range(snn*3,snn*3+3)
    if LockX[i]:
        SupportDOFS.append(listDOFS[dofsInd[0]])
    if LockY[i]:
        SupportDOFS.append(listDOFS[dofsInd[1]])
    if LockRot[i]:
        SupportDOFS.append(listDOFS[dofsInd[2]])
print SupportDOFS

MatLabSupport=""
for j,DOF in enumerate(SupportDOFS):
    MatLabSupport=MatLabSupport+"U("+str(j+1)+")="+DOF+";\n"
