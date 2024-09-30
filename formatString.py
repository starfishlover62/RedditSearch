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
    s = spacesString(length)
    s = s[:start] + string + s[start+len(string):]
    return s

def combineStrings(stringA,stringB,length,startA,startB):
    if(startB < startA):
        return combineStrings(stringB,stringA,length,startB,startA)
    stringA = placeString(stringA,length,startA)
    string = stringA[:startB] + stringB + stringA[startB+len(stringB):]
    return string

    
def spacesString(spaces):
    # st = ""
    # for i in range(spaces):
    #     st += " "
    return "".zfill(spaces).replace("0"," ")

def tabulate(string, terminalWidth = 80, spaces = 8):
    """
    Given a string, splits the string across enough lines, such that there
    each line begins with spaces number of spaces, and the total length of the line
    does not exceed terminalWidth. Each line is terminated with '\n'
    """
    # Removes tabs from the original string
    string = string.replace("\t","")

    # Splits the string into a list, separating at newlines already present (ends of paragraphs)
    stringList = string.splitlines()

    offset = terminalWidth - spaces # the number of non-space characters for the line
    tempstr = "" # Stores the working string while it is being built up
    checkstr = "" # Used for checking if adding the next word will push the string over the length limit
    tabulatedList = [] # A list comprised of each finished line
    for item in stringList:
        item = item.split() # Splits the paragraphs up by words. Separating at every space
        for word in item: # Loops through every word
            # If the word is longer than the amount of space for a single line
            if(len(word) > offset): 
                # Finishes the work in progress line
                tempstr = checkstr 
                tempstr = spacesString(spaces) + tempstr + "\n"
                tabulatedList.append(tempstr)
                tempstr = ""
                checkstr = ""

                # Used to split the long word (typically links) into multiple lines
                workingWord = word

                # Splits word into offset sized lines
                while(len(workingWord) > offset):
                    addWord = spacesString(spaces) + workingWord[:offset] + "\n"
                    tabulatedList.append(addWord)
                    workingWord = workingWord[offset:]
                
                # Gives the end of the word (the part less than offset length) its own line
                addWord = spacesString(spaces) + workingWord + "\n"
                tabulatedList.append(addWord)
                continue

            # For normal words
            checkstr = checkstr + word
            if(len(checkstr) < offset): # simply adds new word to tempstr if it won't make it too long
                tempstr = checkstr
                tempstr = tempstr + " "
                checkstr = tempstr
            elif (len(checkstr) == offset): # Adds word, then pushes line to list and starts new line
                tempstr = checkstr
                tempstr = spacesString(spaces) + tempstr + "\n"
                tabulatedList.append(tempstr)
                tempstr = ""
                checkstr = ""
            else: # Pushes current line to list, then starts a new line with word at the start
                tempstr = spacesString(spaces) + tempstr + "\n"
                tabulatedList.append(tempstr)
                tempstr = word + " "
                checkstr = tempstr
        
        # Adds leftover words at the end of paragraph
        tempstr = spacesString(spaces) + tempstr + "\n"
        tabulatedList.append(tempstr)
        tempstr = ""
        checkstr = ""
    
    newStr = ""
    return newStr.join(tabulatedList) # Combines list into a single string



def enbox(stringList, terminalWidth, leftPadding = 1, rightPadding = 1, leftMargin = 0, rightMargin = 0,fancy=False):
    boxWidth = terminalWidth - (leftMargin + rightMargin)
    textBoxWidth = boxWidth - (leftPadding + rightPadding)

    s = []

    topLeft="+"
    topRight="+"
    bottomLeft="+"
    bottomRight="+"
    sideLeft="+"
    sideRight="+"
    vertical="|"
    horizontal="-"

    if(fancy == True):
        topLeft="┌"
        topRight="┐"
        bottomLeft="└"
        bottomRight="┘"
        sideLeft="├"
        sideRight="┤"
        vertical="│"
        horizontal="─"

    # Creates the top border of the box
    boxStr = topLeft
    boxStr = boxStr + "".zfill(boxWidth-2).replace("0",horizontal)
    boxStr += topRight
    s.append(boxStr)
    boxStr = ""

    for item in stringList:
        if(item != None):
            # Creates a separating line in the box
            if(item == "%separator%"):
                boxStr += sideLeft
                boxStr = boxStr + "".zfill(boxWidth-2).replace("0",horizontal)
                boxStr += sideRight
                s.append(boxStr)
                boxStr = ""
            else:
                tempStr = tabulate(item,textBoxWidth,leftPadding+1)
                listStrings = tempStr.splitlines()
                # print(listStrings)
                for line in listStrings:
                    line = vertical + line[1:]
                    if(len(line) < boxWidth - 1):
                        line += spacesString((boxWidth-len(line)-1))
                    line += vertical
                    s.append(line)

    
    boxStr += bottomLeft
    boxStr = boxStr + "".zfill(boxWidth-2).replace("0",horizontal)
    boxStr += bottomRight
    s.append(boxStr)
    boxStr = ""

    return s