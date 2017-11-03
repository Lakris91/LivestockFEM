import rhinoscriptsyntax as rs
i=1
MatLabNodes=""
for node in nodes:
    X,Y,Z = rs.PointCoordinates(node)
    nodesString= "X("+str(i)+",:) = ["+str(X)+" "+str(Y)+"];"
    MatLabNodes=MatLabNodes+nodesString+"\n"
    i+=1
MatLabNodes=MatLabNodes+"nno="+str(i-1)

i=1
MatLabElements=""
ESI=ElementStartIndex
EEI=ElementEndIndex
for j in range(len(ElementStartIndex)):
    elementString= "T("+str(i)+",:) = ["+str(ESI[j]+1)+" "+str(EEI[j]+1)+"];"
    MatLabElements=MatLabElements+elementString+"\n"
    i+=1
MatLabElements=MatLabElements+"nel="+str(i-1)