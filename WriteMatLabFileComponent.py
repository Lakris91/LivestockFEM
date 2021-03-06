﻿"""Write, run and plot the MatLab script
    Inputs:
        MatLabNodes: MatLab string for defining the nodes
        MatLabElements: MatLab string for defining the elements
        MatLabDOFS: MatLab string for defining the degrees of freedom
        MatLabMaterial: MatLab string for defining the materials
        MatLabSupport: MatLab string for defining the supports
        MatLabNodeLoads: MatLab string for defining the node loads
        MatLabElementLoad: MatLab string for defining the element loads
        PlotScalingDeformation: Scaling factor of the node displacements in deformation plot
        PlotScalingForces: Scaling factor of forces in the force plots
        Run: Write and run MatLab script
        RefreshPlots: Press this when MatLab computation is done
    Output:
        Info: Info
        MLstring: Complete code written in MatLab
        Displacements: Displacement for each degree of freedom in the system
        ReactionForces: The three reaction forces in each of the supports
        NormalForces: Normal forces in both ends in each of the elements
        ShearForces: Shear forces in both ends in each of the elements
        MomentForces: Moment forces in both ends in each of the elements
        DeformationPlot: The deformation of the system
        MomentPlot: The moment forces of the system
        NormalPlot: The normal forces of the system
        ShearPlot: The shear forces of the system"""

__author__ = "LasseKristensen"

import os
import subprocess
import Grasshopper as GH
import rhinoscriptsyntax as rs

ghenv.Component.Params.Output[8].Hidden =True
ghenv.Component.Params.Output[9].Hidden = True
ghenv.Component.Params.Output[10].Hidden = True

def addFileWatcher(path):
    global watcher 
    watcher = GH.Kernel.GH_FileWatcher.CreateFileWatcher(path, GH.Kernel.GH_FileWatcherEvents.Created, GH.Kernel.GH_FileWatcher.FileChangedSimple(fileChanged))

def fileChanged(path):
    ghenv.Component.ExpireSolution(True)

def matlabIsInstalled():
    for path in os.environ["PATH"].split(";"):
        if os.path.isfile(os.path.join(path, "matlab.exe")):
            return True
    return False

def readPlotFile(filepath):
    file=open(filepath,"r")
    filestring=file.read()
    file.close()
    eleList=filestring.split("_")
    eleList=eleList[:-1]
    ptList=[]
    ThePlot=[]
    for ele in eleList:
        plotlines=[]
        plotpoints=[]
        if len(ele)>0:
            XYlist=ele.split("/")
            Xlist=XYlist[0].split(",")
            Ylist=XYlist[1].split(",")
        for i in range(len(Xlist)-1):
            plotpoints.append(rs.AddPoint(float(Xlist[i]),float(Ylist[i]),0))
        for i in range(len(plotpoints)-1):
            plotlines.append(rs.AddLine(plotpoints[i],plotpoints[i+1]))
        if len(plotlines)>1:
            ThePlot.append(rs.JoinCurves(plotlines))
        else:
            ThePlot=plotlines
    ThePlot=rs.ScaleObjects(ThePlot,(0,0,0),(1/rs.UnitScale(4),1/rs.UnitScale(4),1/rs.UnitScale(4)))
    return ThePlot

def readPlotSignFile(filepath):
    file=open(filepath,"r")
    filestring=file.read()
    file.close()
    eleList=filestring.split("_")
    plotpoints=[]
    for ele in eleList:
        XYlist=ele.split(",")
        if len(XYlist)>1:
            plotpoints.append(rs.AddPoint(float(XYlist[0]),float(XYlist[1]),0))
    ThePlot=rs.ScaleObjects(plotpoints,(0,0,0),(1/rs.UnitScale(4),1/rs.UnitScale(4),1/rs.UnitScale(4)))
    return ThePlot

def plusSign(position):
    pluspts=[[-0.02,0.125,0],[0.02,0.125,0],[0.02,0.02,0],[0.125,0.02,0],[0.125,-0.02,0],
    [0.02,-0.02,0],[0.02,-0.125,0],[-0.02,-0.125,0],[-0.02,-0.02,0],[-0.125,-0.02,0],
    [-0.125,0.02,0],[-0.02,0.02,0],[-0.02,0.125,0]]
    
    plusses=[]
    for posi in position:
        pluspos=[]
        for pluspt in pluspts:
            scaledpt=[pluspt[0]*(0.5/rs.UnitScale(4)),pluspt[1]*(0.5/rs.UnitScale(4))]
            xcoord = rs.PointCoordinates(posi)[0]+scaledpt[0]
            ycoord = rs.PointCoordinates(posi)[1]+scaledpt[1]
            pluspos.append(rs.AddPoint(xcoord,ycoord,0))
        plusses.append(rs.AddPolyline(pluspos))
    
    return plusses

if (MatLabNodes==None or 
MatLabElements==None or
MatLabDOFS==None or
MatLabMaterial==None or
MatLabSupport==None or
MatLabNodeLoads==None or
MatLabElementLoad==None):
    Info="All MatLab string inputs must be connected"
else:
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
    MLstring = MLstring.replace("PlotScalingDeformation",str(PlotScalingDeformation))
    MLstring = MLstring.replace("PlotScalingForces",str(PlotScalingForces))
    
    tempFPath=UOfolder+"TempMLfile.m"
    
    mFile=open(tempFPath,"w")
    mFile.write(MLstring)
    mFile.close()
    
    resultfile=UOfolder+"result.txt"
    deformationfile=UOfolder+"deformation.txt"
    momentfile=UOfolder+"momentforces.txt"
    normalfile=UOfolder+"normalforces.txt"
    shearfile=UOfolder+"shearforces.txt"
    momentsignfile=UOfolder+"momentsignforces.txt"
    normalsignfile=UOfolder+"normalsignforces.txt"
    shearsignfile=UOfolder+"shearsignforces.txt"
    changedfile=UOfolder+"changed.txt"
    Info=[]
    
    if matlabIsInstalled():
        if Run:
            P=subprocess.Popen("matlab -nosplash -nodesktop -minimize -r \"run "+tempFPath+"\"")
            if 'watcher' in globals():
                del watcher
            addFileWatcher(changedfile)
    else:
        Info.append("MatLab not installed")
    
    
    
    if os.path.isfile(resultfile) and os.path.isfile(deformationfile):
        if True:
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
            M=M[:-1]
            DeformationPlot=readPlotFile(deformationfile)
            MomentPlot=readPlotFile(momentfile)+plusSign(readPlotSignFile(momentsignfile))
            ShearPlot=readPlotFile(shearfile)+plusSign(readPlotSignFile(shearsignfile))
            NormalPlot=readPlotFile(normalfile)+plusSign(readPlotSignFile(normalsignfile))
        Displacements=V
        ReactionForces=Ru
        NormalForces=[]
        eleCount=int(len(F1)/2)
        [NormalForces.append(str(F1[i])+", "+str(F1[i+eleCount])) for i in range(int(len(F1)/2))]
        ShearForces=[]
        [ShearForces.append(str(F2[i])+", "+str(F2[i+eleCount])) for i in range(int(len(F2)/2))]
        MomentForces=[]
        [MomentForces.append(str(M[i])+", "+str(M[i+eleCount])) for i in range(int(len(M)/2))]
    else:
        Info.append("Deformation and resultsfile not found")
