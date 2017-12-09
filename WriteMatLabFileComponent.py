import os
import subprocess
import Grasshopper as GH
import time
import rhinoscriptsyntax as rs

def matlabIsInstalled():
    for path in os.environ["PATH"].split(";"):
        if os.path.isfile(os.path.join(path, "matlab.exe")):
            return True
    return False

UOfolder= GH.Folders.UserObjectFolders[0]+"LKplugin\\"

ML=open(UOfolder+"RammeLKpluginTemplate.m","r")
MLstring=ML.read()
ML.close()

MLstring = MLstring.replace("MatLabNodes",MatLabNodes)
MLstring = MLstring.replace("MatLabElements",MatLabElements)
MLstring = MLstring.replace("MatLabDOFS",MatLabDOFS)
MLstring = MLstring.replace("MatLabMaterial",MatLabMaterial)
MLstring = MLstring.replace("MatLabSupport",MatLabSupport)
MLstring = MLstring.replace("MatLabNodeLoads",MatLabNodeLoads)
MLstring = MLstring.replace("MatLabElementLoad",MatLabElementLoad)
MLstring = MLstring.replace("MatLabElementLoad",MatLabElementLoad)
MLstring = MLstring.replace("PlotScalingDeformation",str(PlotScalingDeformation[0]))
MLstring = MLstring.replace("PlotScalingForces",str(PlotScalingForces[0]))

tempFPath=UOfolder+"TempMLfile.m"

mFile=open(tempFPath,"w")
mFile.write(MLstring)
mFile.close()

print tempFPath

resultfile=UOfolder+"result.txt"
deformationfile=UOfolder+"deformation.txt"

deformationcurves=[]
if matlabIsInstalled():
    if run:
        subprocess.Popen("matlab -nosplash -nodesktop -minimize -r \"run "+tempFPath+"\"")

if os.path.isfile(resultfile) and os.path.isfile(deformationfile):
    if refresh:
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
        eleList=defstring.split("_")
        ptList=[]
        for ele in eleList:
            deformationpoints=[]
            if len(ele)>0:
                XYlist=ele.split("/")
                Xlist=XYlist[0].split(",")
                Ylist=XYlist[1].split(",")
            for i in range(len(Xlist)-1):
                deformationpoints.append(rs.AddPoint(float(Xlist[i]),float(Ylist[i]),0))
            deformationcurves.append(rs.AddInterpCurve(deformationpoints))
print deformationcurves