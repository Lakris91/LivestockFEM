from math import sqrt
import numpy as np
array=np.array

def transMat(X1,X2):
    # Calculate transformation matrix A
    n = X2-X1                      # directionvector
    L = sqrt(n @ n)             # elementllength
    n = n/L                        # unitvector
    # Define transformationsmatrix
    A = array([ [n[0],  n[1],   0,  0,      0,      0],
                [-n[1],  n[0],   0,  0,      0,      0],
                [0,     0,      1,  0,      0,      0],
                [0,     0,      0,  n[0],   n[1],   0],
                [0,     0,      0,  -n[1],   n[0],   0],
                [0,     0,      0,  0,      0,      1]])
    return A,L

def eleStiff(X1,X2,G):
    # Define element stiffness matrix
    # make transformationsmatrix
    A,L = transMat(X1,X2)
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
    k = np.transpose(A) @ k @ A
    return k

def eleLoad(X1,X2,dLe,ret):
    #Opstil elementlastvektor
    #dan transformationsmatrix
    A,L = transMat(X1,X2)
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

    r = np.transpose(A) @ r
    return r

def forceCalc(X1,X2,Ge,Ve,dLe,ret):
    #Calculate internal forces in an element
    #f1: normalforce
    #f2: shearforce
    #m:  moment
    #transformation matrix A
    A,L = transMat(X1,X2)
    #element stiffness matrix
    k = eleStiff(X1,X2,Ge)
    #opstil belastningsvektor efter lokale retninger
    if ret == 1:
        #calc local nodeforcevector
        Ve1=Ve
        Ve1[0]=0
        Ve1[3]=0
        re = A @ k @ Ve1
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
        re = A @ k @ Ve2
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
