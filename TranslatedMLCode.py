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

def rbeam(X1,X2,dLe):
    #Opstil elementlastvektor 
    #dan transformationsmatrix
    A,L = Abeam(X1,X2)
    #opstil r efter lokale retninger
    r = np.zeros((6,1))
    if dLe[0] == 0:
        p = dLe[1]*L/2
        r = np.transpose([p,0,0,p,0,0])
    elif dLe[0] == 1:
        p = dLe[1]*L/2
        m = dLe[1]*L**2/12
        r = np.transpose([0,p,m,0,p,-m])
    else:
      print("Fejl i specifikation af last!")

    r = dot(np.transpose(A),r);
    return r

def forceCalc(X1,X2,Ge,Ve,dLe):
    #Calculate internal forces in an element 
    #f1: normalforce
    #f2: shearforce
    #m:  moment 
    #transformation matrix A
    A,L = Abeam(X1,X2)
    #element stiffness matrix
    k = kbeam(X1,X2,Ge)
    #calc local nodeforcevector
    re = A.dot(k).dot(Ve)
    #opstil belastningsvektor efter lokale retninger
    if dLe[0] == 1:
        p = dLe[1]*L/2
        m = dLe[1]*L**2/12
        r = np.transpose(array([[0,p,m,0,p,-m]]))
    elif dLe[0] == 0:
        p = dLe[1]*L/2
        r = np.transpose(array([[p,0,0,p,0,0]]))
    else:
        r = np.transpose(array([[0,0,0,0,0,0]]))
    re = re-r
    f1 = array([-re[0],re[3]])
    f2 = array([re[1],-re[4]])
    m  = array([-re[2],re[5]])
    return f1,f2,m

def FEM_frame():
    #Initiation data from GH
    a = 3      # [m]
    bP = 1e4    # [N]
    dP = 1e4    # [N/m]
    E = 2.1e11 # [N/m2]
    A = 1e-3   # [m2]
    I = 2e-6   # [m4]
    
    X=array([[0,0],[0,a],[a,a],[a,0]])
    nno=len(X)
    
    T=array([[0,1],[1,2],[2,3]])
    #nel=len(T)
    
    D = array([[0,1,2,3,4,5],[3,4,5,6,7,8],[6,7,12,9,10,11]])
    #nd=np.max(D)
    
    G= array([[E,A,I],[E,A,I],[E,A,I]])
    
    U=array([0,1,2,9,10,11])
    
    bL=[]
    bL.append([3,bP])
    bL=array(bL)
    
    dL = np.zeros((len(T),2));
    dL[1]=[1,-dP]
    
    Vskala = 2
    Sskala = 0.3e-4
    
    #Program
    
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
        if dLe[1]!=0:
            X1 = X[T[el][0]]
            X2 = X[T[el][1]]
            r=rbeam(X1,X2,dLe)
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
    print("Displacements:")
    print(V)
    print("Reaction forces:")
    print(Ru)
    
    #Plot displacement
    #Calculate forces
    F1=np.zeros((len(T),2))
    F2=np.zeros((len(T),2))
    M=np.zeros((len(T),2))
    for el in range(len(T)):
        X1 = X[T[el][0]]
        X2 = X[T[el][1]]
        de=D[el]
        f1,f2,m=forceCalc(X1,X2,G[el],V[de],dL[el])
        F1[el]=np.transpose(f1)
        F2[el]=np.transpose(f2)
        M[el]=np.transpose(m)
    
    print("Normalforces:")
    print(F1)
    print("Shearforces:")
    print(F2)
    print("Moment:")
    print(M)    
    return 0

FEM_frame()
    