import constants
import math

def removeNonAscii(text):
    newString = ""
    for char in text:
        if(ord(char) <= 255):
            newString = newString + char
    return newString

def formatAge(age, suffix=""):
    """
    Takes a time (age) in seconds, and returns a string that describes it with the largest unit that
    is smaller than the time. ex: age = 119, returns 'one minute', age = 95000, returns 'one day.'
    Suffix is used to append some phrase after the unit, such as 'ago.' The suffix is not applied to the
    just now unit (ages less than 60 seconds)
    """

    try:
        age + 1
    except TypeError:
        return f"{age}"

    ticker = 0

    if(age > constants.YEAR):       # Years
        while(age > constants.YEAR):
            age -= constants.YEAR
            ticker += 1
        if(ticker > 1):
            return f"{ticker} years {suffix}"
        else:
            return f"{ticker} year {suffix}"
        
    elif(age > constants.MONTH):    # Months
        while(age > constants.MONTH):
            age -= constants.MONTH
            ticker += 1
        if(ticker > 1):
            return f"{ticker} months {suffix}"
        else:
            return f"{ticker} month {suffix}"
        
    elif(age > constants.DAY):      # Days
        while(age > constants.DAY):
            age -= constants.DAY
            ticker += 1
        if(ticker > 1):
            return f"{ticker} days {suffix}"
        else:
            return f"{ticker} day {suffix}"
        
    elif(age > constants.HOUR):     # Hours
        while(age > constants.HOUR):
            age -= constants.HOUR
            ticker += 1
        if(ticker > 1):
            return f"{ticker} hours {suffix}"
        else:
            return f"{ticker} hour {suffix}"
        
    elif(age > constants.MINUTE):   # Minutes
        while(age > constants.MINUTE):
            age -= constants.MINUTE
            ticker += 1
        if(ticker > 1):
            return f"{ticker} minutes {suffix}"
        else:
            return f"{ticker} minute {suffix}"
        
    else:   # Times less than 60 seconds (1 minute)
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
    stringList = string.splitlines()
    # for item in stringList:
    #     print(item)
    #     item = item.split()
    #     print(item)
    # string = string.replace("\n","")

    offset = terminalWidth - spaces
    tempstr = ""
    checkstr = ""
    tabulatedList = []
    for item in stringList:
        item = item.split()
        for word in item:
            if(len(word) > offset):
                tempstr = checkstr
                tempstr = spacesString(spaces) + tempstr + "\n"
                tabulatedList.append(tempstr)
                tempstr = ""
                checkstr = ""
                workingWord = word
                while(len(workingWord) > offset):
                    addWord = spacesString(spaces) + workingWord[:offset] + "\n"
                    tabulatedList.append(addWord)
                    workingWord = workingWord[offset:]
                addWord = spacesString(spaces) + workingWord + "\n"
                tabulatedList.append(addWord)
                continue
            checkstr = checkstr + word
            if(len(checkstr) < offset):
                tempstr = checkstr
                tempstr = tempstr + " "
                checkstr = tempstr
            elif (len(checkstr) == offset):
                tempstr = checkstr
                tempstr = spacesString(spaces) + tempstr + "\n"
                tabulatedList.append(tempstr)
                tempstr = ""
                checkstr = ""
            else:
                tempstr = spacesString(spaces) + tempstr + "\n"
                tabulatedList.append(tempstr)
                tempstr = word + " "
                checkstr = tempstr
            # print(tempstr)
        tempstr = spacesString(spaces) + tempstr + "\n"
        tabulatedList.append(tempstr)
        tempstr = ""
        checkstr = ""
    
    newStr = ""
    return newStr.join(tabulatedList)





    # WORKS
    """offset = terminalWidth - (spaces)
    tempstr = ""
    tabulatedList = []
    for item in stringList:
        for i in range(len(item)):
            tempstr = tempstr + item[i]
            if(len(tempstr) >= offset):
                tempstr = spacesString(spaces) + tempstr + "\n"
                print(tempstr)
                tabulatedList.append(tempstr)
                tempstr = ""
        tempstr = spacesString(spaces) + tempstr
        print(tempstr)
        tabulatedList.append(f"{tempstr}\n")
        tempstr = ""
    newStr = ""
    return newStr.join(tabulatedList)"""







    # OLD
    """for i in range(math.ceil(len(string)/offset)):
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
                break"""
    
    # index = 0
    # nextSpace = 0
    # charactersInLine = 0
    # while(index < len(string)):
    #     if((charactersInLine + (nextSpace - index)) > terminalWidth):



    #return addString



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