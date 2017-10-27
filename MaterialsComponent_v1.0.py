
if not (len(Emodul)==0 or len(SecArea)==0 or len(Inertia)==0):
    #Repeat last element in list to get equal list lenght
    maxlen = max(len(Emodul),len(SecArea),len(Inertia))
    SecArea.extend([SecArea[-1]]*(maxlen-len(SecArea)))
    Emodul.extend([Emodul[-1]]*(maxlen-len(Emodul)))
    Inertia.extend([Inertia[-1]]*(maxlen-len(Inertia)))
    
    
    MatLabText=""
    materials=[]
    for i in range(len(Emodul)):
        mate="G("+str(i+1)+",:)=["+str(Emodul[i])+" "+str(SecArea[i])+" "+str(Inertia[i])+"];"
        materials.append("E-module="+str(Emodul[i])+" Area="+str(SecArea[i])+" Inertia="+str(Inertia[i]))
        MatLabText=MatLabText+mate+"\n"
else:
    print "Zero length lists do NOT work"