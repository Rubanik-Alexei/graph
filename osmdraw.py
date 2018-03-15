import bs4
import os
import io
import sys
import svgwrite
import csv
import math as m

mult=float(sys.argv[2])


def adjsort(adjlist):
    return int(adjlist.get('node'))

def spherical2decart(shPoint,radius):
	decPoint = []
	decPoint.append(radius*m.cos(shPoint[0])*m.sin(shPoint[1]))
	decPoint.append(radius*m.sin(shPoint[0])*m.sin(shPoint[1]))
	return decPoint

dwg = svgwrite.Drawing('graph.svg', profile='tiny')
map_file = sys.argv[1]

soup=bs4.BeautifulSoup(io.open(map_file,encoding='utf-8'),'xml')
ways=soup.findAll('way')
nodes=soup.findAll('node')
highways={}
nodesCor={}
for node in nodes:
	nodesCor[node.attrs['id']]=[node.attrs['lon'],node.attrs['lat']]


f = open('adjacencyList.csv', 'w', newline='', encoding='utf-8')
adjacencyList = []
listWriter = csv.DictWriter(f, fieldnames=['node', 'adj'])


v=['motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified', 'residential', 'service', 'road']
for way in ways:
	counter = 0
	tag = way.find('tag',k='highway',v=v)
	if tag!=None:
		nd=way.findAll('nd')
		ref=[]
		for n in nd:
			if counter == len(nd)-1:
				adjacencyList.append({'node': n.attrs["ref"], 'adj': [int(nd[counter-1].attrs["ref"])]})
			else:
				if counter == 0:
					adjacencyList.append({'node': n.attrs["ref"], 'adj': [int(nd[counter+1].attrs["ref"])]})
				else:
					adjacencyList.append({'node': n.attrs["ref"], 'adj': [int(nd[counter - 1].attrs["ref"]), int(nd[counter + 1].attrs["ref"])]})
			ref.append(n.attrs['ref'])
		highways[way.attrs['id']]=ref

maxPoint=[0,0]
minPoint=[90,180]

for nodeKeys in nodesCor.keys():
	if maxPoint[0]<float(nodesCor[nodeKeys][0]):
		maxPoint[0]=float(nodesCor[nodeKeys][0])
	if maxPoint[1]<float(nodesCor[nodeKeys][1]):
		maxPoint[1]=float(nodesCor[nodeKeys][1])
	if minPoint[0]>float(nodesCor[nodeKeys][0]):
		minPoint[0]=float(nodesCor[nodeKeys][0])
	if minPoint[1]>float(nodesCor[nodeKeys][1]):
		minPoint[1]=float(nodesCor[nodeKeys][1])
print(minPoint,maxPoint)

for key in highways.keys():
	begPoint=[0,0]
	for refKey in highways[key]:
		if begPoint==[0,0]:
			begPoint=[int((float(nodesCor[refKey][0])-minPoint[0])*mult),int((maxPoint[1]-float(nodesCor[refKey][1]))*mult)]
			dwg.add(dwg.circle(center=(begPoint[0], begPoint[1]), r=1, stroke='red'))
		else:
			endPoint=[int((float(nodesCor[refKey][0])-minPoint[0])*mult),int((maxPoint[1]-float(nodesCor[refKey][1]))*mult)]
			dwg.add(dwg.circle(center=(endPoint[0], endPoint[1]), r=1, stroke='red'))
			dwg.add(dwg.line((begPoint[0], begPoint[1]), (endPoint[0], endPoint[1]), stroke='black'))
			print(begPoint,endPoint,maxPoint)
			begPoint=endPoint

dpoint=[(maxPoint[0]-minPoint[0]),maxPoint[1]-minPoint[1]]

adjacencyList.sort(key=adjsort)
adjlf=[]
adjlf.append(adjacencyList[0])

for i in range(1, len(adjacencyList)):
	if int(adjacencyList[i].get('node')) != int(adjlf[len(adjlf)-1].get('node')):
		adjlf.append(adjacencyList[i])
	else:
		adj = adjlf[len(adjlf)-1].get('adj') + adjacencyList[i].get('adj')
		dnode = adjlf[len(adjlf)-1].get('node')
		adjlf.pop()
		adjlf.append({'node': dnode, 'adj': adj})


for node in adjlf:
	listWriter.writerow({'node': node.get('node'), 'adj': node.get('adj')})

f.close()
dwg.viewbox(0, 0, int((maxPoint[0]-minPoint[0])*mult), int((maxPoint[1]-minPoint[1])*mult))
dwg.save()



