# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 08:38:31 2018
@author: Lasse
"""

import numpy as np
import math
from math import sqrt
from numpy import array, dot

np.set_printoptions(precision=5)
np.set_printoptions(linewidth=150)

def Abeam(X1,X2):
    # Calculate transformation matrix A 
    n = X2-X1                      # directionvector
    L = sqrt(dot(n,n))             # elementllength
    n = n/L                        # unitvector
    # Define transformationsmatrix
    A = array([ [n[0],  n[1],   0,  0,      0,      0],
                [-n[1],  n[0],   0,  0,      0,      0],
                [0,     0,      1,  0,      0,      0],
                [0,     0,      0,  n[0],   n[1],   0],
                [0,     0,      0,  -n[1],   n[0],   0],
                [0,     0,      0,  0,      0,      1]])
    return A,L

def kbeam(X1,X2,G):
    # Define element stiffness matrix 
    # make transformationsmatrix
    A,L = Abeam(X1,X2)
    # define k from local directions
    EA = G[0]*G[1]
    EI = G[0]*G[2]
    k = array([[EA/L,   0,            0,          -EA/L,      0,            0        ],
               [0,      12*EI/L**3,    6*EI/L**2,   0,          -12*EI/L**3,   6*EI/L**2 ],
               [0,      6*EI/L**2,     4*EI/L,     0,          -6*EI/L**2,    2*EI/L   ],
               [-EA/L,  0,            0,          EA/L,       0,            0        ],
               [0,      -12*EI/L**3,   -6*EI/L**2,  0,          12*EI/L**3,    -6*EI/L**2],
               [0,      6*EI/L**2,     2*EI/L,     0,          -6*EI/L**2,    4*EI/L   ]])
    # transform k to globale directions
    k = np.transpose(A).dot(k).dot(A)
    return k

def rbeam(X1,X2,dLe,ret):
    #Opstil elementlastvektor 
    #dan transformationsmatrix
    A,L = Abeam(X1,X2)
    #opstil r efter lokale retninger
    r = np.zeros((6,1))
    if ret == 0:
        p = dLe[0]*L/2
        r = np.transpose([p,0,0,p,0,0])
    elif ret == 1:
        p = dLe[1]*L/2
        m = dLe[1]*L**2/12
        r = np.transpose([0,p,m,0,p,-m])
    else:
      print("Fejl i specifikation af last!")

    r = dot(np.transpose(A),r);
    return r

def forceCalc(X1,X2,Ge,Ve,dLe,ret):
    #Calculate internal forces in an element 
    #f1: normalforce
    #f2: shearforce
    #m:  moment 
    #transformation matrix A
    A,L = Abeam(X1,X2)
    #element stiffness matrix
    k = kbeam(X1,X2,Ge)
    #opstil belastningsvektor efter lokale retninger
    if ret == 1:
        #calc local nodeforcevector
        Ve1=Ve
        Ve1[0]=0
        Ve1[3]=0
        re = A.dot(k).dot(Ve1)
        #print(re)
        p = dLe[1]*L/2
        m = dLe[1]*L**2/12
        r = np.transpose(array([[0,p,m,0,p,-m]]))
    elif ret == 0:
        #calc local nodeforcevector
        Ve2=Ve
        Ve2[1]=0
        Ve2[2]=0
        Ve2[4]=0
        Ve2[5]=0 
        re = A.dot(k).dot(Ve2)
        #print(re)
        p = dLe[0]*L/2
        r = np.transpose(array([[p,0,0,p,0,0]]))
    else:
        r = np.transpose(array([[0,0,0,0,0,0]]))
    re = re-r
    f1 = array([-re[0],re[3]])
    f2 = array([re[1],-re[4]])
    m  = array([-re[2],re[5]])
    return f1,f2,m

def writeDofPlot(X,T,D,V,skala,mFile,nrp):
    for el in range(len(T)):
        X1 = X[T[el][0]]
        X2 = X[T[el][1]]
        A,L = Abeam(X1,X2)
        #dan transformationsmatrix for flytninger
        Au=A[0:2,0:2]
        #hent lokale flytninger
        v=V[D[el]]
        #koordinater plus flytninger
        Xs=np.zeros((2,nrp))
        for i in range(1,nrp+1):
            s=(i-1)/(nrp-1)
            N=array([   [1-s,   0,                  0,                    s,    0,               0             ],
                        [0,     1-3*s**2+2*s**3,    (s-2*s**2+s**3)*L,    0,    3*s**2-2*s**3,    (-s**2+s**3)*L]])
            Xs=np.transpose(X[T[el][0]])*(1-s)+np.transpose(X[T[el][1]])*s+np.transpose(skala*(np.transpose(Au)).dot(N).dot(A).dot(v))
            Xs=np.transpose(Xs)
            if el==len(T)-1 and i==nrp:
                mFile.write(str(Xs[0][0])+","+str(Xs[1][0])+"\n")
            elif i==nrp:
                mFile.write(str(Xs[0][0])+","+str(Xs[1][0])+"_")
            else:
                mFile.write(str(Xs[0][0])+","+str(Xs[1][0])+"|")
    return 0

def writeForcePlots(X,T,S,s,dL,skala,mFile,nrp):
    plusStr=""
    for el in range(len(T)):
        # retningsvektor
        n = X[T[el][1]]-X[T[el][0]]
        # elementlængde
        L = sqrt(dot(n,n))
        # enhedsvektor
        n = n/L
    
        F1 = array([-n[1],n[0]])*S[el][0]*skala
        F2 = array([-n[1],n[0]])*S[el][1]*skala
        x1 = X[T[el][0]][0]
        x2 = X[T[el][1]][0]
        y1 = X[T[el][0]][1]
        y2 = X[T[el][1]][1]
        xm = (x1+x2)/2-n[1]*L/15
        ym = (y1+y2)/2+n[0]*L/15
        if not el==len(T)-1:
            plusStr+=str(xm)+","+str(ym)+"|"
        else:
            plusStr+=str(xm)+","+str(ym)+"\n"

        if s == 3:
            p = dL[el][1]
            m = -p*L**2/2
            Xp = np.zeros((nrp+4,1))
            Yp = np.zeros((nrp+4,1))
            Xp[0] = x1  
            Xp[1] = x1+F1[0]
            Yp[0] = y1  
            Yp[1] = y1+F1[1]
            Xp[nrp+3] = x2
            Xp[nrp+2] = x2+F2[0]
            Yp[nrp+3] = y2
            Yp[nrp+2] = y2+F2[1]
            
            for i in range(1,nrp+1):
                x = i/(nrp+1)
                mx = m*x*(1-x)
                m1 = array([-n[1],n[0]])*mx*skala
                Xp[i+1] = Xp[1]+i*(Xp[nrp+2]-Xp[1])/(nrp+1)+m1[0]
                Yp[i+1] = Yp[1]+i*(Yp[nrp+2]-Yp[1])/(nrp+1)+m1[1]
            Xp=np.transpose(Xp)[0]
            Yp=np.transpose(Yp)[0]
        else:
            Xp = array([x1,x1+F1[0],x2+F2[0],x2])
            Yp = array([y1,y1+F1[1],y2+F2[1],y2])
        for i in range(len(Xp)):
            if not i == len(Xp)-1:
                mFile.write(str(Xp[i])+","+str(Yp[i])+"|")
            elif i == len(Xp)-1 and el==len(T)-1:
                mFile.write(str(Xp[i])+","+str(Yp[i])+"\n")
            else:
                mFile.write(str(Xp[i])+","+str(Yp[i])+"_")
    mFile.write(plusStr)
    return 0

def strToList(string):
    string=string.replace(" ","")
    list=[]
    for str in string[2:-2].split("],["):
        list.append(str.split(","))
    return list

def FEM_frame():
    file = open('C:/livestock3d/data/livestockFEM/input_file.txt', 'r')
    my_lines = [line.strip()for line in file.readlines()]
    file.close()
    
    X=[[float(co[0]),float(co[1])] for co in strToList(my_lines[0])]
    
    T=[[int(co[0]),int(co[1])] for co in strToList(my_lines[1])]
  
    D=[[int(co[i]) for i in range(6)] for co in strToList(my_lines[2])]

    G=[[float(co[0]),float(co[1]),float(co[2])] for co in strToList(my_lines[3])]

    U=[int(co) for co in my_lines[4][1:-1].split(",")]

    bL=[[int(co[0]),float(co[1])] for co in strToList(my_lines[5])]

    dL=[[float(co[0]),float(co[1])] for co in strToList(my_lines[6])]
    
    Vskala = float(my_lines[7])
    Sskala = float(my_lines[8])
    nrp=int(my_lines[9])
    #Program
    
    X=array(X)
    T=array(T)
    D=array(D)
    G=array(G)
    U=array(U)
    bL=array(bL)
    dL=array(dL)
    
    #System stiffness matrix
    K=np.zeros((np.max(D)+1,np.max(D)+1))
    
    for el in range(len(T)):
        X1 = X[T[el][0]]
        X2 = X[T[el][1]]
        k=kbeam(X1,X2,G[el])
        de=D[el]
        for i,dei in enumerate(de):
            for j,dej in enumerate(de):
                K[dei,dej]+=k[i,j]
    
    #Define loadvector R
    R = np.zeros((np.max(D)+1,1)); 
    for el in range(len(T)):
        dLe=dL[el]
        if dLe[0]!=0:
            X1 = X[T[el][0]]
            X2 = X[T[el][1]]
            r=rbeam(X1,X2,dLe,0)
            de=D[el]
            for i,dei in enumerate(de):
                R[dei]+=r[i]
        
        if dLe[1]!=0:
            X1 = X[T[el][0]]
            X2 = X[T[el][1]]
            r=rbeam(X1,X2,dLe,1)
            de=D[el]
            for i,dei in enumerate(de):
                R[dei]+=r[i]
    
    for bLs in bL:
        d=int(bLs[0])
        R[d]=R[d]+bLs[1]
        
    dof=range(np.max(D)+1)
    du=U
    df=np.setdiff1d(dof,du)
    Kff = K[df,:][:,df]
    Kuu = K[du,:][:,du]
    Kfu = K[df,:][:,du]
    V=np.zeros((np.max(D)+1,1))
    Vu=V[du]
    Rf=R[df]
    Vf = np.linalg.solve(Kff,(Rf-dot(Kfu,Vu)))
    Ru = np.transpose(Kfu).dot(Vf)+Kuu.dot(Vu)
    V[df]=Vf
    V[du]=Vu
    
    #Plot displacement
    #Calculate forces
    F1=np.zeros((len(T),2))
    F2=np.zeros((len(T),2))
    M=np.zeros((len(T),2))
    
    for el in range(len(T)):
        X1 = X[T[el][0]]
        X2 = X[T[el][1]]
        de=D[el]
        f10,f20,m0=forceCalc(X1,X2,G[el],V[de],dL[el],0)
        f11,f21,m1=forceCalc(X1,X2,G[el],V[de],dL[el],1)
        F1[el]=np.transpose(f10)+np.transpose(f11)
        F2[el]=np.transpose(f20)+np.transpose(f21)
        M[el]=np.transpose(m0)+np.transpose(m1)
    
    mFile=open("C:/livestock3d/data/livestockFEM/result_file.txt","w")
    for i,v in enumerate(V):
        if not i == len(V)-1:
            mFile.write(str(v[0])+",")
        else:
            mFile.write(str(v[0])+"\n")
    for i,ru in enumerate(Ru):
        if not i == len(Ru)-1:
            mFile.write(str(ru[0])+",")
        else:
            mFile.write(str(ru[0])+"\n")
    for i,f1 in enumerate(F1):
        if not i == len(F1)-1:
            mFile.write(str(f1[0])+","+str(f1[1])+"|")
        else:
            mFile.write(str(f1[0])+","+str(f1[1])+"\n")
    for i,f2 in enumerate(F2):
        if not i == len(F2)-1:
            mFile.write(str(f2[0])+","+str(f2[1])+"|")
        else:
            mFile.write(str(f2[0])+","+str(f2[1])+"\n")
    for i,m in enumerate(M):
        if not i == len(M)-1:
            mFile.write(str(m[0])+","+str(m[1])+"|")
        else:
            mFile.write(str(m[0])+","+str(m[1])+"\n")
    writeDofPlot(X,T,D,V,Vskala,mFile,nrp)
    writeForcePlots(X,T,F1,1,dL,Sskala,mFile,nrp)
    writeForcePlots(X,T,F2,2,dL,Sskala,mFile,nrp)
    writeForcePlots(X,T,M,3,dL,Sskala,mFile,nrp)
    mFile.close()    
    return 0

FEM_frame()