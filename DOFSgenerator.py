import rhinoscriptsyntax as rs
ESI=ElementStartIndex
EEI=ElementEndIndex
nodecount=max(ElementStartIndex+ElementEndIndex)-min(ElementStartIndex+ElementEndIndex)+1
dofcount=nodecount*3
AHE=AddHingeElement
AHN=AddHingeNode
#Repeat last element of shortest list
if len(AHE)<>0 and len(AHN)<>0:
    maxlen = max(len(AHE),len(AHN))
    AHE.extend([AHE[-1]]*(maxlen-len(AHE)))
    AHN.extend([AHN[-1]]*(maxlen-len(AHN)))
uninodes=[]
doflist=[]
DOFSlist=[]
rngstart=1
#Define no-hinge DOFS
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

if len(AHN)<>0:
    #Add position of hinge
    for j in range(len(DOFSlist)):
        if len(AHE) == 0:
            for ahn in AHN:
                print inidof==ahn
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
    
    #Add hinge
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
    DOFSlist = newDOFSLIST
DegreesOfFreedom=[]
for defree in DOFSlist:
    DegreesOfFreedom.append(str(defree))

MatLabDOFS=""
for k, dofree in enumerate(DegreesOfFreedom):
    MatLabDOF= "D("+str(k+1)+",:)="+ dofree.replace(",","")+";\n"
    MatLabDOFS=MatLabDOFS+MatLabDOF
MatLabDOFS=MatLabDOFS+"nd="+str(max(DOFSflat))+";"



