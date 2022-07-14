import os
import sys
import pandas as pd
from random import randint 
import numpy as np
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

####################################################################################################


#Main Function
#First: Read data from excel sheet into list
#Second: creates a dictionary of origin schools as keys
# and list of destination schools as values
#Third: Draw the plot using pycircos
def main():
    enrollmentData = read_data("[2019] Redacted Enrollment List")
    (originDict,transferDict) = createDict(enrollmentData)

    checkInternalTransfers(originDict,transferDict)

    drawPlot(originDict,transferDict)

#returns number of unique school destinations
def findUnique(data):
    uniqueSchools = []
    for row in data:
        if row[1] not in uniqueSchools:
            uniqueSchools.append(row[1])
        if row[3] not in uniqueSchools:
            uniqueSchools.append(row[3])

    return len(uniqueSchools)

#reads data from dataset file and filters out any schools not belonging to specified school district
def read_data(filename):
    path = DATASETS+f"{filename}.xlsx"
    enrollmentDf = pd.read_excel(path)
    dataList = enrollmentDf.values.tolist()
    enrollmentData = []
    for row in dataList:
        if row[2] == SCHOOLDISTRICT:
            enrollmentData.append(row)

    return enrollmentData

#Creates a dictionary of origins and transfers 
def createDict(enrollmentData):  

    originDict = {} 
    transferDict = {}

    for row in enrollmentData: 
        originKeys = originDict.keys() 
        transferKeys = transferDict.keys() 
        originSchool = row[1]
        transferSchool = row[3]

        #checks to see if origin school and transfer school in each row are in keys
        if originSchool in originKeys: 
            originList = originDict[originSchool]
            transferExist = False 
            for transfer in originList:  
                if transfer[0] == transferSchool:
                    transfer[1] = transfer[1] + 1 
                    transferExist = True 
            if transferExist == False: 
                originList.append([transferSchool,1])
                originDict[originSchool] = originList 

        #Creates dictionary entry linked to a list of school transferred to and the number 
        else: 
            originDict[originSchool] = [[transferSchool,1]]

        # Creates similar dictionary with transfer schools
        if transferSchool in transferKeys: 
            transferList = transferDict[transferSchool]
            originExist = False 

            for origin in transferList:  
                if origin[0] == originSchool:
                    origin[1] = origin[1] + 1 
                    originExist = True 

            if originExist == False: 
                transferList.append([originSchool,1])
                transferDict[transferSchool] = transferList 

        else: 
            transferDict[transferSchool] = [[originSchool,1]]

    return (originDict,transferDict)
 
#creates plot of the chord Diagrams   
def drawPlot(originDict,transferDict):
    chordPlot = Gcircle()
    (originNodeList, transferNodeList) = createNodes(originDict, transferDict)
    chordPlot = drawChords(originNodeList, transferNodeList, chordPlot)

#Logic to create nodesize
def createNodes(originDict, transferDict): 
    originNodeList = []
    transferNodeList = []

    #Creates list of nodes being transferred from
    for originKey in originDict.keys():
        nodeWidth = 0
        for chord in originDict[originKey]: 
            nodeWidth += chord[1]

        originNodeList.append([originKey,nodeWidth])

    #Creates list of nodes being transferred to and adds size of individual chords
    for transferKey in transferDict.keys():
        nodeWidth = 0
        for transferChord in transferDict[transferKey]: 
            nodeWidth += transferChord[1]
            
        transferNodeList.append([transferKey,nodeWidth])

    return (originNodeList,transferNodeList)

#Draws chords onto established nodes
def drawChords(originNodeList, transferNodeList, chordPlot):
    ispace = np.pi/360
    for nodeList in [originNodeList,transferNodeList]:
        for node in nodeList:
            chordColor = randColor()
            chordPlot.add_locus(node[0],node[1],900,100,chordColor, chordColor, None, ispace, True)

    chordPlot.set_locus()
    return chordPlot

#  creates random color (RGB)
def randColor():
    colorString = 'ABCDEF0123456789'
    color = "#"
    for i in range(6):
        color += colorString[randint(0,15)]

    return color

#Function to view transfers within a single zipcode
def checkInternalTransfers(originDict,transferDict):
    transferKeys = list(transferDict.keys())
    originKeys = list(originDict.keys())
    dataList = []
    
    for key in originKeys:
        transfersOut = findTotal(originDict[key])
        if key not in transferKeys:
            transfersIn = 0
        else:
            transfersIn = findTotal(transferDict[key])
        
        netTransfers = transfersOut-transfersIn

        #Labels schools as net exporters/importers
        if(netTransfers > 0):
            value = "Exporter"
        else:
            value = "Importer"
        
        dataList.append([key,transfersOut,transfersIn,netTransfers,value])
        

    df = pd.DataFrame(columns = ["School","Outgoing","Incoming","Net","Exporter/Importer"],data = dataList)
    df.to_excel(ANALYSIS + "commonImports.xlsx",index=False)

#finds total number of transfers from or to a school
def findTotal(transferList):
    total = 0
    for row in transferList:
        total += row[1] 
    
    return total
    
#creates unique list
def removeDuplicates(keyList):
    newKeyList = []
    for key in keyList:
        if key not in newKeyList:
            newKeyList.append(key)
    
    return newKeyList

main()
