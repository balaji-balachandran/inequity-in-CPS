import pandas as pd
from ordered_set import OrderedSet
from datetime import datetime
from styleframe import StyleFrame
from math import trunc
from os import path

################################################################################################
# 10/12/21
# For use in addressing the Chicago Board of Education on possible grade acceleration for students in high performing students in disadvantaged schools
# Examines how a change in policy would affect distribution of students eligible for grade acceleration

################################################################################################
#reads data of the data sheet
def read_data(year, season):

    filename = path.dirname(path.realpath(__file__)) + f"\datasets\{year}\FOIA_REQ_NWEA_{year}{season}"

    df = pd.read_excel(filename + ".xlsx")
    return df.values.tolist()

#finds list of unique schools
def getAllSchools(data):

    schoolIDList = []
    schoolNameList = []

    #populates lists
    for i in range(len(data)):
        schoolIDList.append(data[i][1])
        schoolNameList.append(data[i][2])

    #conversion to ordered set and then to list produces a unique list
    schoolSet = OrderedSet(schoolIDList)
    schoolIDList = list(schoolSet)

    schoolNameSet = OrderedSet(schoolNameList)
    schoolNameList = list(schoolNameSet)

    schoolList = []
    
    #returns school ID list
    for i in range(len(schoolIDList)):
        schoolList.append([schoolIDList[i],schoolNameList[i]])

    return schoolList

#seperates data into lists by school
def seperateSchool(data):
    #acquires list of unique schools
    schoolList = getAllSchools(data)
    school = 0
    rowList = []

    #sorts data by school
    for i in range(len(data)):
        if(schoolList[school][0] == data[i][1]): 
            rowList.append(data[i])
            
        else:
            schoolList[school].append(rowList)
            school+=1
            rowList = []
            rowList.append(data[i])

    schoolList[school].append(rowList)
    
    return schoolList

#seperates data into lists by grade
def seperateGrade(sortedList):
    for school in range(len(sortedList)):
        gradeList=[[],[],[],[],[],[],[],[],[]]
        for i in range(len(sortedList[school][2])):
            if(sortedList[school][2][i][4]== "K"):
                gradeList[0].append(sortedList[school][2][i])
            else:
                for p in range(1,9):
                    if(sortedList[school][2][i][4]== str(p)):
                        gradeList[p].append(sortedList[school][2][i])

        sortedList[school][2]=gradeList

    return sortedList

#seperates data into seperate data by subject
def seperateSubject(sortedList):

    for school in range(len(sortedList)):

        for grade in range(len(sortedList[school][2])):
            subjectList=[[],[]]

            for i in range(len(sortedList[school][2][grade])):

                if(sortedList[school][2][grade][i][5]== "Mathematics"):
                    subjectList[0].append(sortedList[school][2][grade][i])

                elif(sortedList[school][2][grade][i][5]== "Reading"):
                    subjectList[1].append(sortedList[school][2][grade][i])        

            sortedList[school][2][grade]=subjectList

    return sortedList

# Writes data to an excel file
def writeToExcel(finalMatrix, year):
    dfList = []
    for i in range(len(finalMatrix)):
        matrix = []
        
        #columns for excel sheet
        col = ['School',
                   'Grade',
                   'Subject',
                   '# of Students in the Grade',
                   'Mean Score of Students in the Grade',
                   '90th Percentile Score of Grade Above',
                   '50th Percentile Score of 2 Grades Above',
                   '90th Percentile Score of 2 Grades Above',
                   '# of Students Scoring Above 90% 1 Grade Higher',
                   '# of Students Scoring Above 50% 2 Grades Higher',
                   '# of Students Scoring above 90% 2 Grades Higher',
                   '95th Percentile Score Nationally',
                   '# of Students Scoring above 95% Nationally']

        #inserts entry of matrix into 2d Matrix for writing to an excel sheet
        for a in range(len(finalMatrix[i])):
            for b in range(len(finalMatrix[i][a])):
                matrix.append(finalMatrix[i][a][b])

            matrix.append([])
            matrix.append(col)

        #Creates dataframe of the new matrix
        df = pd.DataFrame (matrix, columns = ['School',
                                              'Grade',
                                              'Subject',
                                              '# of Students in the Grade',
                                              'Mean Score of Students in the Grade',
                                              '90th Percentile Score of Grade Above',
                                              '50th Percentile Score of 2 Grades Above',
                                              '90th Percentile Score of 2 Grades Above',
                                              '# of Students Scoring Above 90% 1 Grade Higher',
                                              '# of Students Scoring Above 50% 2 Grades Higher',
                                              '# of Students Scoring above 90% 2 Grades Higher',
                                              '95th Percentile Score Nationally',
                                              '# of Students Scoring above 95% Nationally'])
        df = StyleFrame(df)
        dfList.append(df)

    #creates filename
    time = datetime.today().strftime('%Y-%m-%d')
    filename = "analyzedData/Analysis- HighPerformingStudentsof"+year+"- "+time+".xlsx"

    #Writes using styleframe library to excel sheet
    with StyleFrame.ExcelWriter(filename) as writer:  
        dfList[0].to_excel(writer, sheet_name='Fall', index = False)
        dfList[1].to_excel(writer, sheet_name='Winter', index = False)
        dfList[2].to_excel(writer, sheet_name='Spring', index = False)
    
    
#Calculates Statistics for number of students scoring at or above the 90th percentiles
def calculateStatistics(sortedList, a, b, c, nationalList,season):
    matrix = []
    gradeAboveList = []
    gradeTwoAboveList = []
    dataList = []
    
    bypass = False
    row = 0
    #nationalList has indices [x][y][z] where:
    #x = subject (0 for reading, 1 for math)
    #y = season (0 for fall, 1 for winter, 2 for spring)
    #z = grade (0 for K, 1 for 1st, ..., 8 for 8th)
    
    
    #a = school
    #b = grade
    #c = subject

    #alternating x for both reading and math
    x = (c+1)%2

    nat90percentile = nationalList[x][season][b]

    
    # Create header for table
    for i in range(len(sortedList[a][2][b][c])):
        dataList.append(sortedList[a][2][b][c][i][7])

    if(sortedList[a][2][b][c] == []):
        matrix.append(sortedList[a][1])

        for grade in range(9):
            if grade == b:
                if grade == 0:
                    grade = "K"
                else:
                    grade = int(grade)
                matrix.append(grade)
        if(c == 1):
            matrix.append("Reading")
        else:
            matrix.append("Mathematics")
            
    else:
        matrix.append(sortedList[a][2][b][c][0][2])
        matrix.append(sortedList[a][2][b][c][0][4])
        matrix.append(sortedList[a][2][b][c][0][5])
    

    #handles edge case of 7th and 8th graders with insufficient data
    if b<8:
        for i in range(len(sortedList[a][2][b+1][c])):
            gradeAboveList.append(sortedList[a][2][b+1][c][i][7])
   
    if b < 7:
        for i in range(len(sortedList[a][2][b+2][c])):
            gradeTwoAboveList.append(sortedList[a][2][b+2][c][i][7])

    else:
        bypass = True

    #handles empty dataset
    if dataList == []:
        matrix.append("N/A")
        matrix.append("N/A")
    else:
        matrix.append(len(dataList))
        matrix.append(trunc(sum(dataList)/len(dataList))+1)

    #If there is no entries in the grade above, the table has insufficient information so is left mostly empty
    if gradeAboveList == []:
        matrix.append("N/A")
        matrix.append("N/A")
        matrix.append("N/A")
        matrix.append("N/A")
        matrix.append("N/A")
        matrix.append("N/A")
        if dataList ==[]:
            matrix.append(nat90percentile)
            matrix.append("N/A")
        else:
            matrix.append(nat90percentile)
            matrix.append(countOccurrences(dataList, nat90percentile))
    
    #Handles case when two grade above list is empty 
    elif gradeTwoAboveList == []:
        if gradeAboveList == []:
            matrix.append("N/A")
        else:
            index90 = trunc(9*len(gradeAboveList)/10)
            percentile90 = sorted(gradeAboveList)[index90]

            matrix.append(percentile90)
            matrix.append("N/A")
            matrix.append("N/A")
                  
            matrix.append(countOccurrences(dataList, percentile90))
            matrix.append("N/A")
            matrix.append("N/A")

            if dataList ==[]:
                matrix.append(nat90percentile)
                matrix.append("N/A")
            else:
                matrix.append(nat90percentile)
                matrix.append(countOccurrences(dataList, nat90percentile))


    else:
        if not bypass:
            if b < 7:
                index90 = (trunc(9*len(gradeAboveList)/10))
                percentile90 = sorted(gradeAboveList)[index90]
                matrix.append(percentile90)

                mean = trunc(sum(gradeTwoAboveList)/len(gradeTwoAboveList))+1
                matrix.append(mean)

                index90Two = (trunc(9*len(gradeTwoAboveList)/10))
                percentile90Two = sorted(gradeTwoAboveList)[index90Two]
                matrix.append(percentile90Two)
                
                matrix.append(countOccurrences(dataList, percentile90))
                matrix.append(countOccurrences(dataList, mean))
                matrix.append(countOccurrences(dataList, percentile90Two))

                if dataList ==[]:
                    matrix.append(nat90percentile)
                    matrix.append("N/A")
                else:
                    matrix.append(nat90percentile)
                    matrix.append(countOccurrences(dataList, nat90percentile))

        else:
            #handles 7th grade case of no gradetwo above
            if b == 7:
                index90 = trunc(9*len(gradeAboveList)/10)
                percentile90 = sorted(gradeAboveList)[index90]

                matrix.append(percentile90)

                matrix.append("N/A")

                matrix.append("N/A")
                          
                matrix.append(countOccurrences(dataList, percentile90))

                matrix.append("N/A")

                matrix.append("N/A")

                if dataList ==[]:
                    matrix.append(nat90percentile)
                    matrix.append("N/A")
                else:
                    matrix.append(nat90percentile)
                    matrix.append(countOccurrences(dataList, nat90percentile))


            else:
                matrix.append("N/A")
                matrix.append("N/A")
                matrix.append("N/A")
                matrix.append("N/A")
                matrix.append("N/A")
                matrix.append("N/A")

                if dataList ==[]:
                    matrix.append(nat90percentile)
                    matrix.append("N/A")
                else:
                    matrix.append(nat90percentile)
                    matrix.append(countOccurrences(dataList, nat90percentile))


    return matrix

#return count of how many elements in a list are greater than a number
def countOccurrences(dataList, num):
    counter = 0
    for i in range(len(dataList)):
        if(dataList[i]>num):            #Could change to >= if needed
            counter += 1

    return counter

#Creates large table containing statistics on percentile of students scoring at varying thresholds
def runStatistics(sortedList,year, season):
    matrix = []
    nationalList = readNationalAverage()
    for schools in range(len(sortedList)):
        schoolMatrix = []
        for i in range(len(sortedList[schools][2])):
            for k in range(len(sortedList[schools][2][i])):
                schoolMatrix.append(calculateStatistics(sortedList, schools, i, k, nationalList, season))

        matrix.append(schoolMatrix)

    return matrix

#Determines national average for each grade level and subject
#Produces three dimensional matrix that can be indexed based on grade, season, and subject
def readNationalAverage():
    year = "2015"
    df = pd.read_excel(f"{path.dirname(path.realpath(__file__))}\datasets\{year} NWEA MAP Student Norms 95 percentile RIT scores 211022.xlsx")
    
    newDf = df.values.tolist()
    subjectList = []
    seasonList = []
    gradeList = []

    subjectList = []

    #Note: Heavily dependent on format of excel sheet
    for b in range(2):
        
        columnHeight = 5
        verticalOffset = 2

        x = columnHeight * b + verticalOffset
        seasonList = []

        for p in range(3):
            row = x + p
            gradeList = []

            for i in range(9):
                gradeList.append(newDf[row][i+1])
            seasonList.append(gradeList)
        subjectList.append(seasonList)
    
    return subjectList

#Runs statistical analyses on the data and then writes to an Excel sheet
def generateGraphs(sortedList, year):
    writeMatrix = []
    for i in range(3):
        finalMatrix = runStatistics(sortedList[i],year, i)
        writeMatrix.append(finalMatrix)


    writeToExcel(writeMatrix, year)

#produces statistics for each year of available data
def yearStats(year):
    mainList = []
    for season in ["Fall", "Winter", "Spring"]:
        print(f"Working on {year} {season}")
    
        data = read_data(year, season)
        print("Data inserted into lists")

        # seperates data by school
        sortedList = seperateSchool(data)
        print("List sorted by school")

        # seperates data by grade
        sortedList = seperateGrade(sortedList)
        print("List sorted by Grade")
        
        #seperates data by subject
        sortedList = seperateSubject(sortedList)
        print("List sorted by Subject \n")

        mainList.append(sortedList)

    generateGraphs(mainList, year)
    print("Done with analysis of "+year)

#Loops through a list of years to generate a complete analysis
def main():
    yearList = ["2017", "2018", "2019", "2020"]
    for year in yearList:
        yearStats(year)

main()
