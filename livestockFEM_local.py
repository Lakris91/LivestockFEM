from math import sqrt
import numpy as np

# Calculate transformation matrix A
def transMat(X1,X2):
    n = X2-X1
    L = sqrt(n @ n)
    n = n/L
    A = np.array([ [n[0],  n[1], 0,  0,     0,      0],
                [-n[1], n[0], 0,  0,     0,      0],
                [0,     0,    1,  0,     0,      0],
                [0,     0,    0,  n[0],  n[1],   0],
                [0,     0,    0,  -n[1], n[0],   0],
                [0,     0,    0,  0,     0,      1]])
    return A,L,n

# Define element stiffness matrix
def eleStiff(X1,X2,G):
    A,L,n = transMat(X1,X2)
    EA = G[0]*G[1]
    EI = G[0]*G[2]
    kl = np.array([[EA/L, 0,           0,        -EA/L, 0,          0         ],
                  [ 0,    12*EI/L**3,  6*EI/L**2, 0,   -12*EI/L**3, 6*EI/L**2 ],
                  [ 0,    6*EI/L**2,   4*EI/L,    0,   -6*EI/L**2,  2*EI/L    ],
                  [-EA/L, 0,           0,         EA/L, 0,          0         ],
                  [ 0,   -12*EI/L**3, -6*EI/L**2, 0,    12*EI/L**3,-6*EI/L**2 ],
                  [ 0,    6*EI/L**2,   2*EI/L,    0,   -6*EI/L**2,  4*EI/L    ]])
    k = A.T @ kl @ A
    return k, kl

# Define element load vector
def eleLoad(X1,X2,dLe):
    A,L,n = transMat(X1,X2)
    p1 = dLe[0]*L/2
    p2 = dLe[1]*L/2
    m = dLe[1]*L**2/12
    fl = np.array([[p1,p2,m,p1,p2,-m]]).T
    f = A.T @ fl
    return f, fl

# Calculate internal forces in an element
def forceCalc(X1,X2,Ge,Ve,dLe):
    A,L,n = transMat(X1,X2)
    k,kl = eleStiff(X1,X2,Ge)
    vl = A @ Ve
    re = kl @ vl
    f,fl = eleLoad(X1,X2,dLe)
    re = re-fl
    f1 = np.array([-re[0],re[3]]).T
    f2 = np.array([re[1],-re[4]]).T
    m  = np.array([-re[2],re[5]]).T
    return f1,f2,m

# Generate data for plotting forces in an element
def forcePlot(X1,X2,Se,dLe,nrp,sscale,s):
    A,L,n = transMat(X1,X2)
    F01 = np.array([-n[1],n[0]])*Se[0]*sscale
    F02 = np.array([-n[1],n[0]])*Se[1]*sscale
    Xp = np.array([X1[0],X1[0]+F01[0],X2[0]+F02[0],X2[0]])
    Yp = np.array([X1[1],X1[1]+F01[1],X2[1]+F02[1],X2[1]])
    if s == 3:
        M = np.array([Se[0],Se[1]])
        for i in range(1,nrp+1):
            x = (i/(nrp+1))*L
            mx = (1/2)*dLe[1]*x*(L-x)
            m1 = np.array([-n[1],n[0]])*mx*sscale
            Xp = np.insert(Xp,i+1,Xp[1]+i*(Xp[-2]-Xp[1])/(nrp+1)-m1[0])
            Yp = np.insert(Yp,i+1,Yp[1]+i*(Yp[-2]-Yp[1])/(nrp+1)-m1[1])
            M =  np.insert(M,i,M[0]+i*(M[-1]-M[0])/(nrp+1)+mx)
        return Xp,Yp,M
    else:
        return Xp,Yp

# Generate data for plotting deformations in an element
def deformationPlot(X1,X2,v,div,vscale):
    defPlot=[]
    defVal=[]
    A,L,n = transMat(X1,X2)
    Au=A[0:2,0:2]
    for i in range(div):
        xL=(i)/(div-1)
        N2 = 1 - 3*xL**2 + 2*xL**3
        N3 = L*(xL - 2*xL**2 + xL**3)
        N5 = 3*xL**2 - 2*xL**3
        N6 = L*(-xL**2 + xL**3)
        N=np.array([[1-xL, 0,  0,  xL, 0,  0 ],
                    [0   , N2, N3, 0,  N5, N6]])
        vl = A @ v
        ul = N @ vl
        u = (ul.T @ Au)
        Xe=X1.T*(1-xL)+X2.T*xL
        Xu=(Xe+u*vscale)
        defPlot.append(np.append(Xu,0).tolist())
        defVal.append(np.append(u,np.linalg.norm(u)).tolist())
    defVal=(np.array(defVal).T).tolist()
    return defPlot,defVal
