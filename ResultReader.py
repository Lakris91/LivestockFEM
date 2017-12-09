import rhinoscriptsyntax as rs

result=open(resultfile,"r")
resultstring=result.read()
result.close()
resList=resultstring.split(",")
V=[]
Ru=[]
F1=[]
F2=[]
M=[]
listlist=[V,Ru,F1,F2,M]
listCount=0
for res in resList:
    if res[:1]=="/":
        listCount+=1
        res=res.replace("/","")
    listlist[listCount].append(res)


deformation=open(deformationfile,"r")
defstring=deformation.read()
deformation.close()
deformationcurves=[]
eleList=defstring.split("_")
ptList=[]
for ele in eleList:
    deformationpoints=[]
    if len(ele)>0:
        XYlist=ele.split("/")
        Xlist=XYlist[0].split(",")
        Ylist=XYlist[1].split(",")
    for i in range(len(Xlist)-1):
        print str(Xlist[i])+"  "+str(Ylist[i])
        deformationpoints.append(rs.AddPoint(float(Xlist[i]),float(Ylist[i]),0))
    deformationcurves.append(rs.AddInterpCurve(deformationpoints))
