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

    return boxStr


def enboxList(stringList, terminalWidth, leftPadding = 1, rightPadding = 1, leftMargin = 0, rightMargin = 0):
    boxWidth = terminalWidth - (leftMargin + rightMargin)
    textBoxWidth = boxWidth - (leftPadding + rightPadding)

    s = []

    boxStr = "+"
    for i in range(boxWidth-2):
        boxStr += "-"
    boxStr += "+"
    s.append(boxStr)
    boxStr = ""

    for item in stringList:
        if(item != None):
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