"""Define the materials of the system 
    Inputs:
        ElementIndex: Index of the element to define material for
        E: Elastic modulus of the element in Newton per m2
        SectionArea: Section area in m2
        Inertia: Moment of inertia in m4
    Output:
        MatLabMaterial: MatLab string for defining the materials
        Materials: Materials per element"""

__author__ = "LasseKristensen"

if not (len(E)==0 or len(SectionArea)==0 or len(Inertia)==0 or len(ElementIndex)==0):
    #Repeat last element in list to get equal list lenght
    maxlen = len(ElementIndex)
    SectionArea.extend([SectionArea[-1]]*(maxlen-len(SectionArea)))
    E.extend([E[-1]]*(maxlen-len(E)))
    Inertia.extend([Inertia[-1]]*(maxlen-len(Inertia)))
    SectionArea=SectionArea[:maxlen]
    E=E[:maxlen]
    Inertia=Inertia[:maxlen]
    
    MatLabMaterial=""
    Materials=[]
    for i in range(maxlen):
        mate="G("+str(ElementIndex[i]+1)+",:)=["+str(E[i])+" "+str(SectionArea[i])+" "+str(Inertia[i])+"];"
        Materials.append("E-module="+str(E[i])+" Area="+str(SectionArea[i])+" Inertia="+str(Inertia[i]))
        MatLabMaterial=MatLabMaterial+mate+"\n"
