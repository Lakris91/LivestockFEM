import json
import numpy as np
from livestockFEM_local import *
from livestockFEM_viz import *
array=np.array
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

        self.X = array(inDict["PyNodes"])
        self.T = array(inDict["PyElements"])
        self.D = array(inDict["PyDOFS"])
        self.G = array([mat[:3] for mat in inDict["PyMaterial"]])
        self.U = array(inDict["PySupport"])
        self.bL = array(inDict["PyNodeLoad"])
        self.dL = np.round(array(inDict["PyElementLoad"]),0)
        self.plotScale = inDict["UnitScaling"]
        self.Vskala = inDict["PlotScalingDeformation"]
        self.Sskala = inDict["PlotScalingForces"]/1000
        self.nrp = inDict["PlotDivisions"]

        self.K = self.sysStiff()
        self.R = self.loadVec()

        self.V,self.Ru = self.calcDispReac()
        self.F1,self.F2,self.M = self.calcForces()

        topo=[]
        for ele in self.T:
            topo.append((self.X[ele]*self.plotScale).tolist())
        self.outDict["Topology"]=topo
        self.outDict["Displacements"]=self.V.T.tolist()[0]
        self.outDict["Reactions"]=self.Ru.T.tolist()[0]
        self.outDict["NormalForce1"]=self.F1.tolist()
        self.outDict["ShearForce2"]=self.F2.tolist()
        self.outDict["Moment3"]=self.M.tolist()
        self.outDict["UnitScaling"]=self.plotScale
        self.outDict["Nodes"]=self.X.tolist()
        self.outDict["PlotDivisions"]=self.nrp
        self.outDict["DeformTooLarge"]=int(any(self.V>1) or any(self.V<-1))

        self.exportDispPlot()
        self.exportForcePlot(1)
        self.exportForcePlot(2)
        self.exportForcePlot(3)

        previewSupports(self)
        previewHinge(self)
        previewNodeload(self)
        previewElementload(self)

    def sysStiff(self):
        K = np.zeros((np.max(self.D)+1,np.max(self.D)+1))
        #System stiffness matrix
        for el in range(len(self.T)):
            X1 = self.X[self.T[el][0]]
            X2 = self.X[self.T[el][1]]
            #Define element stiffness matrix
            k,kl=eleStiff(X1,X2,self.G[el])
            kk=k
            de=self.D[el]
            kk = np.vstack([de, kk])
            kk = np.hstack([np.concatenate(([-1],de))[np.newaxis].T, kk])
            self.outDict["ElementStiffnessSmall"].append(np.around(kk,0).tolist())
            kkl=kl
            kkl = np.vstack([de, kkl])
            kkl = np.hstack([np.concatenate(([-1],de))[np.newaxis].T, kkl])
            self.outDict["ElementStiffnessSmallLocal"].append(np.around(kkl,0).tolist())
            Kk = np.zeros((np.max(self.D)+1,np.max(self.D)+1))
            for i,dei in enumerate(de):
                for j,dej in enumerate(de):
                    K[dei,dej]+=k[i,j]
                    Kk[dei,dej]+=k[i,j]
            Kk = np.vstack([np.arange(np.ma.size(Kk,1)), Kk])
            Kk = np.hstack([(np.arange(np.ma.size(Kk,0))-1)[np.newaxis].T, Kk])
            self.outDict["ElementStiffnessExpanded"].append(np.around(Kk,0).tolist())
        KK = K
        KK = np.vstack([np.arange(np.ma.size(KK,1)), KK])
        KK = np.hstack([(np.arange(np.ma.size(KK,0))-1)[np.newaxis].T, KK])
        self.outDict["SystemStiffness"]=np.around(KK,0).tolist()
        return K

    def loadVec(self):
        R = np.zeros((np.max(self.D)+1,1))
        #Define loadvector R
        for el in range(len(self.T)):
            dLe=self.dL[el]
            if dLe[0]!=0:
                X1 = self.X[self.T[el][0]]
                X2 = self.X[self.T[el][1]]
                r=eleLoad(X1,X2,dLe,0)
                de=self.D[el]
                for i,dei in enumerate(de):
                    R[dei]+=r[i]

            if dLe[1]!=0:
                X1 = self.X[self.T[el][0]]
                X2 = self.X[self.T[el][1]]
                r=eleLoad(X1,X2,dLe,1)
                de=self.D[el]
                for i,dei in enumerate(de):
                    R[dei]+=r[i]
        for bLs in self.bL:
            d=int(bLs[0])
            R[d]+=bLs[1]

        return R

    def calcDispReac(self):
        dof=range(np.max(self.D)+1)
        du=self.U
        df=np.setdiff1d(dof,du)
        Kff = self.K[df,:][:,df]
        Kfu = self.K[df,:][:,du]
        Kuu = self.K[du,:][:,du]
        V=np.zeros((np.max(self.D)+1,1))
        Vu=V[du]
        Rf=self.R[df]
        Vf = np.linalg.solve(Kff,(Rf-Kfu @ Vu))
        Ru = Kfu.T @ Vf + Kuu @ Vu
        V[df]=Vf
        V[du]=Vu
        V = np.around(V,6)
        Ru = np.around(Ru,0)
        return V,Ru

    def calcForces(self):
        #Calculate forces
        F1=np.zeros((len(self.T),2))
        F2=np.zeros((len(self.T),2))
        M=np.zeros((len(self.T),2))

        for el in range(len(self.T)):
            X1 = self.X[self.T[el][0]]
            X2 = self.X[self.T[el][1]]
            de=self.D[el]
            f10,f20,m0=forceCalc(X1,X2,self.G[el],self.V[de],self.dL[el],0)
            f11,f21,m1=forceCalc(X1,X2,self.G[el],self.V[de],self.dL[el],1)
            F1[el]=f10.T + f11.T
            F2[el]=f20.T + f21.T
            M[el]=m0.T + m1.T
        F1 = np.around(F1,0)
        F2 = np.around(F2,0)
        M = np.around(M,0)
        return F1,F2,M

    def exportDispPlot(self):
        rou=int(6-math.log10(self.plotScale))
        #print(rou)
        div=self.nrp+2
        self.outDict["DOFPlot"]=[]
        self.outDict["DefDist"]=[]
        for el in range(len(self.T)):
            self.outDict["DOFPlot"].append([])
            self.outDict["DefDist"].append([])
            X1 = self.X[self.T[el][0]]
            X2 = self.X[self.T[el][1]]
            A,L = transMat(X1,X2)
            #dan transformationsmatrix for flytninger
            Au=A[0:2,0:2]
            #hent lokale flytninger
            v=self.V[self.D[el]]
            #koordinater plus flytninger
            Xs=np.zeros((2,div))
            for i in range(1,div+1):
                s=(i-1)/(div-1)
                N=array([   [1-s,   0,                  0,                    s,    0,               0             ],
                            [0,     1-3*s**2+2*s**3,    (s-2*s**2+s**3)*L,    0,    3*s**2-2*s**3,    (-s**2+s**3)*L]])
                Xs=(self.X[self.T[el][0]]).T*(1-s)+(self.X[self.T[el][1]]).T*s+((self.Vskala*Au.T) @ N @ A @ v).T
                Xs0=(self.X[self.T[el][0]]).T*(1-s)+(self.X[self.T[el][1]]).T*s+((Au.T) @ N @ A @ v).T
                Xe=[(X2[0]-X1[0])*((i-1)/(div-1))+X1[0],(X2[1]-X1[1])*((i-1)/(div-1))+X1[1]]
                disVec=(np.array(Xe)-Xs0)*self.plotScale
                Xs*=self.plotScale
                self.outDict["DOFPlot"][el].append(np.around(Xs[0],rou).tolist()+[0.0])
                self.outDict["DefDist"][el].append(np.around(disVec[0],rou).tolist()+[round(np.linalg.norm(disVec),rou)])
            self.outDict["DefDist"][el]=(array(self.outDict["DefDist"][el]).T).tolist()

    def exportForcePlot(self,s):
        if s==1: S=self.F1
        elif s==2: S=self.F2
        else: S=self.M
        rou=int(6-math.log10(self.plotScale))
        self.outDict["PlusPos"]=[]
        self.outDict["ForcePlot"+str(s)]=[]
        self.outDict["MomentForcesPt"]=[]
        for el in range(len(self.T)):
            self.outDict["ForcePlot"+str(s)].append([])
            # retningsvektor
            n = self.X[self.T[el][1]]-self.X[self.T[el][0]]
            # elementlængde
            L = sqrt(n @ n)
            # enhedsvektor
            n = n/L

            F01 = array([-n[1],n[0]])*S[el][0]*self.Sskala
            F02 = array([-n[1],n[0]])*S[el][1]*self.Sskala
            x1 = self.X[self.T[el][0]][0]
            x2 = self.X[self.T[el][1]][0]
            y1 = self.X[self.T[el][0]][1]
            y2 = self.X[self.T[el][1]][1]
            xm = ((x1+x2)/2-n[1]*L/15)*self.plotScale
            ym = ((y1+y2)/2+n[0]*L/15)*self.plotScale
            self.outDict["PlusPos"].append([xm,ym,0.0])

            if s == 3:
                p = self.dL[el][1]
                m = -1/2*p*L**2
                Xp = np.zeros((self.nrp+4,1))
                Yp = np.zeros((self.nrp+4,1))
                Yp0 = np.zeros((self.nrp+2,1))
                Yp0[0] = S[el][0]
                Yp0[-1] = S[el][1]
                Xp[0] = x1
                Xp[1] = x1+F01[0]
                Yp[0] = y1
                Yp[1] = y1+F01[1]
                Xp[-1] = x2
                Xp[-2] = x2+F02[0]
                Yp[-1] = y2
                Yp[-2] = y2+F02[1]
                for i in range(1,self.nrp+1):
                    x = i/(self.nrp+1)
                    mx = m*x*(1-x)
                    m1 = array([-n[1],n[0]])*mx*self.Sskala
                    Xp[i+1] = Xp[1]+i*(Xp[self.nrp+2]-Xp[1])/(self.nrp+1)+m1[0]
                    Yp[i+1] = Yp[1]+i*(Yp[self.nrp+2]-Yp[1])/(self.nrp+1)+m1[1]
                    Yp0[i] = Yp0[0]+i*(Yp0[-1]-Yp0[0])/(self.nrp+1)+mx
                Xp=Xp.T[0]*self.plotScale
                Yp=Yp.T[0]*self.plotScale
                Yp0=Yp0.T[0]
                self.outDict["MomentForcesPt"].append(np.around(Yp0,0).tolist())
            else:
                Xp = array([x1,x1+F01[0],x2+F02[0],x2])*self.plotScale
                Yp = array([y1,y1+F01[1],y2+F02[1],y2])*self.plotScale

            for i in range(len(Xp)):
                self.outDict["ForcePlot"+str(s)][el].append([round(Xp[i],rou),round(Yp[i],rou),0.0])



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
