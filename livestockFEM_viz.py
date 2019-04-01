import numpy as np
from numpy import array
from numpy.linalg import norm
import math

def previewSupports(self):
    NodesIndex=[]
    NodesCoord=[]
    Locks=[]
    for sup in self.U:
        for i,dof in enumerate(self.D):
            if sup in dof:
                pos = dof.tolist().index(sup)
                node=self.T[i][int(math.floor(pos/3))]
                if not node in NodesIndex:
                    NodesIndex.append(self.T[i][int(math.floor(pos/3))])
                    NodesCoord.append(self.X[self.T[i][int(math.floor(pos/3))]])
                    Locks.append([False,False,False])
                if pos%3 == 0:
                    Locks[NodesIndex.index(node)][0]=True
                if pos%3 == 1:
                    Locks[NodesIndex.index(node)][1]=True
                if pos%3 == 2:
                    Locks[NodesIndex.index(node)][2]=True

    bboxmaxX=max([x for x,y in self.X])*self.plotScale
    bboxminX=min([x for x,y in self.X])*self.plotScale
    bboxmaxY=max([y for x,y in self.X])*self.plotScale
    bboxminY=min([y for x,y in self.X])*self.plotScale
    fixed=[(-0.15,0.0),(-0.15,-0.30),(0.15,-0.30),(0.15,-0.0),(-0.15,0.0)]
    pinned=[(0.15, -0.3), (-0.15, -0.3), (-0.02, -0.04), (-0.035, -0.035), (-0.050, 0.0), (-0.035, 0.035), (0.0, 0.050), (0.035, 0.035), (0.050, 0.0), (0.035, -0.035), (0.02, -0.04), (0.15, -0.3)]
    roller=[(-0.035, 0.035), (0.0, 0.050), (0.035, 0.035), (0.050, 0.0), (0.035, -0.035), (0.02, -0.04), (0.15, -0.3), (0.075, -0.3),
    (0.04, -0.315), (0.025, -0.35), (0.04, -0.385), (0.075, -0.4), (0.11, -0.385), (0.125, -0.35), (0.11, -0.315), (0.075, -0.3),
    (-0.075, -0.3), (-0.11, -0.315), (-0.125, -0.35), (-0.11, -0.385), (-0.075, -0.4), (-0.04, -0.385), (-0.025, -0.35), (-0.04, -0.315),
    (-0.075, -0.3), (-0.15, -0.3), (-0.02, -0.04), (-0.035, -0.035), (-0.050, 0.0), (-0.035, 0.035)]
    fixed=[(x*self.plotScale,y*self.plotScale) for x,y in fixed]
    pinned=[(x*self.plotScale,y*self.plotScale) for x,y in pinned]
    roller=[(x*self.plotScale,y*self.plotScale) for x,y in roller]
    NodesCoord=[(x*self.plotScale,y*self.plotScale) for x,y in NodesCoord]
    sim=0.05*self.plotScale
    pllines=[]
    for i, no in enumerate(NodesCoord):
        x,y=no
        xbound = abs(x-bboxmaxX)>abs(x-bboxminX)
        ybound = abs(y-bboxmaxY)>abs(y-bboxminY)
        bound = [abs(y-bboxminY),abs(y-bboxmaxY),abs(x-bboxminX),abs(x-bboxmaxX)].index(min(abs(x-bboxmaxX),abs(x-bboxminX),abs(y-bboxmaxY),abs(y-bboxminY)))
        print([bboxminY,bboxmaxY,bboxminX,bboxmaxX])
        print([abs(y-bboxminY),abs(y-bboxmaxY),abs(x-bboxminX),abs(x-bboxmaxX)])
        loco = Locks[i].count(True)
        if loco == 1:
            if Locks[i][0]==True:
                if xbound:
                    pllines.append([[ly+x,lx+y] for lx,ly in roller])
                else:
                    pllines.append([[-ly+x,lx+y] for lx,ly in roller])
            elif Locks[i][1]==True:
                if ybound:
                    pllines.append([[lx+x,ly+y] for lx,ly in roller])
                else:
                    pllines.append([[lx+x,-ly+y] for lx,ly in roller])
        elif loco == 2:
            if Locks[i][0]==True and Locks[i][1]==True:
                if bound==0:
                    pllines.append([[lx+x,ly+y] for lx,ly in pinned])
                elif bound==1:
                    pllines.append([[lx+x,-ly+y] for lx,ly in pinned])
                elif bound==2:
                    pllines.append([[ly+x,lx+y] for lx,ly in pinned])
                elif bound==3:
                    pllines.append([[-ly+x,-lx+y] for lx,ly in pinned])
            elif Locks[i][0]==True and Locks[i][2]==True:
                if xbound:
                    pllines.append([[(ly-sim)+x,lx+y] for lx,ly in roller])
                else:
                    pllines.append([[-(ly-sim)+x,lx+y] for lx,ly in roller])
            elif Locks[i][1]==True and Locks[i][2]==True:
                if ybound:
                    pllines.append([[lx+x,(ly-sim)+y] for lx,ly in roller])
                else:
                    pllines.append([[lx+x,-(ly-sim)+y] for lx,ly in roller])
        elif loco == 3:
            if bound==0:
                pllines.append([[lx+x,ly+y] for lx,ly in fixed])
            elif bound==1:
                pllines.append([[lx+x,-ly+y] for lx,ly in fixed])
            elif bound==2:
                pllines.append([[ly+x,lx+y] for lx,ly in fixed])
            elif bound==3:
                pllines.append([[-ly+x,-lx+y] for lx,ly in fixed])
    self.outDict["SupportViz"]=pllines

def previewHinge(self):
    hinge=array([[-0.035, -0.035], [-0.050, 0.0], [-0.035, 0.035], [0.0, 0.050], [0.035, 0.035], [0.050, 0.0], [0.035, -0.035], [0.0, -0.050],[-0.035, -0.035]])
    cirSize=100
    #print[self.D)
    rotDOF=[]
    rotDOFel=[]
    addDOT=[]
    for i,node in enumerate(self.X):
        rotDOF.append([])
        rotDOFel.append([])
        for j,el in enumerate(self.T):
            if i==el[0]:
                rotDOF[i].append(self.D[j][2])
                rotDOFel[i].append([j,0])
            if i==el[1]:
                rotDOF[i].append(self.D[j][5])
                rotDOFel[i].append([j,1])
        if len(set(rotDOF[i])) == 1:
            rotDOF[i]=[]
            rotDOFel[i]=[]
        addDOT.append([])
        for dof in rotDOF[i]:
            if rotDOF[i].count(dof)==1:
                addDOT[i].append(True)
            else:
                addDOT[i].append(False)
    dotPts=[]
    for i,ad in enumerate(addDOT):
        if len(ad)==0:
            continue
        elif all(ad):
            dotPts.append((self.X[i]*self.plotScale).tolist())
        else:
            for j,add in enumerate(ad):
                if add:
                    ele=rotDOFel[i][j][0]
                    no=rotDOFel[i][j][1]
                    Node=self.outDict["Topology"][ele][no]
                    if no == 0:
                        vec=array(self.outDict["Topology"][ele][1])-array(self.outDict["Topology"][ele][0])
                        vecNorm=vec/norm(vec)*(50)
                        dotPts.append((array(Node)+vecMove).tolist())
                    else:
                        vec=array(self.outDict["Topology"][ele][0])-array(self.outDict["Topology"][ele][1])
                        vecMove=vec/norm(vec)*(50)
                        dotPts.append((array(Node)+vecMove).tolist())
    dots=[]
    for dotPt in dotPts:
        dots.append((dotPt-hinge*self.plotScale).tolist())
    self.outDict["HingeViz"]=dots

def previewNodeload(self):
    sca=self.Sskala*self.plotScale
    self.outDict["ForceScale"]=sca
    if not (len(self.bL)==1 and self.bL[0][1]==0):
        vec=[]
        nodelist=[]
        for dof,lsize in self.bL:
            node=int((int(dof)-int(dof)%3)/3)
            if not node in nodelist:
                vec.append([0.0,0.0])
                nodelist.append(node)
            if bool(int(dof)%3):
                vec[nodelist.index(node)][1]=lsize*sca
            if not bool(int(dof)%3):
                vec[nodelist.index(node)][0]=lsize*sca
        sizelist=[int(round(norm(array(lo))*(1/sca),0)) for lo in vec]
        arrows=[]
        for size in sizelist:
            x=-size*0.1*sca
            y=x/2
            arrows.append([[x,y],[x,-y]])
        arrows=array(arrows)

        for i,v in enumerate(vec):
            if v[0]==0 and v[1]>0:
                ang = math.pi/2
            elif v[0]==0 and v[1]<0:
                ang = -math.pi/2
            else:
                ang = math.atan(v[1]/v[0])
            for j,arro in enumerate(arrows[i]):
                x=arro[0]
                y=arro[1]
                arrows[i][j][0]=x*math.cos(ang)-y*math.sin(ang)
                arrows[i][j][1]=x*math.sin(ang)+y*math.cos(ang)
        pllines=[]
        for i,no in enumerate((self.X[nodelist]*self.plotScale)-(array(vec)*(sca/2))):
            pllines.append([])
            pllines[i].append((no+arrows[i][1]).tolist())
            pllines[i].append((no+arrows[i][0]).tolist())
            pllines[i].append(no.tolist())
            pllines[i].append((no+arrows[i][1]).tolist())
            pllines[i].append((no-(array(vec)[i]*0.1)).tolist())
            pllines[i].append((no-array(vec)[i]).tolist())
    else:
        pllines=[]
    self.outDict["NodeloadViz"]=pllines

def previewElementload(self):
    sca=self.Sskala*self.plotScale
    self.outDict["ForceScale"]=sca
    vec=[]
    nodelist=[]
    loadvec=np.copy(self.dL)
    divPts0=[]
    vecPts0=[]
    sizelist=[]
    for i,load in enumerate(self.dL):
        if load[0]==0.0 and load[1]==0.0:
            continue
        nodes=array(self.outDict['Topology'])[i]
        #print(nodes)
        v = nodes[1]-nodes[0]
        if v[0]==0 and v[1]>0:
            ang = math.pi/2
        elif v[0]==0 and v[1]<0:
            ang = -math.pi/2
        else:
            ang = math.atan(v[1]/v[0])

        x=load[0]
        y=load[1]
        loadvec[i][0]=x*math.cos(ang)-y*math.sin(ang)
        loadvec[i][1]=x*math.sin(ang)+y*math.cos(ang)

        divPts=nodes[0]+(nodes[1]-nodes[0])*(np.vstack(np.arange(9)/8))

        divPts0.append(divPts.tolist())
        vecPts0.append((loadvec[i]*sca).tolist())
        sizelist.append(norm(load))

    arrows=[]
    for size in sizelist:
        x=-size*((sca/10)/2)
        y=x/2
        arrows.append([[x,y],[x,-y]])
    arrows=array(arrows)

    for i,v in enumerate(vecPts0):
        if v[0]==0 and v[1]>0:
            ang = math.pi/2
        elif v[0]==0 and v[1]<0:
            ang = -math.pi/2
        else:
            ang = math.atan(v[1]/v[0])
        for j,arro in enumerate(arrows[i]):
            x=arro[0]
            y=arro[1]
            arrows[i][j][0]=x*math.cos(ang)-y*math.sin(ang)
            arrows[i][j][1]=x*math.sin(ang)+y*math.cos(ang)

    divPts0=array(divPts0)

    vecPts0=np.reshape(np.repeat(array(vecPts0), 9, axis=0),np.shape(divPts0))
    pllines0=[]
    for i,vec in enumerate(vecPts0):
        pllines=[]
        for j,no in enumerate(divPts0[i]-(vec*(sca/2))):
            pllines.append([])
            pllines[j].append((no+arrows[i][1]).tolist())
            pllines[j].append((no+arrows[i][0]).tolist())
            pllines[j].append(no.tolist())
            pllines[j].append((no+arrows[i][1]).tolist())
            pllines[j].append((no-(vec[i]*0.05)).tolist())
            pllines[j].append((no-vec[i]).tolist())
        pllines.append([(((divPts0[i]-(vec*(sca/2)))-vec)[0]).tolist(),(((divPts0[i]-(vec*(sca/2)))-vec)[-1]).tolist()])
        pllines0.append(pllines)
    self.outDict["ElementloadViz"]=pllines0
