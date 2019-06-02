import json
import numpy as np
from livestockFEM_local import *
from livestockFEM_viz import *
import sys
import os
import math

np.set_printoptions(precision=5)
np.set_printoptions(linewidth=200)

class FEM_frame:
    def __init__(self,inDict):
        self.outDict={}
        self.outDict["ElementStiffnessSmall"]=[]
        self.outDict["ElementStiffnessSmallLocal"]=[]
        self.outDict["ElementStiffnessExpanded"]=[]
        self.outDict["DOFPlot"]=[]
        self.outDict["DefDist"]=[]
        self.outDict["PlusPos"]=[]
        self.outDict["ForcePlot1"]=[]
        self.outDict["ForcePlot2"]=[]
        self.outDict["ForcePlot3"]=[]
        self.outDict["MomentForcesPt"]=[]
        self.X = np.array(inDict["PyNodes"])
        self.T = np.array(inDict["PyElements"])
        self.D = np.array(inDict["PyDOFS"])
        self.G = np.array([mat[:3] for mat in inDict["PyMaterial"]])
        self.U = np.array(inDict["PySupport"])
        self.bL = np.array(inDict["PyNodeLoad"])
        self.dL = np.round(np.array(inDict["PyElementLoad"]),0)
        self.plotScale = inDict["UnitScaling"]
        self.Vskala = inDict["PlotScalingDeformation"]
        self.Sskala = inDict["PlotScalingForces"]/1000
        self.nrp = inDict["PlotDivisions"]

        self.K = self.sysStiff()
        self.F = self.loadVec()
        self.V,self.Re = self.calcDispReac()
        self.F1,self.F2,self.M = self.calcForces()
        self.outDict["Topology"]=[]
        for ele in self.T:
            self.outDict["Topology"].append((self.X[ele]*self.plotScale).tolist())
        self.outDict["Displacements"]=np.around(self.V,6).T.tolist()[0]
        self.outDict["Reactions"]=np.around(self.Re,0).T.tolist()[0]
        self.outDict["NormalForce1"]=np.around(self.F1,0).tolist()
        self.outDict["ShearForce2"]=np.around(self.F2,0).tolist()
        self.outDict["Moment3"]=np.around(self.M,0).tolist()
        self.outDict["UnitScaling"]=self.plotScale
        self.outDict["Nodes"]=self.X.tolist()
        self.outDict["PlotDivisions"]=self.nrp
        self.outDict["DeformTooLarge"]=int(any(self.V>10) or any(self.V<-10))
        self.exportDispPlot()
        self.exportForcePlot(1)
        self.exportForcePlot(2)
        self.exportForcePlot(3)
        previewSupports(self)
        previewHinge(self)
        previewNodeload(self)
        previewElementload(self)

    #Define System stiffness matrix
    def sysStiff(self):
        K = np.zeros((np.max(self.D)+1,np.max(self.D)+1))
        for el in range(len(self.T)):
            X1 = self.X[self.T[el][0]]
            X2 = self.X[self.T[el][1]]
            k,kl=eleStiff(X1,X2,self.G[el])
            kWA=k
            de=self.D[el]
            kWA = np.vstack([de, kWA])
            kWA = np.hstack([np.concatenate(([-1],de))[np.newaxis].T, kWA])
            self.outDict["ElementStiffnessSmall"].append(np.around(kWA,0).tolist())
            klWA=kl
            klWA = np.vstack([de, klWA])
            klWA = np.hstack([np.concatenate(([-1],de))[np.newaxis].T, klWA])
            self.outDict["ElementStiffnessSmallLocal"].append(np.around(klWA,0).tolist())
            KeWA = np.zeros((np.max(self.D)+1,np.max(self.D)+1))
            for i,dei in enumerate(de):
                for j,dej in enumerate(de):
                    K[dei,dej]+=k[i,j]
                    KeWA[dei,dej]+=k[i,j]
            KeWA = np.vstack([np.arange(np.ma.size(KeWA,1)), KeWA])
            KeWA = np.hstack([(np.arange(np.ma.size(KeWA,0))-1)[np.newaxis].T, KeWA])
            self.outDict["ElementStiffnessExpanded"].append(np.around(KeWA,0).tolist())
        KWA = K
        KWA = np.vstack([np.arange(np.ma.size(KWA,1)), KWA])
        KWA = np.hstack([(np.arange(np.ma.size(KWA,0))-1)[np.newaxis].T, KWA])
        self.outDict["SystemStiffness"]=np.around(KWA,0).tolist()
        return K

    #Define loadvector R
    def loadVec(self):
        F = np.zeros((np.max(self.D)+1,1))
        for el in range(len(self.T)):
            dLe=self.dL[el]
            X1 = self.X[self.T[el][0]]
            X2 = self.X[self.T[el][1]]
            f,fl=eleLoad(X1,X2,dLe)
            for i,dei in enumerate(self.D[el]):
                F[dei]+=f[i]
        for bLs in self.bL:
            d=int(bLs[0])
            F[d]+=bLs[1]
        return F

    # Calculate displacements and reactions
    def calcDispReac(self):
        dof=range(np.max(self.D)+1)
        ds=self.U
        Rs=-self.F[ds]
        df=np.setdiff1d(dof,ds)
        Kff = self.K[df,:][:,df]
        Ksf = self.K[ds,:][:,df]
        V=np.zeros((np.max(self.D)+1,1))
        Vs=V[ds]
        Rf=self.F[df]
        Vf = np.linalg.pinv(Kff) @ Rf
        Rf = Ksf @ Vf
        V[df]=Vf
        V[ds]=Vs
        Re=Rf+Rs
        return V,Re

    # Calculate internal forces
    def calcForces(self):
        F1=np.zeros((len(self.T),2))
        F2=np.zeros((len(self.T),2))
        M=np.zeros((len(self.T),2))
        for el in range(len(self.T)):
            X1 = self.X[self.T[el][0]]
            X2 = self.X[self.T[el][1]]
            de=self.D[el]
            f1,f2,m=forceCalc(X1,X2,self.G[el],self.V[de],self.dL[el])
            F1[el]=f1
            F2[el]=f2
            M[el]=m
        return F1,F2,M

    # Generate geometry for deformation plot
    def exportDispPlot(self):
        rou=int(6-math.log10(self.plotScale))
        div=self.nrp+2
        for el in range(len(self.T)):
            X1 = self.X[self.T[el][0]]
            X2 = self.X[self.T[el][1]]
            v=self.V[self.D[el]]
            DOFPlot,DefDist = deformationPlot(X1,X2,v,div,self.Vskala)
            self.outDict["DOFPlot"].append(np.around(np.array(DOFPlot)*self.plotScale,rou).tolist())
            self.outDict["DefDist"].append(np.around(np.array(DefDist)*self.plotScale,rou).tolist())


    # Generate geometry for force plots
    def exportForcePlot(self,s):
        if s==1: S=self.F1
        elif s==2: S=self.F2
        else: S=self.M
        rou=int(6-math.log10(self.plotScale))
        for el in range(len(self.T)):
            self.outDict["ForcePlot"+str(s)].append([])
            X1 = self.X[self.T[el][0]]
            X2 = self.X[self.T[el][1]]
            self.outDict["PlusPos"].append((plusPos(X1,X2)*self.plotScale).tolist())
            if s == 3:
                Xp,Yp,M = forcePlot(X1,X2,S[el],self.dL[el],self.nrp,self.Sskala,s)
                self.outDict["MomentForcesPt"].append(np.around(M,0).tolist())
            else:
                Xp,Yp = forcePlot(X1,X2,S[el],self.dL[el],self.nrp,self.Sskala,s)
            Xp = np.around(Xp*self.plotScale,rou)
            Yp = np.around(Yp*self.plotScale,rou)
            for i in range(len(Xp)):
                self.outDict["ForcePlot"+str(s)][el].append([Xp[i],Yp[i],0.0])

# Runs when file is run from Grasshopper
if __name__ == "__main__":
    with open(sys.argv[1]) as jsonfile:
        jsonDict = json.load(jsonfile)
    if "input_file.json" in os.path.split(sys.argv[1])[1]:
        resPath = sys.argv[1].replace("input_file.json","result_file.json")
    else:
        resPath = sys.argv[1].replace(".json","result_file.json")
    FEM=FEM_frame(jsonDict)
    dictstr=json.dumps(FEM.outDict).replace(', "',',\n "').replace("{","{\n ").replace("}","\n}")
    with open(resPath,"w") as file:
        file.write(dictstr)
