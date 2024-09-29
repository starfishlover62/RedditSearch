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
import prawcore



def currentTimestamp():
    return datetime.datetime.now(timezone.utc).timestamp()


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


def getSearchNum(screen, searches):
    """
    Displays a list of searches, and has the user select one to be performed. Also allows the user
    to create or delete searches.
    Return Values: 
        -3 : Search was deleted (therefore save)
        -2 : Searches parameter is empty, or the user selected to create a new search
        -1 : User pressed q to quit
        >=0: The index of the searches list that was chosen
    """
    if(searches):
        ls = []
        ticker = 1
        for item in searches:
            ls.append(f"{ticker}. {item.name}")
            ticker = ticker + 1
        lineNum = 0
        toolTip = scroll.ToolTip(["",formatString.combineStrings(f"<-- Line {lineNum + 1} -- >","((a) add, (e) select, (d) delete, (v) view, or (q) quit)",80,0,curses.COLS-57)])
        page = scroll.ScrollingList(screen,ls,0,toolTip)
        
        while(True):
            # Updates tooltip and prints page to screen
            toolTip.replace(["",formatString.combineStrings(f"<-- Line {lineNum + 1} -- >","((a) add, (e) select, (d) delete, (v) view, or (q) quit)",80,0,curses.COLS-57)])
            page.print()

            char = screen.getch() # Gets single character input from user
            if(char == ord('q')): # Returns from function, signalling to quit program
                return -1
            
            elif(char == curses.KEY_UP or char == ord('w')): # Scrolls up
                lineNum = page.scrollUp()
                continue
            
            elif(char == curses.KEY_DOWN or char == ord('s')): # Scrolls down
                lineNum = page.scrollDown()
                continue

            elif(char == ord('a')):
                return -2
            
            # User either wants to perform a search/create one or delete a search.
            # Either way, input is gathered the same
            elif char == ord('e') or char == ord('d') or char == ord('v'):
                # Updates prompt(tooltip), then prints to screen
                if(char == ord('e')):
                    toolTip.replace(["~Selecting~",formatString.combineStrings(f"Enter a search number, then press enter: ","(press q to exit)",80,0,curses.COLS-18)])
                elif(char == ord('v')):
                    toolTip.replace(["~Viewing~",formatString.combineStrings(f"Enter a search number, then press enter: ","(press q to exit)",80,0,curses.COLS-18)])
                else:
                    toolTip.replace(["~Deleting~",formatString.combineStrings(f"Enter a search number, then press enter: ","(press q to exit)",80,0,curses.COLS-18)])
                page.print()

                # Moves cursor to end of prompt
                placeCursor(screen,x=41,y=curses.LINES-1)
    

                # Display what they type, and require they press enter
                c = screen.getch() # Allows immediate exit if they press q
                if c == ord('q'):
                    continue

                # Updates prompt(tooltip), then prints to screen
                if(char == ord('e')):
                    toolTip.replace(["~Selecting~",formatString.combineStrings(f"Enter a search number, then press enter: ","(enter q to exit)",80,0,curses.COLS-18)])
                elif(char == ord('v')):
                    toolTip.replace(["~Viewing~",formatString.combineStrings(f"Enter a search number, then press enter: ","(enter q to exit)",80,0,curses.COLS-18)])
                else:
                    toolTip.replace(["~Deleting~",formatString.combineStrings(f"Enter a search number, then press enter: ","(enter q to exit)",80,0,curses.COLS-18)])
                page.print()

                # Moves cursor to end of prompt
                placeCursor(screen,x=41,y=curses.LINES-1)

                # Displays user's input, and requires they press enter to submit
                curses.echo()
                curses.nocbreak()
                curses.ungetch(c) # Adds the first character back to the buffer
                string = screen.getstr()

                # Undo displaying input and requiring enter be pressed
                curses.noecho()
                curses.cbreak()

                # Attempts to convert their input to an integer
                val = 0
                try:
                    val = int(string)
                except ValueError:
                    continue
                

                val -= 1 # Offsets input, so it is an index
                if(val >= 0 and val < len(searches)):
                    if(char == ord('d')):
                        del searches[val]
                        return -3
                    elif(char == ord('v')):
                        view = searchTree(searches[val])
                        viewLine = 0
                        viewTool = scroll.ToolTip(["",formatString.combineStrings(f"<-- Line {viewLine + 1} -- >","press (q) to exit",80,0,curses.COLS-18)])
                        viewPage = scroll.ScrollingList(screen,view,viewLine,viewTool)
                        while True:
                            viewTool.replace([formatString.combineStrings(f"<-- Line {viewLine + 1} -- >","press (q) to exit",80,0,curses.COLS-18)])
                            viewPage.print()
                            viewChar = screen.getch()
                            if(viewChar == ord('q')): # Returns from function, signalling to quit program
                                break
                            
                            elif(viewChar == curses.KEY_UP or viewChar == ord('w')): # Scrolls up
                                viewLine = viewPage.scrollUp()
                                continue
                            
                            elif(viewChar == curses.KEY_DOWN or viewChar == ord('s')): # Scrolls down
                                viewLine = viewPage.scrollDown()
                                continue
                    else:
                        return val
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
    questionIndex = 0 # The current index of questions array
    returnSearch = search.Search()
    lineNum = 0
    quit = False
    atLeastOneSub = False
    toolTip = scroll.ToolTip([questions[questionIndex],formatString.combineStrings(f"<-- Line {lineNum + 1} -- >","(press q to quit)",80,0,curses.COLS-18)])
    page = scroll.ScrollingList(screen,stringList,0,toolTip)
    temp = []

    while(True):
        if(quit):
            break

        page.print()

        
        # placeCursor(screen,x=16,y=curses.LINES-2)
        # screen.refresh()
        if(questionIndex == 0):
            # Gets search name
            prompt = questions[questionIndex]
            toolTip.replace([prompt])
            page.print()
            placeCursor(screen,x=(len(prompt) + 1),y=curses.LINES-1)
            
            # Gets input
            curses.echo() # Displays what they type
            curses.nocbreak() # Requires that they press enter
            string = screen.getstr().decode("ASCII") # Their input

            # Undo displaying input and requiring enter be pressed
            curses.noecho()
            curses.cbreak()
            returnSearch.update(name = string)
            questionIndex = questionIndex + 1
            stringList = searchTree(returnSearch)
            page.updateStrings(screen,stringList,0,toolTip)

        elif(questionIndex == 1):
            # Gets first subreddit name
            prompt = questions[questionIndex]
            toolTip.replace([prompt])
            page.print()
            placeCursor(screen,x=(len(prompt) + 1),y=curses.LINES-1)
            
            # Gets input
            curses.echo() # Displays what they type
            curses.nocbreak() # Requires that they press enter
            string = screen.getstr().decode("ASCII") # Their input

            # Undo displaying input and requiring enter be pressed
            curses.noecho()
            curses.cbreak()
            if(returnSearch.subreddits == None): # If this is the first sub search, set subreddits value
               returnSearch.update(subreddits=[search.SubredditSearch()])
            else: # Otherwise, append a new subreddit search
               returnSearch.update(subreddits=returnSearch.subreddits.append(search.SubredditSearch()))
            returnSearch.subreddits[-1].update(sub=string)
            questionIndex = questionIndex + 1
            stringList = searchTree(returnSearch)
            page.updateStrings(screen,stringList,0,toolTip)
            
        else: # For all questions except name of search
            while(True):
                prompt = f"Add a {questions[questionIndex]} (y/n):"
                toolTip.replace([prompt])
                page.print()
                placeCursor(screen,x=(len(prompt) + 1),y=curses.LINES-1)
                c = screen.getch() # Gets the character they type

                # User entered n. Moves on to next question. If this was the last question, asks
                # user if they want to add another subreddit.
                if c == ord('n'):
                    questionIndex = questionIndex + 1
                    temp = []
                    if(questionIndex >= len(questions)):
                        prompt = f"Add another Subreddit (y/n):"
                        toolTip.replace([prompt])
                        page.print()
                        placeCursor(screen,x=(len(prompt) + 1),y=curses.LINES-1)
                        answer = screen.getch()
                        if(answer == ord('n')):
                            quit = True
                            break
                        else:
                            questionIndex = 1
                            break
                elif c == ord('y'): # Otherwise
                    # Update prompt to remove option to quit
                    prompt = f"{questions[questionIndex]}"
                    toolTip.replace([prompt])
                    page.print()
                    placeCursor(screen,x=(len(prompt) + 1),y=curses.LINES-1)

                    # Gets input
                    curses.echo() # Displays what they type
                    curses.nocbreak() # Requires that they press enter
                    string = screen.getstr().decode("ASCII") # Their input

                    # Undo displaying input and requiring enter be pressed
                    curses.noecho()
                    curses.cbreak()
                    if(not string.strip() == ""):
                        temp.append(string)
                        if(questionIndex == 2):
                            returnSearch.subreddits[-1].update(titleWL=temp)
                        elif(questionIndex == 3):
                            returnSearch.subreddits[-1].update(titleBL=temp)
                        elif(questionIndex == 4):
                            returnSearch.subreddits[-1].update(flairWL=temp)
                        elif(questionIndex == 5):
                            returnSearch.subreddits[-1].update(flairBL=temp)
                        elif(questionIndex == 6):
                            returnSearch.subreddits[-1].update(postWL=temp)
                        elif(questionIndex == 7):
                            returnSearch.subreddits[-1].update(postBL=temp)
                        stringList = searchTree(returnSearch)
                        page.updateStrings(screen,stringList,0,toolTip)
                            
    return returnSearch

def placeItem(item,middle,last):
    tierThree="  |    |    |->"
    tierThreeEmpty="            |->"
    tierThreeEnd="       |    |->"
    tierThreeNoMiddle="  |         |->"
    if(len(item) > (79-len(tierThree))):
        if(last == True):
            item = f"{item[:76-(len(tierThreeEmpty))]}..."
        else:
            item = f"{item[:76-(len(tierThree))]}..."
    if(middle == True):
        if(last == True):
            return (f"{tierThreeEmpty}{item}")
        else:      
            return (f"{tierThreeEnd}{item}")
    else:
        if(last == True):
            return (f"{tierThreeNoMiddle}{item}")
        else:      
            return (f"{tierThree}{item}")

def placeTitle(name,middle):
    tierTwo="  |    |->"
    tierTwoEmpty="       |->"

    if(middle == True):
        return (f"{tierTwoEmpty}{name}")
    else:
        return (f"{tierTwo}{name}")
    



def searchTree(search):
    """
    Returns a list of strings representing a tree-style view of a search
    """
    if(search is not None):
        stringList = []
        if(not search.name == None):
            stringList.append(search.name)
            if(not search.subreddits == None):
                tierOne="  |->"
                tierTwo="  |    |->"
                tierTwoEmpty="       |->"
                tierThree="  |    |    |->"
                tierThreeEmpty="            |->"
                subNum=0
                lastSub=len(search.subreddits)
                finalSub=False
                for sub in search.subreddits:
                    subNum = subNum+1
                    if(subNum >= lastSub):
                        finalSub = True
                    if(not sub.titleWL == None and len(sub.titleWL) > 0):
                        subLast = 0
                    if(not sub.titleBL == None and len(sub.titleBL) > 0):
                        subLast = 1
                    if(not sub.flairWL == None and len(sub.flairWL) > 0):
                        subLast = 2
                    if(not sub.flairBL == None and len(sub.flairBL) > 0):
                        subLast = 3
                    if(not sub.postWL == None and len(sub.postWL) > 0):
                        subLast = 4
                    if(not sub.postBL == None and len(sub.postBL) > 0):
                        subLast = 5
                    
                    stringList.append(f"{tierOne}{sub.name}")
                    if(not sub.titleWL == None and len(sub.titleWL) > 0):
                        stringList.append(placeTitle("Title whitelist",finalSub))
                        for item in sub.titleWL:
                            if(subLast == 0):
                                stringList.append(placeItem(item,finalSub,True))
                            else:
                                stringList.append(placeItem(item,finalSub,False))

                    if(not sub.titleBL == None and len(sub.titleBL) > 0):
                        stringList.append(placeTitle("Title blacklist",finalSub))
                        for item in sub.titleBL:
                            if(subLast == 1):
                                stringList.append(placeItem(item,finalSub,True))
                            else:
                                stringList.append(placeItem(item,finalSub,False))

                    if(not sub.flairWL == None and len(sub.flairWL) > 0):
                        stringList.append(placeTitle("Flair whitelist",finalSub))
                        for item in sub.flairWL:
                            if(subLast == 2):
                                stringList.append(placeItem(item,finalSub,True))
                            else:
                                stringList.append(placeItem(item,finalSub,False))

                    if(not sub.flairBL == None and len(sub.flairBL) > 0):
                        stringList.append(placeTitle("Flair blacklist",finalSub))
                        for item in sub.flairBL:
                            if(subLast == 3):
                                stringList.append(placeItem(item,finalSub,True))
                            else:
                                stringList.append(placeItem(item,finalSub,False))

                    if(not sub.postWL == None and len(sub.postWL) > 0):
                        stringList.append(placeTitle("Post whitelist",finalSub))
                        for item in sub.postWL:
                            if(subLast == 4):
                                stringList.append(placeItem(item,finalSub,True))
                            else:
                                stringList.append(placeItem(item,finalSub,False))

                    if(not sub.postBL == None and len(sub.postBL) > 0):
                        stringList.append(placeTitle("Post blacklist",finalSub))
                        for item in sub.postBL:
                            if(subLast == 5):
                                stringList.append(placeItem(item,finalSub,True))
                            else:
                                stringList.append(placeItem(item,finalSub,False))
        return stringList
    else:
        return None





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
    """
    Formats and returns post header information. This includes: subreddit, title, flair, author, and age
    """
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
    if(lowerBound < 0  or upperBound < 0): # Makes sure both bounds are valid
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
    Enters a viewing mode for a single post. Arrow keys can be used to move through and between posts.
    """
    age = f"{formatString.formatAge(int(currentTimestamp()-post.created_utc),"ago")}"
    stringList = formatString.enbox([formatString.removeNonAscii(post.title),post.author.name,f"Posted in ({formatString.removeNonAscii(post.subreddit.display_name)}), {age}","%separator%",formatString.removeNonAscii(post.selftext),"%separator%",post.url],curses.COLS)
    
    lineNum = 0

    toolTip = scroll.ToolTip([formatString.combineStrings(f"<-- Line 1 -- >","(press q to quit)",80,0,curses.COLS-18)])
    page = scroll.ScrollingList(screen,stringList,0,toolTip)
            
    while(True):
        toolTip.replace([formatString.combineStrings(f"<-- Line {lineNum + 1} -- >","(press q to quit)",80,0,curses.COLS-18)])
        page.print()

        char = screen.getch()
        
        # Exit viewing the post
        if char == ord('q'):
            break

        # Scroll down in the post
        elif(char == curses.KEY_DOWN or char == ord('s')):
            lineNum = page.scrollDown()
        
        # Scroll up in the post
        elif(char == curses.KEY_UP or char == ord('w')):
            lineNum = page.scrollUp()

        # View previous post
        elif(char == curses.KEY_LEFT or char == ord('a')):
            return -1
        
        # View next post
        elif(char == curses.KEY_RIGHT or char == ord('d')):
            return 1
        
        # Display help screen
        elif char == ord('h'):
            screen.clear()
            helpPage = scroll.ScrollingList(screen,[
                "Press the button in () to execute its command",
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
                "Press any key to exit this screen"],0,None)
            placeCursor(screen,x=0,y=curses.LINES-1)
            helpPage.print()
            char = screen.getch() # Help screen disappears when user presses any key

        # Open post in web browser
        elif char == ord('o'):
            webbrowser.open_new_tab(post.url)

        # Copy url to clipboard
        elif char == ord('c'):
            copyToClipboard(post.url)
        
        # Open image, if present
        elif char == ord('i'):
            response = requests.get(post.url) # Gets information from Internet
            if(response.status_code == 200): # Code 200 means information was sucessfully gathered
                try:
                    img = Image.open(BytesIO(response.content)) # Converts binary data to image
                    img.show() # Opens the image in default image viewer
                except  PIL.UnidentifiedImageError: # Typically thrown if the link was not an image.
                    pass
        
        # Open author's page
        elif char == ord('m'):
            webbrowser.open_new_tab(f"https://www.reddit.com/user/{post.author.name}/")
        
        # Displays url of post
        elif char == ord('u'):
            screen.clear()
            screen.addstr(0,0,post.url)
            screen.addstr(curses.LINES-1,curses.COLS-24,"(press any key to exit)")
            placeCursor(screen,x=0,y=curses.LINES-1)
            screen.refresh()
            char = screen.getch()


def placeCursor(screen,x,y):
    """
    Moves the cursor to the specified location
    """
    screen.addstr(y,x,"")



def convertHTML(original):
    """
    Takes a post's selftext_html, and converts to a list of strings, which are used in various other functions
    """
    stringsList = []

    while(not original.find("<p>") == -1):
        start = original.find("<p>")
        end = original.find("</p>")
        stringsList.append(original[start+3:end])
        original = original[:start] + original[end+4:]
        
    print(original)
    final = ""
    for i in range(len(stringsList)):
        while(not stringsList[i].find("&#39;") == -1):
            apostrophe = stringsList[i].find("&#39;")
            stringsList[i] = stringsList[i][:apostrophe] + "'" + stringsList[i][apostrophe+5:]
        # print(stringsList[i])
        # print()
        final = final + stringsList[i] + "\n\n"
    # print(final)
    val = formatString.enbox([final],80)
    return val


def isValidSubreddit(userReddit,name):
    """
    Pulls a single post from the subreddit specified in name, using the praw reddit instance userReddit.
    Returns 1 if sub is valid, -1 if it does not exist or has been banned, or -2 if it is private
    """
    try:
        for submission in userReddit.subreddit(name).new(limit=1):
            s = submission.id
    except (prawcore.exceptions.NotFound, prawcore.exceptions.Redirect, prawcore.exceptions.BadRequest, AttributeError): # Errors that arise when the subreddit does not exist
        return -1
    except prawcore.exceptions.Forbidden:
        return -2
    return 1