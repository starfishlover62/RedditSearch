import constants
import math

def formatAge(age):
    # time constants

    try:
        age + 1
    except TypeError:
        return f"{age}"

    ticker = 0

    if(age > constants.YEAR):
        while(age > constants.YEAR):
            age -= constants.YEAR
            ticker += 1
        return f"{ticker} year(s)"
    elif(age > constants.MONTH):
        while(age > constants.MONTH):
            age -= constants.MONTH
            ticker += 1
        return f"{ticker} month(s)"
    elif(age > constants.DAY):
        while(age > constants.DAY):
            age -= constants.DAY
            ticker += 1
        return f"{ticker} day(s)"
    elif(age > constants.HOUR):
        while(age > constants.HOUR):
            age -= constants.HOUR
            ticker += 1
        return f"{ticker} hour(s)"
    elif(age > constants.MINUTE):
        while(age > constants.MINUTE):
            age -= constants.MINUTE
            ticker += 1
        return f"{ticker} minute(s)"
    else:
        return "just now"
    

# Places string at location start, and fills with spaces until it is size length
def placeString(string,length,start = 0):
    if(len(string)>=length):
        return string
    s = ""
    s = s.zfill(length)
    s = s.replace("0"," ")
    s = s[:start] + string + s[start+len(string):]
    return s

def combineStrings(stringA,stringB,length,startA,startB):
    if(startB < startA):
        return combineStrings(stringB,stringA,length,startB,startA)
    stringA = placeString(stringA,length,startA)
    string = stringA[:startB] + stringB + stringA[startB+len(stringB):]
    return string

    
def spacesString(spaces):
    st = ""
    for i in range(spaces):
        st += " "
    return st

def tabulate(string, terminalWidth = 80, spaces = 8):
    # Removes new lines and tabs from the original string
    string = string.replace("\t","")
    string = string.replace("\n","")

    # Creates a string with a number of spaces equal to spaces
    addString = spacesString(spaces)
    ogString = addString

    offset = terminalWidth - (spaces)
    for i in range(math.ceil(len(string)/offset)):
        if(addString != ogString): # Adds a new line and spaces to every line after the first
            addString += "\n" 
            addString += spacesString(spaces)
        nonSpaceFound = False
        for j in range(offset):
            try:
                if(not nonSpaceFound):
                    if(string[j + offset*i] != " "): # Checks character to see if it is something other than a space
                        nonSpaceFound = True
                if(nonSpaceFound):
                    addString += string[j + offset*i] # Adds the characters to the string to be returned
            except IndexError:
                break
    
    # index = 0
    # nextSpace = 0
    # charactersInLine = 0
    # while(index < len(string)):
    #     if((charactersInLine + (nextSpace - index)) > terminalWidth):



    return addString



def enbox(stringList, terminalWidth, leftPadding = 1, rightPadding = 1, leftMargin = 0, rightMargin = 0):
    boxWidth = terminalWidth - (leftMargin + rightMargin)
    textBoxWidth = boxWidth - (leftPadding + rightPadding)

    s = []

    # Creates the top border of the box
    boxStr = "+"
    for i in range(boxWidth-2):
        boxStr += "-"
    boxStr += "+"
    s.append(boxStr)
    boxStr = ""

    for item in stringList:
        if(item != None):
            # Creates a separating line in the box
            if(item == "%separator%"):
                boxStr += "+"
                for i in range(boxWidth-2):
                    boxStr += "-"
                boxStr += "+"
                s.append(boxStr)
                boxStr = ""
            else:
                tempStr = tabulate(item,textBoxWidth,leftPadding+1)
                listStrings = tempStr.splitlines()
                # print(listStrings)
                for line in listStrings:
                    line = "|" + line[1:]
                    if(len(line) < boxWidth - 1):
                        line += spacesString((boxWidth-len(line)-1))
                    line += "|"
                    s.append(line)

    
    boxStr += "+"
    for i in range(boxWidth-2):
        boxStr += "-"
    boxStr += "+"
    s.append(boxStr)
    boxStr = ""

    return s