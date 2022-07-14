import pandas as pd
import os
import time as t
import urllib.request
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import math

##################################################################
#Bus companies are paid per mile they drive if the bus has a student with special needs on it
#Looked to see distances that bus companies traveled to see if any routes were excessively long
# and which companies 

########################### UTILITY ##############################
def findUpperDir(string,levels=1):
    for i in range(levels):
        string = os.path.dirname(string)

    return string
##################################################################

ROUTEDATA = "Attachment C. Routes + Schools.xlsx"
#ROUTEDATA = "testdata.xlsx"
CHROMEDRIVER = "chromedriver.exe"


#################################################################
def read_data(filename):
    path = findUpperDir(__file__) + "\\" + filename
    df = pd.read_excel(path)
    listDf = df.values.tolist()

    return listDf

#removes numbers from a string
def removeNums(string):
    for i in range(10):
        string = string.replace(str(i),"")
    
    return string

#Takes data and isolates school names on each route
def isolateSchools(busData):
    #loops through all rows and creates a list as the third entry in each row, consisting of the schools on each route
    for row in busData:
        row[2] = removeNums(row[2]).split("/")
        for i in range(len(row[2])):
            row[2][i] = row[2][i].strip()

    return busData

#Creates a dictionary of school names and corresponding addresses
def createSchoolDict():
    schoolData = read_data("CPS_School_Locations_SY1516.xlsx")
    schoolDict = {}
    manualData = read_data("unmatchedSchools.xlsx")

    #Can add zipcode to address if needed ****
    for school in schoolData:
        address = school[3]+", Chicago, IL"
        schoolDict[school[0]] = address

    for school in manualData:
        address = school[1]
        schoolDict[school[0]] = address

    return schoolDict

#views how many schools are in the school Dictionary and returns list of unmatched schools
def matchSchools(uniqueSchools, schoolDict):
    keys = list(schoolDict.keys())
    matches = 0
    unmatchedSchools = []
    for i in range(len(keys)):
        keys[i] = keys[i].lower()
    for school in uniqueSchools:
        if school.lower() in keys:
            matches += 1
        else:
            unmatchedSchools.append(school)
    
    return [matches,unmatchedSchools]

#Webcrawler that finds addresses for schools on google
def addressWebcrawler(schoolname):
    newSchoolname = schoolname.replace(" ","+")
    url = "https://google.com/search?q="+newSchoolname+"+Chicago+School+Zipcode"

    # Perform the request
    request = urllib.request.Request(url)

    # Set a normal User Agent header, otherwise Google will block the request.
    request.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36')
    raw_response = urllib.request.urlopen(request).read()

    # Read the repsonse as a utf-8 string
    html = raw_response.decode("utf-8")
    string = "<span class=\"LrzXr\">"

    if string in html:
        #captures the address that is located between the specified HTML tags
        location = html.split(string)[1].split("</span>")[0]

        address = location[:(len(location)-5)]
        
        return address

    else:
        return "NOT FOUND"

#finds address of any schools that were not included in official CPS dataset
def findUnmatchedAddress(unmatchedSchoolList):
    schools = []
    addresses = []
    total = len(unmatchedSchoolList)
    count = 0

    for school in unmatchedSchoolList:
        address = addressWebcrawler(school)
        schools.append(school)
        addresses.append(address)
        count = count + 1
        print(f"On {count} out of {total} ({100 * count/total}%)")

    d = {"Schools":schools,"Addresses":addresses}
    df = pd.DataFrame(data = d)
    df.to_excel("output.xlsx",index=False)

#find distances in a route by using distance calculator website
def findDistances(busData,schoolDict):
    done = 0
    total = len(busData)

    #Calculates distance for each route
    for route in busData:
        tripDistance = 0
        tripTime = 0
        validAddress = True   
        routeList = []

        if len(route[2]) > 1:
            for i in range(1,len(route[2])):
                if validAddress:
                    firstAddress = schoolDict[route[2][i-1]]
                    secondAddress = schoolDict[route[2][i]]

                    #catches invalid address on first two addresses
                    if(firstAddress == "NOT FOUND" or secondAddress == "NOT FOUND"):
                        validAddress = False
                        routeList = ["No valid Address found for stop(s)"]
                    else:
                        #try except catches errors on third+ addresses
                        try:
                            #calculates distance and time between two stops and adds to total route
                            segment = calculateDistanceance(firstAddress,secondAddress)
                            distance = segment[0]
                            time = segment[1]
                            tripDistance += distance                        
                            tripTime += time

                            routeList.append(distance)
                            routeList.append(time)
                        except:
                            routeList = ["ERROR: FIX MANUALLY"]
                            validAddress = False

        #catches if only one school is in the route                        
        else:
            routeList = ["No Route"]
            validAddress = False

        #inserts total distance and time if a route exists
        if(validAddress):
            routeList.insert(0,tripDistance)
            routeList.insert(1,tripTime)

        #Appends the number of stops on a route
        route.append(len(route[2]))

        #appends route statistics to end 
        route.extend(routeList)

        routeString = ""

        #replaces list in third entry with string
        for i in range(len(route[2])):
            routeString += route[2][i] + " / "
        route[2] = routeString[:len(routeString)-3]

        done += 1
        print(f"{done} out of {total} routes calculated ({round(100*done/total,4)}%)")

    return busData

#calculates distance and time between two addresses
def calculateDistance(address1, address2):
    address1 = address1.replace(" ","%20")
    address2 = address2.replace(" ","%20")

    url = f"https://distancecalculator.globefeed.com/US_Distance_Result.asp?vr=apes&fromplace={address1}&toplace={address2}"


    # initiating the webdriver. Parameter includes the path of the webdriver.
    myPath = CHROMEDRIVER

    #Declares Options to remove print messages to console
    options = Options()
    options.headless = True
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    #sets driver object
    driver = webdriver.Chrome(options=options)

    #Gets the Url
    driver.get(url)

    # ensures page is loaded 
    t.sleep(8)

    html = driver.page_source

    if "drvDistance" in html:
        DistanceStr = isolateDistance(html)
        TimeStr = isolateTime(html)
        

    else:
        print("Location Not Found")

    driver.close()

    return (DistanceStr,TimeStr)

#isolates the distance string from page source code
def isolateDistance(html):
    string = html.split("drvDistance")[1].split("</span>")[0].split(">")[1]

    #replaces miles suffix and convert to number
    string = string.replace(" mi","")
    miles = float(string)

    return miles

#isolates the distance string from page source code
def isolateTime(html):
    string = html.split("drvDuration")[1]
    string = string.split("</span>")[0]
    string = string.split(">")[1]

    string = string.replace("minutes","").strip()
    if "hours" in string:
        hours = int(string.split("hours")[0].strip())
        minutes = int(string.split("hours")[1].strip())

        minutes += hours * 60  
    else:
        minutes = int(string)

    return minutes

def main():
    #reads data in
    busData = read_data(ROUTEDATA)
    
    #extracts route information and address information
    busData = isolateSchools(busData)
    schoolDict = createSchoolDict()   
    
    #calculates route distance and times
    busData = findDistances(busData, schoolDict)

    #columns for writing to excel
    columns = ["BUS COMPANY",
    "ROUTE ID",
    "ROUTE SCHOOLS",
    "# OF SCHOOLS",
    "TOTAL TRIP DISTANCE(MILES)",
    "TOTAL TRIP DISTANCE(MINUTES)",
    "PATH 1 DISTANCE",
    "PATH 1 TIME",
    "PATH 2 DISTANCE",
    "PATH 2 TIME",
    "PATH 3 DISTANCE",
    "PATH 3 TIME",
    "PATH 4 DISTANCE",
    "PATH 4 TIME",
    "PATH 5 DISTANCE",
    "PATH 5 TIME",
    "PATH 6 DISTANCE",
    "PATH 6 TIME"]

    #ensures data is rectangular so it can be written to excel
    for route in busData:
        checked = False
        while not checked:
            if(len(route) < len(columns)):
                route.append("")
            else:
                checked = True

    df = pd.DataFrame(busData,columns = columns)

    df.to_excel("RouteStatistics.xlsx",index=False)

main()
