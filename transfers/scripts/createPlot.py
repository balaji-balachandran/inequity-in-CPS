import sys
import os
import numpy as np
import pandas as pd
import requests
from random import *
from ordered_set import OrderedSet
path = os.path.dirname(os.path.dirname(__file__)) + "\\resources"
sys.path.append(path)
from pycircos import *

# Program that uses data of transfers of all Illinois students to identify rates of transfers between certain zipcodes
# within the Chicago Public School District, looking to see if any schools are exploiting CPS policies regarding
# student attendance and school funding

####################################################################################################
#Utility function to find the folder name n levels above current
def findUpperDir(string,levels = 1):
    for i in range(levels):
        string = os.path.dirname(string)

    return string

###################################### GLOBAL VARIABLES ############################################

SCHOOLDISTRICT = "City of Chicago SD 299"
DATASETS = findUpperDir(__file__,2) + "\\datasets\\"
ANALYSIS = findUpperDir(__file__,2) + "\\analysis\\"
WITHDRAWLIST = [31, 32, 33, 34, 35, 40]
WITHDRAWINDEX = 2

####################################################################################################


def read_data(filename):
    df = pd.read_excel(DATASETS + filename + ".xlsx")
    newDf = df.values.tolist()

    return newDf

# gets unique list of data
def getAllUnique(data,index):

    uniqueList = []
    for i in range(len(data)):
        uniqueList.append(data[i][index])

    uniqueSet = OrderedSet(uniqueList)
    uniqueList = list(uniqueSet)

    return uniqueList

#seperates raw data into categories of transfers (e.g Jones Prep to Ace Tech)
def populateList(dataList):
    transferList = []
    for i in dataList:
        #verifies if school zip is known
        if str(i[10]) == "nan" or str(i[10])=="NOT FOUND":        
            transferList.append(str(i[0])+":"+"Unknown School")
        else:
            transferList.append(f"{i[0]}:{i[10]}")

    #removes repeated categories
    transferSet = OrderedSet(transferList)
    uniqueTransferList = list(transferSet)

    #creates "nodes" (sectors along chord diagram)
    node = []
    for i in uniqueTransferList:
        counter = 0
        for p in range(len(transferList)):
            if i == transferList[p]:
                counter += 1
        node.append([str(i), counter])

    #Creates intermediary list 
    newList = []
    for i in node:
        newList.append(i[0][0:5])
        newList.append(i[0][6:])

    uniqueSet = OrderedSet(newList)
    uniqueList = list(uniqueSet)
    
    # dictates size of nodes
    nodeSizeList = []
    for i in uniqueList:
        counter = 0
        
        #counts origin and destination for node Size
        for p in transferList:
            if p[0:5] == i:
                counter += 1
            if p[6:] == i:
                counter+= 1
                
        nodeSizeList.append([i,counter])

    return [node,nodeSizeList]

#plots nodes on the chord diagram
def createPlot(nodeList):
    chordPlot = Gcircle()
    chordColorList = []
    
    #space in between nodes is set to 0.5 degrees
    ispace = np.pi/360
    colorDict = {}

    for node in nodeList:
        chordColor = randColor()
        colorDict[node[0]] = chordColor
        chordPlot.add_locus(node[0],node[1],900,100,chordColor, chordColor, None, ispace, True)

    #sets nodes in place
    chordPlot.set_locus()

    return [chordPlot,colorDict]

# draws chords onto chord diagram
def createChords(plotList,chordList,nodeDict):
    chordPlot = plotList[0]
    chordColors = plotList[1]

    # initializes nodeDict to 0
    for i in nodeDict.keys():
        nodeDict[i] = 0

    for i in range(len(chordList)):
        startNode = chordList[i][0][0:5]
        endNode = chordList[i][0][6:]

        amount = chordList[i][1]

        color = chordColors[endNode]

        start1 = nodeDict[startNode]
        start2 = nodeDict[endNode]

        
        drawChord(chordPlot,startNode,endNode,amount,start1,start2,color)
        
        # sets new start and endpoints for future nodes
        nodeDict[startNode] = nodeDict[startNode]+amount-1
        nodeDict[endNode] = nodeDict[endNode]+amount-1

    # saves Chordplot and completes chord diagram
    chordPlot.save("chordplot")

def drawChord(chordPlot,startNode,endNode,amount,start1,start2,pigment):
    chordPlot.chord_plot([startNode, start1, start1+amount-1, 900], [endNode, start2, start2+amount-1, 900], color =pigment)

    return [startNode,"Index start is from "+str(start1)+"-"+str(start1+amount)+": Index end is from "+str(start2)+"-"+str(start2+amount)]
    
def randColor():
    colorString = 'ABCDEF0123456789'
    color = "#"
    for i in range(6):
        color += colorString[randint(0,15)]

    return color

    
def main():
    newDataList = read_data("transferDatawithZipcodes")
    
    #Creates chord Diagram for every withdrawal Code
    for WITHDRAWALCODE in WITHDRAWLIST:
        dataList = []
        #Discards if zipcode is not found, and then filters by withdrawal Code
        for i in newDataList:
            # or str(i[10]) == "nan" or i[10] == "NOT FOUND"
            if str(i[0])=="NOT FOUND" or str(i[10]) == "nan" or i[10] == "NOT FOUND":
                continue
            else:
                if i[6] == WITHDRAWALCODE:
                    dataList.append(i)


        zipCodeList = getAllUnique(dataList, 0)

        NodeAndChordList = populateList(dataList)

        chordList = NodeAndChordList[0]
        nodeList = NodeAndChordList[1]

        nodeDict = {}
        for i in nodeList:
            nodeDict[i[0]] = i[1]

        plotList = createPlot(nodeList)

        createChords(plotList,chordList,nodeDict)

        print(f"Completed Withdrawal Code {WITHDRAWALCODE}")

    
main()

