import numpy as np
import sys
import pandas as pd

mylines = []
p_number = []
lineList = []
with open ('.../header.txt', 'rt') as myfile:
	for myline in myfile:
		start = myline.find('packet_num')
		end = myline.find(')',start)
		p = (myline[start:end])
		if p.rstrip():
			v = p.split()
			data = int(v[2])
			lineList.append(data)
MissedPacket = (max(lineList) - len(lineList))/max(lineList)   

print('Number of rececived packet :', len(lineList))
print('Highest packet number :', max(lineList))
print('PER :', MissedPacket)