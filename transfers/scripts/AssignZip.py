import urllib.request
import pandas as pd
from ordered_set import OrderedSet


#reads data in
def read_data(filename):
    df = pd.read_excel("datasets/"+filename + ".xlsx")
    newDf = df.values.tolist()

    return newDf

#gets unique list of data 
def getAllUnique(data,index):

    uniqueList = []
    for i in range(len(data)):
        uniqueList.append(str(data[i][index]))

    #conversion of list to ordered set and back to list removes repeated entries
    uniqueSet = OrderedSet(uniqueList)
    uniqueList = list(uniqueSet)

    return uniqueList

#webscraper function
def findZipcode(schoolname):
    newSchoolname = schoolname.replace(" ","+")
    url = f"https://google.com/search?q={newSchoolname}+Chicago+School+Zipcode"

    # Perform the request
    request = urllib.request.Request(url)

    # Sets normal User Agent header, otherwise Google will block the request.
    request.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36')
    raw_response = urllib.request.urlopen(request).read()

    # Read the repsonse as a utf-8 string
    html = raw_response.decode("utf-8")

    #html tag containing address
    string = "<span class=\"LrzXr\">"

    #checks if address string is in html source code and 
    if string in html:
    
        address = html.split(string)[1].split("</span>")[0]
        zipcode = address[(len(address)-5):]

        return zipcode

    else:
        return "NOT FOUND"

#searches school list for any schools that are not already in the provided dataset to search for corresponding areacodes
def findAreaList(zipDict, schoolList):
    count = 0
    for school in schoolList:
        if school not in zipDict.keys():
            print("Currently on {school}: {count} Completed")
            zipDict[school] = findZipcode(school)
            count += 1
            
    return zipDict

#Creates column of zipcode for easy writing to excel
def createColumns(areaCodeDict,dataList):
    columnList = []
    
    for i in range(len(dataList)):
        zipcode = areaCodeDict.get(dataList[i][9])
        columnList.append(zipcode)

    return columnList

#Writes data to excel sheet
def writeToExcel(columnList,filename):
    df = pd.read_excel("datasets/"+filename + ".xlsx")
    df.insert(0, "Zipcode", columnList, True)

    df.to_excel("datasets/doneZips.xlsx", index=False)

#Reads zipcodes from CPS provided FOIA request to avoid unnecessary searches and improve accuracy
def readZip():
    df = pd.read_csv("datasets/CPS_School_Locations_SY1516.csv")
    newDf = df.values.tolist()
    zipDict = {}
    for i in newDf:
        zipDict[i[0]] = i[4]
    
    return zipDict
   
def main():
    filename = "testZips"
    print("Reading Data...")
    dataList = read_data(filename)

    print("Creating Zipcode Dictionary...")
    zipDict = readZip()
    print(zipDict)

    print("Creating school list")
    schoolList = getAllUnique(dataList, 9)

    print("Revising zipcode Dictionary...")
    areaCodeDict = findAreaList(zipDict, schoolList)

    print("Writing to Excel")
    zipcodeColumn = createColumns(areaCodeDict,dataList)
    writeToExcel(zipcodeColumn,filename)

main()


