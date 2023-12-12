import datetime
from datetime import timezone
import math
import pyperclip
import curses
import webbrowser
import search
import json
import dump
import constants



def currentTimestamp():
    return datetime.datetime.now(timezone.utc).replace(tzinfo=timezone.utc).timestamp()


def getSearches(JSONPath):
    searches = []
    with open(JSONPath,"r") as read:
        data = json.load(read)
        s = data["searches"]
        read.close()

        for item in s:
            subs = item["subreddits"]
            subSearches = []
            for i in subs:
                name = i["name"]
                titleWL = i["whiteListTitle"]
                titleBL = i["blackListTitle"]
                flairWL = i["whiteListFlair"]
                flairBL = i["blackListFlair"]
                postWL = i["whiteListPost"]
                postBL = i["blackListPost"]
                subSearches.append(search.subSearch(name,titleWL,titleBL,flairWL,flairBL,postWL,postBL))

            searches.append(search.search(item["name"],item["lastSearchTime"],subSearches))
    
    return searches

"""
reddit is the reddit instance, searchCriteria is a search object, and numPosts is the number of posts to fetch per subreddit in
searchCriteria

"""
def getNumPosts(reddit, searchCriteria, numPosts = 20):
    posts = []
    for sub in searchCriteria.subreddits:
        subreddit = reddit.subreddit(sub.subreddit)
        for post in subreddit.new(limit=numPosts):
            posts.append(post)

    return posts




"""
Return values:
    -2 searches is empty
    -1 user pressed q to quit
    >=0 the index of the searches list that was chosen

"""
def getSearch(screen, searches):
    counter = 0
    if(searches):
        char = 0
        lineNum = 0
        while(char != ord('q')):
            screen.clear()
            screen.refresh()
            ticker = 0
            end = len(searches)
            if(lineNum+curses.LINES-1 < end):
                end = lineNum+curses.LINES-2

            for i in range(lineNum,end):
                screen.addstr(ticker,0,f"{ticker+1}. {searches[i].name}")
                ticker += 1
            
            screen.addstr(curses.LINES-1,curses.COLS-18,"(press q to quit)")
            screen.addstr(curses.LINES-1,0,f"<-- Line {lineNum + 1} -->")
            screen.refresh()
            char = screen.getch()
            if(char == ord('q')):
                return -1
            if(len(searches) > curses.LINES - 2):

                if char == curses.KEY_UP or char == ord('w'):
                    if(lineNum > 0):
                        lineNum -= 1
                    else:
                        lineNum = 0      
                elif char == curses.KEY_DOWN or char == ord('s'):
                    if(lineNum < len(searches) - curses.LINES + 2):
                        lineNum += 1
                    else:
                        lineNum = len(searches) - curses.LINES + 2
            if char == ord('e'):
                screen.addstr(curses.LINES-1,curses.COLS-18,"(press q to exit)")
                screen.addstr(curses.LINES-1,0,f"Enter a post number, then press enter: ")
                c = screen.getch() # Allows immediate exit if they press q
                if c == ord('q'):
                    continue

                # Otherwise update prompt
                screen.addstr(curses.LINES-1,0,"")
                screen.clrtoeol()
                screen.refresh()
                screen.addstr(curses.LINES-1,curses.COLS-18,"(enter q to exit)")
                screen.addstr(curses.LINES-1,0,f"Enter a post number, then press enter: ")

                # Display what they type, and require they press enter
                curses.echo()
                curses.nocbreak()
                curses.ungetch(c) # Adds the first character back to the buffer
                string = screen.getstr()

                # Undo displaying input and requiring enter be pressed
                curses.noecho()
                curses.cbreak()

                val = 0
                try:
                    val = int(string)
                except ValueError:
                    continue

                val -= 1
                if(val >= 0 and val < len(searches)):
                    screen.clear()
                    screen.refresh()
                    return val
        return -1
    else:
        return -2
            




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


def viewPost(post,screen):
    age = f"Created {formatAge(int(currentTimestamp()-post.created_utc))} ago"
    stringList = enboxList([post.title,age,"%separator%",post.selftext,"%separator%",post.url],curses.COLS)
    postLessThanFull = False
    if(len(stringList) < curses.LINES - 2):
        postLessThanFull = True
    
    postLineNum = 0
            
    while(True):
        screen.clear()
        ticker = 0
        end = len(stringList)
        if(postLineNum+curses.LINES-2 < end):
            end = postLineNum+curses.LINES-2

        for i in range(postLineNum,end):
            screen.addstr(ticker,0,stringList[i])
            
            ticker += 1


        screen.addstr(curses.LINES-1,curses.COLS-38,"(press h for help)  (press q to exit)")

        if(postLessThanFull or postLineNum == len(stringList) - curses.LINES + 3):
            screen.addstr(curses.LINES-1,0,f"<-- (end) -->")
        else:
            screen.addstr(curses.LINES-1,0,f"<-- Line {postLineNum+1} -->")

        screen.refresh()
        char = screen.getch()
        
        if char == ord('q'):
            break

        if(not postLessThanFull):
            if char == curses.KEY_UP or char == ord('w'):
                    if(postLineNum > 0):
                        postLineNum -= 1
                    else:
                        postLineNum = 0      
            elif char == curses.KEY_DOWN or char == ord('s'):
                if(postLineNum < len(stringList) - curses.LINES + 2):
                    postLineNum += 1
                else:
                    postLineNum = len(stringList) - curses.LINES + 2
        
        if char == ord('h'):
            screen.clear()
            screen.addstr(0,0,"Press the button in () to execute its command")
            screen.addstr(1,0,"(w) or (up arrow) scroll up")
            screen.addstr(2,0,"(s) or (down arrow) scroll down")
            screen.addstr(3,0,"(h) Displays this menu")
            screen.addstr(4,0,"(o) Opens the post in a new tab of the default web browser")
            screen.addstr(5,0,"(c) Copies the post url to the clipboard")
            screen.addstr(6,0,"(u) Prints the post url to the screen (You will have to manually copy it)")
            screen.addstr(7,0,"(a) Opens the author's page in a new tab of the default web browser")
            screen.addstr(8,0,"(q) returns to the previous screen")
            screen.addstr(9,0,"Press any key to exit this screen")
            screen.refresh()
            screen.getch()
        elif char == ord('o'):
            webbrowser.open_new_tab(post.url)
        elif char == ord('c'):
            copyToClipboard(post.url)
        elif char == ord('a'):
            webbrowser.open_new_tab(f"https://www.reddit.com/user/{post.author.name}/")
        elif char == ord('u'):
            screen.clear()
            screen.addstr(0,0,post.url)
            screen.addstr(curses.LINES-1,curses.COLS-18,"(press q to exit)")
            screen.addstr(curses.LINES-1,0,"")
            screen.refresh()
            while(char != ord('q')):
                char = screen.getch()


