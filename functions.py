import datetime
from datetime import timezone
import math
import pyperclip
import curses
import webbrowser
import search
import json
import dump
import formatString
import scroll
import requests
from io import BytesIO
from PIL import Image
import PIL



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
                subSearches.append(search.SubredditSearch(name,titleWL,titleBL,flairWL,flairBL,postWL,postBL))

            searches.append(search.Search(item["name"],item["lastSearchTime"],subSearches))
    
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
    -2 searches is empty or user wants to perform a custom search
    -1 user pressed q to quit
    >=0 the index of the searches list that was chosen

"""
def getSearchNum(screen, searches):
    if(searches):
        ls = []
        ticker = 1
        for item in searches:
            ls.append(f"{ticker}. {item.name}")
            ticker = ticker + 1
        ls.append(f"{ticker}. Create a new search")
        
        toolTip = scroll.ToolTip(formatString.combineStrings("<-- Line 1 -- >","(press q to quit)",80,0,curses.COLS-18))
        page = scroll.ScrollingList(screen,ls,0,toolTip)
        lineNum = 0
        while(True):
            screen.clear()
            
            ticker = 0
            for item in page.getLines():
                screen.addstr(ticker,0,f"{item}")
                ticker = ticker + 1
            

            screen.refresh()
            char = screen.getch()
            if(char == ord('q')):
                return -1
            
            elif(char == curses.KEY_UP or char == ord('w')):
                lineNum = page.scrollUp()
                toolTip.replace([formatString.combineStrings(f"<-- Line {lineNum + 1} -- >","(press q to quit)",80,0,curses.COLS-18)])
            
            elif(char == curses.KEY_DOWN or char == ord('s')):
                lineNum = page.scrollDown()
                toolTip.replace([formatString.combineStrings(f"<-- Line {lineNum + 1} -- >","(press q to quit)",80,0,curses.COLS-18)])
            
            elif char == ord('e'):
                # Updates prompt
                toolTip.replace([formatString.combineStrings(f"Enter a search number, then press enter: ","(press q to exit)",80,0,curses.COLS-18)])
                screen.clear()
            
                ticker = 0
                for item in page.getLines():
                    screen.addstr(ticker,0,f"{item}")
                    ticker = ticker + 1
                

                screen.refresh()
                screen.addstr(curses.LINES-1,41,"") # Moves cursor to end of prompt
    

                # Display what they type, and require they press enter
                c = screen.getch() # Allows immediate exit if they press q
                if c == ord('q'):
                    toolTip.replace([formatString.combineStrings(f"<-- Line {lineNum + 1} -- >","(press q to quit)",80,0,curses.COLS-18)])
                    continue
                toolTip.replace([formatString.combineStrings(f"Enter a search number, then press enter: ","(enter q to quit)",80,0,curses.COLS-18)])
                ticker = 0
                for item in page.getLines():
                    screen.addstr(ticker,0,f"{item}")
                    ticker = ticker + 1
                

                screen.refresh()
                screen.addstr(curses.LINES-1,41,"") # Moves cursor to end of prompt
                curses.echo()
                curses.nocbreak()
                curses.ungetch(c) # Adds the first character back to the buffer
                string = screen.getstr()

                # Undo displaying input and requiring enter be pressed
                curses.noecho()
                curses.cbreak()

                # Ensures that their input is an integer
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
                elif(val == len(searches)):
                    screen.clear()
                    screen.refresh()
                    return -2
                toolTip.replace([formatString.combineStrings(f"<-- Line {lineNum + 1} -- >","(press q to quit)",80,0,curses.COLS-18)])
        return -1
    else:
        return -2
            

def createSearch(screen):
    """
    Creates a search object found in search.py. Prompts user to input data to create this object
    """

    # Clears out the screen to prepare it for creating the search
    screen.clear()
    screen.refresh()

    stringList = []
    questions = ["Name of search:","Subreddit:","Whitelisted title:","Blacklisted title:","Whitelisted flair:","Blacklisted flair:","Whitelisted word in post:","Blacklisted word in post:"]
    searchBuild = [] # Saves the name, creation data, and the list of subreddit searches
    subSearchBuild = [] # Used to save the componentes of a subreddit search while it is being built
    questionIndex = 0 # The current index of questions array
    lineNum = 0
    quit = False
    toolTip = scroll.ToolTip([questions[questionIndex],formatString.combineStrings(f"<-- Line {lineNum + 1} -- >","(press q to quit)",80,0,curses.COLS-18)])
    page = scroll.ScrollingList(screen,stringList,0,toolTip)

    while(True):
        if(quit):
            break

        page.print()

        
        placeCursor(screen,x=16,y=curses.LINES-2)
        screen.refresh()
        if(questionIndex == 0):
            toolTip.replace([questions[questionIndex]])
            page.print()
            placeCursor(screen,x=16,y=curses.LINES-1)
            
            # Gets input
            curses.echo() # Displays what they type
            curses.nocbreak() # Requires that they press enter
            string = screen.getstr().decode("ASCII") # Their input

            # Undo displaying input and requiring enter be pressed
            curses.noecho()
            curses.cbreak()
            searchBuild.append(string)
            searchBuild.append(None)
            stringList.append(f"{questions[questionIndex]} {string}")
            questionIndex = questionIndex + 1
            
        else: # For all questions except name of search
            temp = []
            while(True):
                toolTip.replace([f"Add a {questions[questionIndex]} (y/n):"])
                page.print()
                placeCursor(screen,x=26,y=curses.LINES-1)
                if (questionIndex == 1 and (len(temp) > 0)): # Allows user to only add one subreddit at a time.
                    c = ord('n')
                    quit = False
                else:
                    c = screen.getch() # Gets the character they type
                if c == ord('n'):
                    if(questionIndex == 1):
                        if(len(temp) == 0):
                            quit = True
                            break
                        subSearchBuild.append(temp[0])
                        stringList.append(f"|----{questions[questionIndex]} {temp[0]}")
                    else:
                        subSearchBuild.append(temp)
                        stringList.append(f"{questions[questionIndex]} {string}")
                    questionIndex = questionIndex + 1
                    if(questionIndex >= len(questions)):
                        questionIndex = 1
                        if(len(searchBuild) < 3):
                            searchBuild.append([])
                        searchBuild[2].append(search.SubredditSearch(subSearchBuild[0],subSearchBuild[1],subSearchBuild[2],subSearchBuild[3],subSearchBuild[4],subSearchBuild[5],subSearchBuild[6]))
                    break
                elif c == ord('y'): # Otherwise
                    # Update prompt to remove option to quit
                    toolTip.replace([questions[questionIndex]])
                    page.print()
                    placeCursor(screen,x=26,y=curses.LINES-1)

                    # Gets input
                    curses.echo() # Displays what they type
                    curses.nocbreak() # Requires that they press enter
                    string = screen.getstr().decode("ASCII") # Their input

                    # Undo displaying input and requiring enter be pressed
                    curses.noecho()
                    curses.cbreak()
                    temp.append(string)
        
    if(len(searchBuild) >= 3):
        s = search.Search(searchBuild[0],searchBuild[1],searchBuild[2])
        dump.saveSearches(s,"checkValidSearch.json")

        return s
    
    return






def performSearch(reddit,search,screen = None):
    posts = []
    ticker = 0
    for sub in search.subreddits:
        subreddit = reddit.subreddit(sub.name)
        for post in subreddit.new(limit=None):
            if(post.created_utc == None):
                continue
            if(post.created_utc < search.lastSearchTime):
                break
            else:
                if(filterPost(post,sub)):
                    posts.append(post)
            ticker = ticker + 1
            if(screen != None):
                startX = 13
                startY = 8
                screen.clear()
                screen.addstr(curses.LINES-1,0," (This may take a while, depending on time since the search was last performed)")
                screen.addstr(startY,startX,"                         _     _ ")
                screen.addstr(startY+1,startX," ___  ___  __ _ _ __ ___| |__ (_)_ __   __ _ ")
                screen.addstr(startY+2,startX,"/ __|/ _ \\/ _` | '__/ __| '_ \\| | '_ \\ / _` |")
                if(ticker % 3 == 1):
                    screen.addstr(startY+3,startX,"\\__ \\  __/ (_| | | | (__| | | | | | | | (_| |  _")
                    screen.addstr(startY+4,startX,"|___/\\___|\\__,_|_|  \\___|_| |_|_|_| |_|\\__, | (_)")

                elif(ticker % 3 == 2):
                    screen.addstr(startY+3,startX,"\\__ \\  __/ (_| | | | (__| | | | | | | | (_| |  _   _")
                    screen.addstr(startY+4,startX,"|___/\\___|\\__,_|_|  \\___|_| |_|_|_| |_|\\__, | (_) (_)")

                if(ticker % 3 == 0):
                    screen.addstr(startY+3,startX,"\\__ \\  __/ (_| | | | (__| | | | | | | | (_| |  _   _   _")
                    screen.addstr(startY+4,startX,"|___/\\___|\\__,_|_|  \\___|_| |_|_|_| |_|\\__, | (_) (_) (_)")

                screen.addstr(startY+5,startX,"                                       |___/ ")
                screen.addstr(0,0,"")
                screen.refresh()

    return posts

def filterPost(post,subReddit):

    # Easier reference to post contents
    title = post.title
    flair = post.link_flair_text
    content = post.selftext

    # Check blacklists

    if(not title == None and not subReddit.titleBL == None):
        for t in subReddit.titleBL:
            if(t.lower() in title.lower()):
                return False
            
    if(not flair == None and not subReddit.flairBL == None):
        for f in subReddit.flairBL:
            if(f.lower() in flair.lower()):
                return False
    
    if(not content == None and not subReddit.postBL == None):
        for c in subReddit.postBL:
            if(c.lower() in content.lower()):
                return False
            
    # Check whitelists

    if(not title == None and not subReddit.titleWL == None):
        for t in subReddit.titleWL:
            if(t.lower() in title.lower()):
                return True
            
    if(not flair == None and not subReddit.flairWL == None):
        for f in subReddit.flairWL:
            if(f.lower() in flair.lower()):
                return True
    
    if(not content == None and not subReddit.postWL == None):
        for c in subReddit.postWL:
            if(c.lower() in content.lower()):
                return True
    
    return False


def getHeaders(posts):
    headers = []
    ticker = 1
    if (not posts == None):
        for post in posts:
            # Age
            age = post.created_utc
            if(not age == None):
                age = int(currentTimestamp() - age)
            else:
                age = 0

            # Subreddit
            sub = formatString.removeNonAscii(post.subreddit.display_name)
            if(sub == None):
                sub = "<NO SUBREDDIT>"

            # Title
            title = formatString.removeNonAscii(post.title)
            if(title == None):
                title = "<NO TITLE>"
            
            # Flair
            flair = post.link_flair_text
            if(flair == None):
                flair = "<NO FLAIR>"
            
            # Author
            author = post.author
            if(author == None):
                author = "deleted"
            else:
                author = author.name

            try:
                headers += (formatString.enbox([f"{ticker}). {title}",flair,author,f"Posted in ({sub}), {formatString.formatAge(age,"ago")}"],curses.COLS))
            except AttributeError:
                continue
            ticker += 1
    return headers


def sortPosts(posts):
    """
    Sorts a list by creation date. The newest posts come first
    """
    posts.sort(key=postAge, reverse=True)
    return posts


def postAge(post):
    """
    Provides the creation time of a post, in UTC
    """
    return post.created_utc


def copyToClipboard(string):
    """
    Copies the string to the clipboard
    """
    pyperclip.copy(string)


def getInput(prompt, lowerBound, upperBound, numAttempts = -1):
    """
    Gets an integer input from an user, verifies that it is within some bounds, and 
    allows them a set number of attempts to get a valid input. Most likely unused, and able to be removed
    """
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
    """
    Enters a viewing mode for a single post. Arrow keys can be used to move between posts.
    """
    age = f"{formatString.formatAge(int(currentTimestamp()-post.created_utc),"ago")}"
    stringList = formatString.enbox([formatString.removeNonAscii(post.title),post.author.name,f"Posted in ({formatString.removeNonAscii(post.subreddit.display_name)}), {age}","%separator%",formatString.removeNonAscii(post.selftext),"%separator%",post.url],curses.COLS)
    
    lineNum = 0

    toolTip = scroll.ToolTip([formatString.combineStrings(f"<-- Line 1 -- >","(press q to quit)",80,0,curses.COLS-18)])

    page = scroll.ScrollingList(screen,stringList,0,toolTip)
            
    while(True):
        screen.clear()
        toolTip.replace([formatString.combineStrings(f"<-- Line {lineNum + 1} -- >","(press q to quit)",80,0,curses.COLS-18)])
        ticker = 0
        for item in page.getLines():
            screen.addstr(ticker,0,f"{item}")
            ticker = ticker + 1

        

        screen.refresh()
        char = screen.getch()
        
        if char == ord('q'):
            break
        elif(char == curses.KEY_DOWN or char == ord('s')):
            lineNum = page.scrollDown()
        elif(char == curses.KEY_UP or char == ord('w')):
            lineNum = page.scrollUp()
        elif(char == curses.KEY_LEFT or char == ord('a')):
            return -1
        elif(char == curses.KEY_RIGHT or char == ord('d')):
            return 1
        elif char == ord('h'):
            while(True):
                screen.clear()
                helpPage = scroll.ScrollingList(screen,["Press the button in () to execute its command",
                                                        "(w) or (up arrow) scroll up",
                                                        "(s) or (down arrow) scroll down",
                                                        "(a) or (left arrow) view previous post",
                                                        "(d) or (right arrow) view next post",
                                                        "(h) Displays this menu",
                                                        "(i) If post is an image, opens image",
                                                        "(o) Opens the post in a new tab of the default web browser",
                                                        "(c) Copies the post url to the clipboard",
                                                        "(u) Prints the post url to the screen (You will have to manually copy it)",
                                                        "(m) Opens the author's page in a new tab of the default web browser",
                                                        "(q) returns to the previous screen",
                                                        "Press 'q' to exit this screen"],0,None)
                
                ticker = 0
                for item in helpPage.getLines():
                    screen.addstr(ticker,0,f"{item}")
                    ticker = ticker + 1
                screen.refresh()
                char = screen.getch()
                if char == ord('q'):
                    break
                elif(char == ord('s')):
                    helpPage.scrollDown()
                elif(char == ord('w')):
                    helpPage.scrollUp()

        elif char == ord('o'):
            webbrowser.open_new_tab(post.url)
        elif char == ord('c'):
            copyToClipboard(post.url)
        elif char == ord('i'):
            response = requests.get(post.url)
            if(response.status_code == 200):
                try:
                    img = Image.open(BytesIO(response.content))
                    img.show()
                except  PIL.UnidentifiedImageError:
                    pass
        elif char == ord('m'):
            webbrowser.open_new_tab(f"https://www.reddit.com/user/{post.author.name}/")
        elif char == ord('u'):
            screen.clear()
            screen.addstr(0,0,post.url)
            screen.addstr(curses.LINES-1,curses.COLS-18,"(press q to exit)")
            screen.addstr(curses.LINES-1,0,"")
            screen.refresh()
            while(char != ord('q')):
                char = screen.getch()


def placeCursor(screen,x,y):
    screen.addstr(y,x,"")
