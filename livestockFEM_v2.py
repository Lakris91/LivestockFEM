import json
import numpy as np
from livestockFEM_local import *
array=np.array

np.set_printoptions(precision=5)
np.set_printoptions(linewidth=200)

class FEM_frame:

    def __init__(self,inDict):
        #with open(input_file, 'r') as file:
        #    inDict=json.loads(file.read())
        self.X = array(inDict["PyNodes"])
        self.T = array(inDict["PyElements"])
        self.D = array(inDict["PyDOFS"])
        self.G = array(inDict["PyMaterial"])
        self.U = array(inDict["PySupport"])
        self.bL = array(inDict["PyNodeLoad"])
        self.dL = array(inDict["PyElementLoad"])
        self.plotScale = inDict["UnitScaling"]
        self.Vskala = inDict["PlotScalingDeformation"]
        self.Sskala = inDict["PlotScalingForces"]/self.plotScale
        self.nrp = inDict["PlotDivisions"]

        self.K = self.sysStiff()
        self.R = self.loadVec()

        self.V,self.Ru = self.calcDispReac()
        self.F1,self.F2,self.M = self.calcForces()

        self.outDict={}
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

        self.exportDispPlot()
        self.exportForcePlot(1)
        self.exportForcePlot(2)
        self.exportForcePlot(3)
        self.createJSON("result_file.json")

    def sysStiff(self):
        K = np.zeros((np.max(self.D)+1,np.max(self.D)+1))
        #System stiffness matrix
        for el in range(len(self.T)):
            X1 = self.X[self.T[el][0]]
            X2 = self.X[self.T[el][1]]
            #Define element stiffness matrix
            k=eleStiff(X1,X2,self.G[el])
            de=self.D[el]
            for i,dei in enumerate(de):
                for j,dej in enumerate(de):
                    K[dei,dej]+=k[i,j]
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
        return F1,F2,M

    def exportDispPlot(self):
        self.outDict["DOFPlot"]=[]
        for el in range(len(self.T)):
            self.outDict["DOFPlot"].append([])
            X1 = self.X[self.T[el][0]]
            X2 = self.X[self.T[el][1]]
            A,L = transMat(X1,X2)
            #dan transformationsmatrix for flytninger
            Au=A[0:2,0:2]
            #hent lokale flytninger
            v=self.V[self.D[el]]
            #koordinater plus flytninger
            Xs=np.zeros((2,self.nrp))
            for i in range(1,self.nrp+1):
                s=(i-1)/(self.nrp-1)
                N=array([   [1-s,   0,                  0,                    s,    0,               0             ],
                            [0,     1-3*s**2+2*s**3,    (s-2*s**2+s**3)*L,    0,    3*s**2-2*s**3,    (-s**2+s**3)*L]])
                Xs=(self.X[self.T[el][0]]).T*(1-s)+(self.X[self.T[el][1]]).T*s+((self.Vskala*Au.T) @ N @ A @ v).T

                Xs*=self.plotScale
                self.outDict["DOFPlot"][el].append(Xs[0].tolist()+[0.0])

    def exportForcePlot(self,s):
        if s==1: S=self.F1
        elif s==2: S=self.F2
        else: S=self.M
        self.outDict["PlusPos"]=[]
        self.outDict["ForcePlot"+str(s)]=[]
        for el in range(len(self.T)):
            self.outDict["ForcePlot"+str(s)].append([])
            # retningsvektor
            n = self.X[self.T[el][1]]-self.X[self.T[el][0]]
            # elementlængde
            L = sqrt(n @ n)

            # enhedsvektor
            n = n/L
            #n=array([1,0])
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
                m = -p*L**2/2
                Xp = np.zeros((self.nrp+4,1))
                Yp = np.zeros((self.nrp+4,1))
                #Yp0 = np.zeros((self.nrp+4,1))
                Xp[0] = x1
                Xp[1] = x1+F01[0]
                Yp[0] = y1
                Yp[1] = y1+F01[1]
                #Yp0[0] = 0
                #Yp0[1] = F01[1]
                Xp[self.nrp+3] = x2
                Xp[self.nrp+2] = x2+F02[0]
                Yp[self.nrp+3] = y2
                Yp[self.nrp+2] = y2+F02[1]
                #Yp0[self.nrp+3] = 0
                #Yp0[self.nrp+2] = F02[1]
                for i in range(1,self.nrp+1):
                    x = i/(self.nrp+1)
                    mx = m*x*(1-x)
                    m1 = array([-n[1],n[0]])*mx*self.Sskala
                    Xp[i+1] = Xp[1]+i*(Xp[self.nrp+2]-Xp[1])/(self.nrp+1)+m1[0]
                    Yp[i+1] = Yp[1]+i*(Yp[self.nrp+2]-Yp[1])/(self.nrp+1)+m1[1]
                    #Yp0[i+1] = Yp0[1]+i*(Yp0[self.nrp+2]-Yp0[1])/(self.nrp+1)
                Xp=Xp.T[0]*self.plotScale
                Yp=Yp.T[0]*self.plotScale
                #Yp0=Yp0.T[0]*self.plotScale
                print(Yp.T)
                #print("el",el,":",Yp0.T)
            else:
                Xp = array([x1,x1+F01[0],x2+F02[0],x2])*self.plotScale
                Yp = array([y1,y1+F01[1],y2+F02[1],y2])*self.plotScale

            for i in range(len(Xp)):
                self.outDict["ForcePlot"+str(s)][el].append([Xp[i],Yp[i],0.0])

    def createJSON(self,output_file):
        dictstr=str(self.outDict).replace("'",'"').replace(', "',',\n "').replace("{","{\n ").replace("}","\n}")
        with open(output_file,"w") as file:
            file.write(dictstr)

if __name__ == "__main__":
    FEM=FEM_frame('C:/livestock3d/data/livestockFEM/input_file.json')
