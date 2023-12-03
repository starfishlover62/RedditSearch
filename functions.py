import datetime
from datetime import timezone
import math
import pyperclip

def currentTimestamp():
    return datetime.datetime.now(timezone.utc).replace(tzinfo=timezone.utc).timestamp()



def formatAge(age):
    # time constants
    SECONDS_PER_MINUTE = 60
    SECONDS_PER_HOUR = 3600 # 3,600
    SECONDS_PER_DAY = 86400 # 86,400
    SECONDS_PER_MONTH = 2592000 # 2,592,000  (30 days in a month)
    SECONDS_PER_YEAR = 31536000 # 31,536,000
    try:
        age + 1
    except TypeError:
        return f"{age}"
    
    formattedAge = ""

    ticker = 0

    if(age > SECONDS_PER_YEAR):
        while(age > SECONDS_PER_YEAR):
            age -= SECONDS_PER_YEAR
            ticker += 1
        return f"{ticker} year(s)"
    elif(age > SECONDS_PER_MONTH):
        while(age > SECONDS_PER_MONTH):
            age -= SECONDS_PER_MONTH
            ticker += 1
        return f"{ticker} month(s)"
    elif(age > SECONDS_PER_DAY):
        while(age > SECONDS_PER_DAY):
            age -= SECONDS_PER_DAY
            ticker += 1
        return f"{ticker} day(s)"
    elif(age > SECONDS_PER_HOUR):
        while(age > SECONDS_PER_HOUR):
            age -= SECONDS_PER_HOUR
            ticker += 1
        return f"{ticker} hour(s)"
    elif(age > SECONDS_PER_MINUTE):
        while(age > SECONDS_PER_MINUTE):
            age -= SECONDS_PER_MINUTE
            ticker += 1
        return f"{ticker} minute(s)"
    else:
        return "just now"
    
def spacesString(spaces):
    st = ""
    for i in range(spaces):
        st += " "
    return st

def tabulate(string, terminalWidth = 80, spaces = 8):
    string = string.replace("\t","")
    string = string.replace("\n","")
    addString = spacesString(spaces)
    ogString = addString

    offset = terminalWidth - (spaces)
    for i in range(math.ceil(len(string)/offset)):
        if(addString != ogString):
            addString += "\n" 
            addString += spacesString(spaces)
        nonSpaceFound = False
        for j in range(offset):
            try:
                if(not nonSpaceFound):
                    if(string[j + offset*i] != " "):
                        nonSpaceFound = True
                if(nonSpaceFound):
                    addString += string[j + offset*i]
            except IndexError:
                break

    return addString


def enbox(stringList, terminalWidth, leftPadding = 1, rightPadding = 1, leftMargin = 0, rightMargin = 0):
    boxWidth = terminalWidth - (leftMargin + rightMargin)
    textBoxWidth = boxWidth - (leftPadding + rightPadding)

    boxStr = "+"
    for i in range(boxWidth-2):
        boxStr += "-"
    boxStr += "+\n"

    for item in stringList:
        if(item != None):
            if(item == "%separator%"):
                boxStr += "+"
                for i in range(boxWidth-2):
                    boxStr += "-"
                boxStr += "+\n"
            else:
                tempStr = tabulate(item,textBoxWidth,leftPadding+1)
                listStrings = tempStr.splitlines()
                # print(listStrings)
                for line in listStrings:
                    line = "|" + line[1:]
                    if(len(line) < boxWidth - 1):
                        line += spacesString((boxWidth-len(line)-1))
                    line += "|\n"
                    boxStr += line

    if(boxStr[-1] != "\n" ):
        boxStr += "\n"
    
    boxStr += "+"
    for i in range(boxWidth-2):
        boxStr += "-"
    boxStr += "+"

    print(boxStr)


def copyToClipboard(string):
    pyperclip.copy(string)

def getInput(prompt, lowerBound, upperBound, numAttempts = -1):
    if(lowerBound < 0  or upperBound < 0):
        return -1
    attempts = 0
    if(numAttempts <= 0):
        attempts = numAttempts - 1
    while(attempts < numAttempts):
        try:
            value = int(input(f"{prompt}\n"))
        except ValueError:
            attempts += 1
            continue
        return value
    return -1

