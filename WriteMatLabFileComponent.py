ML=open("C:/Git/LKplugin/RammeLKpluginTemplate.m","r")
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
#print MLstring

mFile=open("C:/Git/LKplugin/TempMLfile.m","w")
mFile.write(MLstring)
mFile.close()

import os
import subprocess
if run:
    subprocess.Popen("matlab -nosplash -nodesktop -r \"run C:\Git\LKplugin\TempMLfile.m\"")
    #os.startfile("C:/Git/LKplugin/RunMLscript.bat")