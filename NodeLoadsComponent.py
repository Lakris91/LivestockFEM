import rhinoscriptsyntax as rs
LNN=LoadNodesNo
listDOFS=NodeDOFS.replace("[","").replace("]","").replace(" ","").split(",")
if len(LNN)==0 or len(Direction)==0 or len(Newton)==0:
    MatLabNodeLoad="bL = [];"
else:
    #Repeat last element of shortest list
    nodeLen = len(LNN)
    Direction.extend([Direction[-1]]*(nodeLen-len(Direction)))
    Newton.extend([Newton[-1]]*(nodeLen-len(Newton)))
    Direction=Direction[:nodeLen]
    Newton=Newton[:nodeLen]
    
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
        xstring= "bL("+str(j)+",:)=["+str(listDOFS[int(lnn)*3])+" "+str(Newton[i]*vecX[i])+"];\n"
        j+=1
        ystring= "bL("+str(j)+",:)=["+str(listDOFS[int(lnn)*3+1])+" "+str(Newton[i]*vecY[i])+"];\n"
        j+=1
        MatLabNodeLoads=MatLabNodeLoads+xstring+ystring
