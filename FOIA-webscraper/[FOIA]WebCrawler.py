import requests
import pandas as pd
import time
import os

####################################### GLOBAL CONSTANTS #############################################################
BASEURL = "https://cps.mycusthelp.com/webapp/_rs/(S(xsqtvcgoedb042oyzh1mctqm))/RequestArchiveDetails.aspx?rid="
OUTFILE = "[FOIA]FOIA Requests"
STARTSTRING = "<p style=\"font-weight: 400; max-width: 75%; font-size: 0.875rem\" tabindex=\"0\">"
ENDSTRING = "</p>"

####################################### FUNCTION DEFINITIONS #########################################################
#Gets user input, finds data on the CPS public archive, and saves details to the incomplete file 

def main():
    #asks the user which rows of the datasheet they'd like to start and end on
    rowList = getRows()

    #Gets preexisting data and then appends details onto it
    data = read_data()
    detailedData = scrapeWeb(data,rowList)

    writeToExcel(detailedData)


#Reads the data of the Excel Sheet using the pandas library and inserts it into a list
def read_data():
    filename = os.path.dirname(os.path.realpath(__file__))+f"\{OUTFILE}"

    #Reads the data in the Excel Sheet as a pandas DataFrame
    df = pd.read_excel(filename + ".xlsx")
    newDf = df.to_numpy()

    #Transforms the dataframe into a 2 dimensional list
    dataList = []
    for i in range(0,len(newDf)):
        rowList=[]
        for p in range(len(newDf[0])):
            rowList.append(newDf[i][p])

        dataList.append(rowList)

    return dataList


#Navigates the CPS Public Archive of FOIA requests to find necessary data
def scrapeWeb(data,rows):
    failList = []
    for row in rows:

        #Progress tracker
        count = row - rows[0]
        percentage = round((100 * count/(len(rows))),2)
        print(f"Currently on {(count)} out of {len(rows)} ({percentage}%)")

        requestString = data[row][0]
        
        #Isolates unique request number that is in the URL
        #Sample request string: N009683-061021
        #Unique request number: 009683

        # Removes letter from the beginning of the string,
        # splits the string by the dash,
        # then only retains the first half

        requestNumber = requestString[1:].split("-")[0]
        URL = BASEURL + requestNumber
    
        page = establishConnection(URL)

        #Retrieves the HTML source code of the page and searches
        newPage = page.text


        stringList = newPage.split(STARTSTRING)
        
        #isolates data in the table
        for p in range(1,6):
            try:                
                newString = isolateEntries(stringList[p], ENDSTRING)

                #Handles overflow case
                if len(data[row]) < 9:
                    data[row].append(newString)
                else:
                    data[row][p+3] = newString
                    
            except IndexError:
                print("Failed  on row " + str(row+2) + ". Program continuing...")
                failList.append(row+2)
                break

        #Saves progress periodically
        if row % 50 == 0:
            writeToExcel(data)
            print("Progress Saved.")

    #displays rows failed during runtime
    if len(failList) != 0:
        print("Failed on rows: ")
        for failedRow in failList:
            print(failedRow)
        
    return data

#Writes the data to Excel
def writeToExcel(dataList):
    
    df = pd.DataFrame(dataList,columns=['Request Number','Create Date','Summary','Request Status','Date Received','Name of Requester','Record Description','Status','Date Complete'])
    #Specifies the filename
    df.to_excel(os.path.dirname(os.path.realpath(__file__))+f"\{OUTFILE}.xlsx", index=False)

#Attempts to connect and retries every 60 seconds if it fails
def establishConnection(URL):
    worked = False
    while not worked:
        try:
            page = requests.get(URL)
            worked = True
        except:
            #If the program is shut out of the connection by the host, the program waits a minute before trying
            print("Encountered an error. Waiting a minute before resuming")

            time.sleep(60)

            #Notifies the user that the program is ready to resume and tries the request again
            print("Done Waiting")

    return page

#Isolates entries from table
def isolateEntries(rawString, delimiter):
    subStringList = rawString.split(delimiter)

    if len(subStringList) != 1:
        return subStringList[0]
    else:
        print("Error isolating entries")

#Menu function for input on the start and end rows
def getRows():
    start = input("What row would you like to begin your request at?: ")
    end = input("What row would you like to end your request at?: ")

    start = int(start)-2
    end = int(end) - 1

    rowList = []
    for i in range(start, end):
        rowList.append(i)

    return rowList

# Searches for missing entries in the datasheet
def checkRows(dataList):
    failList = []
    for i in range(len(dataList)):
        wasFailed = 0
        for p in range(5):
            if str(dataList[i][4+p])== "nan":
                wasFailed += 1
        if wasFailed > 4:
            failList.append(i+2)

    return failList


#displays rows that have failed for manual searching (fails less than 0.3% of the time)
def failedRows():
    dataList = read_data()
    failList = checkRows(dataList)
    print(f"A total of {len(failList)} requests failed:")
    string = "Row "
    for i in range(len(failList)):
        string += f"{failList[i]}, "
    print(string)

######################################################################################################################

#failedRows()
main()

