
if not (len(Emodul)==0 or len(SecArea)==0 or len(Inertia)==0 or len(ElementNo)==0):
    #Repeat last element in list to get equal list lenght
    maxlen = len(ElementNo)
    SecArea.extend([SecArea[-1]]*(maxlen-len(SecArea)))
    Emodul.extend([Emodul[-1]]*(maxlen-len(Emodul)))
    Inertia.extend([Inertia[-1]]*(maxlen-len(Inertia)))
    SecArea=SecArea[:maxlen]
    Emodul=Emodul[:maxlen]
    Inertia=Inertia[:maxlen]
    
    MatLabMaterial=""
    materials=[]
    for i in range(maxlen):
        mate="G("+str(ElementNo[i]+1)+",:)=["+str(Emodul[i])+" "+str(SecArea[i])+" "+str(Inertia[i])+"];"
        materials.append("E-module="+str(Emodul[i])+" Area="+str(SecArea[i])+" Inertia="+str(Inertia[i]))
        MatLabMaterial=MatLabMaterial+mate+"\n"
else:
    print "Zero length lists do NOT work"