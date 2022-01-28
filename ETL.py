#!/usr/bin/python3
import csv
import string
import pandas as pd
import re as r
import os
import glob
import time
import datetime

#FUNZIONI

#aggiunge header ad ogni partizione csv
def primariga(nome):
	os.system("sed -i '1i DeviceId,ArrivalTime,DepartureTime,DurationSeconds,StreetMarker,Sign,Area,StreetId,StreetName,BetweenStreet1,BetweenStreet2,Side Of Street,In Violation,Vehicle Present' "+str(nome))

#patizionamento csv iniziale
def partiziona():
	os.system("split -d -l 100000 file.csv part")

#controllo del secondo parametro di 'Sign'
def checkparametro(x):
	prova=['MTR','30M','15M','TKT']
	k=data_frame[x].str.split(" ")
	for i in k:
		if (i[1] not in prova):
			i[1]="1  1"
	data_frame[x]=k.str.join(" ")

#contatore di parole in colonna x salvato in colonna tmp
def contaparole(x):
	data_frame["tmp"]=data_frame[x].str.split(" ").str.len()

#sostituzione in stringa di vecchio con nuovo
def CambioSingolo(colum,vecchio,nuovo):
	for i in vecchio:
		data_frame[colum]=data_frame[colum].str.replace(i, nuovo)

#funzione di normalizzazione codice cartello Sign
def LZnormalizzate(colum):
	LZ=["METER","LZ M","LZ M30","LZ  30 M" "LZ M 30","LZ M15", "LZ M 15","LZ 15 M"]
	LZ1=["MTR","LZ 30M","LZ 30M","LZ 30M","LZ 30M","LZ 15M","LZ 15M","LZ 15M"]
	for i in range(len(LZ)):
		data_frame[colum]=data_frame[colum].str.replace(LZ[i], LZ1[i])

#funzione di normalizzazione ore parcheggio
def PNormalizate(colum):
	P1=["P 1 ","1 P ","P1 "]
	P2=["P 2 ","2 P ","P2 "]
	P3=["P 3 ","3 P ","P3 "]
	P4=["P 4 ","4 P ","P4 "]
	P5=["P 5 ","5 P ","P5 "]
	P6=["P 6 ","6 P ","P6 "]
	P7=["P 7 ","7 P ","P7 "]
	P8=["P 8 ","8 P ","P8 "]
	P9=["P 9 ","9 P ","P9 "]
	P10=["P 10 ","10 P ","P10 "]
	P11=["P 1/2","1/2 P","P1/2"]
	P12=["P 1/4","1/4 P","P1/4"]
	P13=["P 3/4","3/4 P","P3/4"]
	P14=["P /","P/","/p"]
	PX=[P1,P2,P3,P4,P5,P6,P7,P8,P9,P10,P11,P12,P13,P14]
	PXS=["1P ","2P ","3P ","4P ","5P ","6P ","7P ","8P ","9P ","10P ","1/2P","1/4P","3/4P"," "]
	for i in range(len(PX)):
		CambioSingolo(colum,PX[i],PXS[i])

#funzione per gestione orario 24h
def post(i):
	return i+12
	
#funzione di normalizzazione ora Sign
def Ore(colum):
	data_frame[colum]=data_frame[colum].str.replace("MIDNIGHT","00:00")
	data_frame[colum]=data_frame[colum].str.replace(".",":")
	data_frame[colum]=data_frame[colum].str.replace(" TO ","-")
	data_frame[colum]=data_frame[colum].str.replace(" TO","-")
	data_frame[colum]=data_frame[colum].str.replace("TO ","-")
	lista=["00","15","30","45"]
	for i in range(24):
		for j in lista:
			data_frame[colum]=data_frame[colum].str.replace(" "+str(i)+"AM"," "+str(i)+":00")
			data_frame[colum]=data_frame[colum].str.replace("-"+str(i)+":"+j+"PM","-"+str(post(i))+":"+j)
			data_frame[colum]=data_frame[colum].str.replace(str(i)+":"+j+"PM",str(post(i))+":"+j)
			data_frame[colum]=data_frame[colum].str.replace(" "+str(i)+"PM"," "+str(post(i))+":00") 
			data_frame[colum]=data_frame[colum].str.replace("-"+str(i)+"PM","-"+str(post(i))+":00")          
			data_frame[colum]=data_frame[colum].str.replace(str(i)+":"+j+"AM",str(i)+":"+j)
			data_frame[colum]=data_frame[colum].str.replace(" "+str(i)+":"+j," "+str(i)+":"+j)
			
	#toglie gli spazi del trattino
	for i in range(10):
		for j in range(10):
			data_frame[colum]=data_frame[colum].str.replace(str(i)+" - "+str(j),str(i)+"-"+str(j))
			data_frame[colum]=data_frame[colum].str.replace(str(i)+" -"+str(j),str(i)+"-"+str(j))
			data_frame[colum]=data_frame[colum].str.replace(str(i)+"- "+str(j),str(i)+"-"+str(j))

   
	
#funzione di normalizzazione giorni Sign
def Giorni(colum):
	gNonNormalizzato=[" M-"," M -"," MON -","-F ","- F ","- SU ","-SU ","-S ","- S ","-SA ","- SA ","MF"]
	gNormalizzato=[" MON-"," MON-"," MON-","-FRI ","-FRI ","-SUN ","-SUN ","-SUN ","-SUN ","-SAT ","-SAT ","MON-FRI"]
	for i in range(len(gNonNormalizzato)):
		data_frame[colum]=data_frame[colum].str.replace(gNonNormalizzato[i], gNormalizzato[i])



#funzione di normalizzazione colonna sign che richiama funzioni
def NormalizzazioneSign (colum):
	PNormalizate(colum)
	LZnormalizzate(colum)
	Giorni(colum)
	Ore(colum)
	checkparametro(colum) 
	contaparole(colum)



##INIZIO SCRIPT
partiziona()

#conto le partizioni create
nproc=(glob.glob("part*"))

#apertura file output csv
file_path2='file2.csv'

#apertura file output testo e numero eliminizioni
file_path3='out.txt'

	
testo = open(file_path3,"a")

lenCsvI=0
lenCsvF=0

t1=time.time()

#per ogni partizione effettuo normalizzazione e pulizia
for i in range(len(nproc)):

	if (str(nproc[i])!="part00"):
		primariga(str(nproc[i]))
	
	print(str(nproc[i]))
	file_path=nproc[i]
	
	#inizializza partizione corrente
	data_frame = pd.read_csv(file_path)

	#Dimensione csv iniziale 
	DimCsv=len(data_frame)
	lenCsvI=lenCsvI+DimCsv
	DimTmp=DimCsv

	#Numeri record eliminati
	elemElem=DimCsv-DimTmp
	testo.write("DATI CSV INIZIALI\n")
	testo.write("Dim : "+str(DimTmp)+" Eliminate : "+str(elemElem))

	#colonne da eliminare e modificare in maiuscolo
	column_namedrop = ['DeviceId','DepartureTime','StreetId','BetweenStreet1','BetweenStreet2','Vehicle Present','Side Of Street']
	column_nameupper=['StreetMarker','Sign','Area','StreetName']

	#eliminazione colonne
	for i in column_namedrop:
		data_frame = data_frame.drop(i, axis = 1)


	#eliminazione righe con attributo vuoto 
	data_frame.dropna(how="any", inplace=True)

	#Dimensione csv attuale
	DimCsv2=len(data_frame)
	#Numeri record eliminati
	elemElem=DimTmp-DimCsv2
	testo.write("\nEliminazione attributi vuoti\n")
	testo.write("Dim : "+str(DimCsv2)+" Eliminate : "+str(elemElem))
	DimTmp=DimCsv2

	#controllo solo data solo nel 2014
	data_frame = data_frame[pd.to_datetime(data_frame['ArrivalTime']).dt.year==2014]

	 
	DimCsv2=len(data_frame)
	#Numeri record eliminati
	elemElem=DimTmp-DimCsv2
	testo.write("\nEliminazione istanza con anno != 2014\n")
	testo.write("Dim : "+str(DimCsv2)+" Eliminate : "+str(elemElem))
	DimTmp=DimCsv2

	#controllo del tempo maggiore di 0
	data_frame = data_frame[data_frame["DurationSeconds"]>0]

	#Dimensione csv attuale
	DimCsv2=len(data_frame)
	#Numeri record eliminati
	elemElem=DimTmp-DimCsv2
	testo.write("\nEliminazione istanze DurationSeconds < 0 \n")
	testo.write("Dim : "+str(DimCsv2)+" Eliminate : "+str(elemElem))
	DimTmp=DimCsv2

	#Rinominazione tabella e controllo valori solo booleani
	data_frame.rename(columns={'In Violation':'InViolation'}, inplace=True)
	data_frame.query("InViolation == 'False' or InViolation == 'True'")

	#Dimensione csv attuale 
	DimCsv2=len(data_frame)
	#Numeri record eliminati
	elemElem=DimTmp-DimCsv2
	testo.write("\nEliminazione istanze booleane errate  \n")
	testo.write("Dim : "+str(DimCsv2)+" Eliminate : "+str(elemElem))
	DimTmp=DimCsv2

	#normalizzazione in maiuscolo
	for i in column_nameupper:
		data_frame[i]=data_frame[i].str.upper()

	#normalizzo colonna sign 
	NormalizzazioneSign('Sign')

	#se tmp ha più di 4 elem si elimina record
	data_frame=data_frame[data_frame["tmp"]==4]
	data_frame=data_frame.drop("tmp", axis = 1) 

	#Dimensione csv attuale 
	DimCsv2=len(data_frame)
	#Numeri record eliminati
	elemElem=DimTmp-DimCsv2
	testo.write("\nEliminazione post normalizzazione sign \n")
	testo.write("Dim : "+str(DimCsv2)+" Eliminate : "+str(elemElem))
	DimTmp=DimCsv2

	#Dimensione csv finale
	DimCsv2=len(data_frame)
	elemElem=DimCsv-DimCsv2
	lenCsvF=lenCsvF+DimCsv2
	testo.write("\nDATI CSV Finali \n")
	testo.write("Dim : "+str(DimCsv2)+" Eliminate : "+str(elemElem))
	testo.write("\n ______________________\n\n")

	#scrive su file csv nuovo
	try:
		l = open(file_path2)
		#fai quello che vuoi
		data_frame.to_csv(file_path2,mode='a', header=False, index = False)
	except (IOError, OSError):
		#il file non esiste, oppure non hai i permessi sufficienti
		data_frame.to_csv(file_path2, index = False)
		pass

	#pulizia dataframe attuale
	colonne=['ArrivalTime','DurationSeconds','StreetMarker','Sign','Area','StreetName','InViolation']
	for i in colonne:
		data_frame = data_frame.drop(i, axis = 1)

	os.system("rm "+str(file_path))

#Tempo impiegato
t2=time.gmtime(time.time()-t1)
testo.write("\n Dim CSV iniziale : "+str(lenCsvI)+"\n Dim CSV Finale : "+str(lenCsvF)+"\n tempo impiegato :"+str(time.strftime("%H:%M:%S", t2)))
print("\n Dim CSV iniziale : "+str(lenCsvI)+"\n Dim CSV Finale : "+str(lenCsvF)+"\n tempo impiegato :"+str(time.strftime("%H:%M:%S", t2)))