import rhinoscriptsyntax as rs
LEN=LoadElementNo
MatLabElementLoad="dL = zeros(nel,2);\n"
if not (len(LEN)==0 or len(Direction)==0 or len(NPerM)==0 or len(ElePlanes)==0 or len(Global)==0):
    #Repeat last element of shortest list
    eleLen = len(LEN)
    Direction.extend([Direction[-1]]*(eleLen-len(Direction)))
    NPerM.extend([NPerM[-1]]*(eleLen-len(NPerM)))
    Global.extend([Global[-1]]*(eleLen-len(Global)))
    Direction=Direction[:eleLen]
    NPerM=NPerM[:eleLen]
    Global=Global[:eleLen]
    vecX=[]
    vecY=[]
    vecOri=[]
    for i,dir in enumerate(Direction):
        #Unitize 2D vector
        vec=rs.VectorUnitize([dir[0],dir[1],0])
        if Global[i]:
            line=rs.AddLine((0,0,0),vec)
            #vec=rs.XformCPlaneToWorld((0,0,0),ElePlanes[LEN[i]])
            vpt=rs.XformWorldToCPlane(vec,ElePlanes[LEN[i]])
            opt=rs.XformWorldToCPlane((0,0,0),ElePlanes[LEN[i]])
            #print rs.EvaluatePlane(ElePlanes[LEN[i]],[0,0])
            vec=rs.VectorCreate(vpt,opt)
        print vec
        MLx="dL("+str(LEN[i]+1)+",:)=[1 "+str(vec[0]*NPerM[i])+"];\n"
        MLy="dL("+str(LEN[i]+1)+",:)=[2 "+str(vec[1]*NPerM[i])+"];\n"
        MatLabElementLoad=MatLabElementLoad+MLx+MLy