import os
import subprocess
import Grasshopper as GH

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

if matlab_installed():
    if run:
        subprocess.Popen("matlab -nosplash -nodesktop -r \"run "+tempFPath+"\"")
        #os.startfile("C:/Git/LKplugin/RunMLscript.bat")


