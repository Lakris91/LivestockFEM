
listDOFS=NodeDOFS.replace("[","").replace("]","").split(",")
print listDOFS
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

for snn in SNN:
    print range(snn,snn+3)