# Libraries
import datetime
from datetime import timezone
import pyperclip
import curses
import webbrowser
import json
import requests
from io import BytesIO
from PIL import Image
import PIL
import prawcore
import re

# Provided
import search
from tree import searchTree
import formatString
import scroll

import config


def close(screen):
    """
    Closes the ncurses window and restores the terminal to its previous state
    """
    curses.nocbreak()
    screen.keypad(0)
    curses.echo()
    curses.endwin()


def currentTimestamp():
    """
    Returns the current UTC timestamp
    """
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

def getNumPosts(reddit, searchCriteria, numPosts = 20):
    """
    reddit is the reddit instance, searchCriteria is a search object, and numPosts is the number of posts to fetch per subreddit in
    searchCriteria

    """
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
        toolTip = scroll.ToolTip(["",formatString.combineStrings(f"<-- Line {lineNum + 1} -- >","((a) add, (e) select, (d) delete, (v) view, or (q) quit)",curses.COLS,0,curses.COLS-57)])
        page = scroll.ScrollingList(screen,ls,0,toolTip)
        
        while(True):
            # Updates tooltip and prints page to screen
            toolTip.replace(["",formatString.combineStrings(f"<-- Line {lineNum + 1} -- >","((a) add, (e) select, (d) delete, (v) view, or (q) quit)",curses.COLS,0,curses.COLS-57)])
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
                    toolTip.replace(["~Selecting~",formatString.combineStrings(f"Enter a search number, then press enter: ","(press q to exit)",curses.COLS,0,curses.COLS-18)])
                elif(char == ord('v')):
                    toolTip.replace(["~Viewing~",formatString.combineStrings(f"Enter a search number, then press enter: ","(press q to exit)",curses.COLS,0,curses.COLS-18)])
                else:
                    toolTip.replace(["~Deleting~",formatString.combineStrings(f"Enter a search number, then press enter: ","(press q to exit)",curses.COLS,0,curses.COLS-18)])
                page.print()

                # Moves cursor to end of prompt
                placeCursor(screen,x=41,y=curses.LINES-1)
    

                # Display what they type, and require they press enter
                c = screen.getch() # Allows immediate exit if they press q
                if c == ord('q'):
                    continue

                # Updates prompt(tooltip), then prints to screen
                if(char == ord('e')):
                    toolTip.replace(["~Selecting~",formatString.combineStrings(f"Enter a search number, then press enter: ","(enter q to exit)",curses.COLS,0,curses.COLS-18)])
                elif(char == ord('v')):
                    toolTip.replace(["~Viewing~",formatString.combineStrings(f"Enter a search number, then press enter: ","(enter q to exit)",curses.COLS,0,curses.COLS-18)])
                else:
                    toolTip.replace(["~Deleting~",formatString.combineStrings(f"Enter a search number, then press enter: ","(enter q to exit)",curses.COLS,0,curses.COLS-18)])
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
                        view = searchTree(searches[val],curses.COLS,config.fancy_characters)
                        viewLine = 0
                        viewTool = scroll.ToolTip(["",formatString.combineStrings(f"<-- Line {viewLine + 1} -- >","press (q) to exit",curses.COLS,0,curses.COLS-18)])
                        viewPage = scroll.ScrollingList(screen,view,viewLine,viewTool)
                        while True:
                            viewTool.replace([formatString.combineStrings(f"<-- Line {viewLine + 1} -- >","press (q) to exit",curses.COLS,0,curses.COLS-18)])
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
    toolTip = scroll.ToolTip([questions[questionIndex],formatString.combineStrings(f"<-- Line {lineNum + 1} -- >","(press q to quit)",curses.COLS,0,curses.COLS-18)])
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
            stringList = searchTree(returnSearch,curses.COLS,config.fancy_characters)
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
            stringList = searchTree(returnSearch,curses.COLS,config.fancy_characters)
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
                        stringList = searchTree(returnSearch,curses.COLS,config.fancy_characters)
                        page.updateStrings(screen,stringList,0,toolTip)
                            
    return returnSearch


def performSearch(reddit,search,screen = None,minCols=80,minLines=24):
    """
    Gathers posts that meat the search object criteria, using the reddit object. 
    If a screen object is provided, displays a simple search in progress message.
    """
    posts = []
    ticker = 0
    if(screen != None):
        screen.clear()
        screen.refresh()
        string = "Searching..."
        stringTicker = 0
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
            # with open("output.txt","a") as f:
            #     f.write(f"{ticker}\n")
            
            if(screen != None):
                resize = eventListener(screen,False,5)
                if(resize == "resize"):
                    size = list(screen.getmaxyx())
                    if(size[0] < minLines):
                        size[0] = minLines
                    if(size[1] < minCols):
                        size[1] = minCols
                    curses.resize_term(size[0],size[1])
                screen.clear()
                waitMessage = "(This may take a while, depending on time since the search was last performed)"
                screen.addstr(curses.LINES-1,int((curses.COLS-len(waitMessage))/2),waitMessage)
                stringTicker = int(ticker / 98)
                stringTicker = stringTicker % (len(string)*2)
                if(stringTicker >= len(string)):
                    screen.addstr(int((curses.LINES/2)-1),int((curses.COLS-len(string))/2)+stringTicker-len(string),string[stringTicker-len(string):])
                else:
                    screen.addstr(int((curses.LINES/2)-1),int((curses.COLS-len(string))/2),string[:stringTicker])
                    
                screen.refresh()

    return posts

def filterPost(post,subReddit):
    """
    Determines if the post should be included, based off of the filters. Blacklisted items are removed before 
    whitelisted items are added.
    """

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
            info = getPostInfo(post)

            try:
                headers += (formatString.enbox([f"{ticker}). {info["title"]}",info["author"],info["flair"],f"Posted in ({info["sub"]}), {info["age"]}"],curses.COLS,fancy=config.fancy_characters))
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


def getPostInfo(post):
    # Age
    age = "<NONE>"
    if(not post.created_utc == None):
        age = f"{formatString.formatAge(int(currentTimestamp()-post.created_utc),"ago")}"

    # Subreddit
    sub = formatString.removeNonAscii(post.subreddit.display_name)
    if(sub == None):
        sub = "<NO SUBREDDIT>"

    # Title
    title = formatString.removeNonAscii(post.title)
    if(title == None):
        title = "<NO TITLE>"
    
    # Flair
    flair = formatString.removeNonAscii(f"~Flair: {post.link_flair_text}~")
    if(flair == None):
        flair = "~<NO FLAIR>~"
    
    # Author
    author = post.author
    if(author == None):
        author = "[deleted]"
    else:
        author = f"[{author.name}]"
    
    return {"age":age,"sub":sub,"title":title,"flair":flair,"author":author}

def viewPost(post,screen,minCols=80,minLines=24):
    """
    Enters a viewing mode for a single post. Arrow keys can be used to move through and between posts.
    """
    resized = False
    info = getPostInfo(post)
    try:
        stringList = formatString.enbox([info["title"],info["author"],info["flair"],\
                                         f"Posted in ({info["sub"]}), {info["age"]}","%separator%",\
                                            formatString.removeNonAscii(post.selftext),"%separator%",post.url],\
                                                curses.COLS,fancy=config.fancy_characters)
    except AttributeError:
        stringList = ""
    
    
    lineNum = 0

    toolTip = scroll.ToolTip([formatString.combineStrings(f"<-- Line 1 -- >","(press q to quit)",curses.COLS,0,curses.COLS-18)])
    page = scroll.ScrollingList(screen,stringList,0,toolTip)
            
    while(True):
        toolTip.replace([formatString.combineStrings(f"<-- Line {lineNum + 1} -- >","(press q to quit)",curses.COLS,0,curses.COLS-18)])
        page.print()

        # char = screen.getch()
        char = eventListener(screen)
        if char == "timeout":
            continue
        
        # Exit viewing the post
        if char == "exit":
            return (0,resized)

        elif char == "resize":
            resized = True
            size = list(screen.getmaxyx())
            if(size[0] < minLines):
                size[0] = minLines
            if(size[1] < minCols):
                size[1] = minCols
            curses.resize_term(size[0],size[1])
            try:
                stringList = formatString.enbox([info["title"],info["author"],info["flair"],\
                                                f"Posted in ({info["sub"]}), {info["age"]}","%separator%",\
                                                    formatString.removeNonAscii(post.selftext),"%separator%",post.url],\
                                                        curses.COLS,fancy=config.fancy_characters)
            except AttributeError:
                stringList = ""
            page.updateStrings(screen,stringList,lineNum,toolTip) # Adds the headers list to the pagination controller
            temp = lineNum
            lineNum = page.scrollDown()
            if(not temp == lineNum):
                lineNum = page.scrollUp()

        # Scroll down in the post
        elif(char == "scrollDown"):
            lineNum = page.scrollDown()
        
        # Scroll up in the post
        elif(char == "scrollUp"):
            lineNum = page.scrollUp()

        # View previous post
        elif(char == "scrollLeft"):
            return (-1,resized)
        
        # View next post
        elif(char == "scrollRight"):
            return (1,resized)
        
        # Display help screen
        elif char == "help":
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
        elif char == "open":
            webbrowser.open_new_tab(post.url)

        # Copy url to clipboard
        elif char == "copy":
            copyToClipboard(post.url)
        
        # Open image, if present
        elif char == "image":
            response = requests.get(post.url) # Gets information from Internet
            if(response.status_code == 200): # Code 200 means information was sucessfully gathered
                try:
                    img = Image.open(BytesIO(response.content)) # Converts binary data to image
                    img.show() # Opens the image in default image viewer
                except  PIL.UnidentifiedImageError: # Typically thrown if the link was not an image.
                    pass
        
        # Open author's page
        elif char == "message":
            webbrowser.open_new_tab(f"https://www.reddit.com/user/{post.author.name}/")
        
        # Displays url of post
        elif char == "url":
            with open(config.link_output,"a") as f:
                f.write(f"{info["title"]}:\n")
                f.write(f"\t{post.url}\n")
                links = findURLs(post.selftext)
                for link in links:
                    f.write(f"\t{link}\n")

            screen.clear()
            screen.addstr(0,0,f"URL saved to {config.link_output}")
            screen.addstr(curses.LINES-1,curses.COLS-24,"(press any key to exit)")
            placeCursor(screen,x=0,y=curses.LINES-1)
            screen.refresh()
            char = screen.getch()

def findURLs(text):
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex, text)
    return [x[0] for x in url]

def placeCursor(screen,x,y):
    """
    Moves the cursor to the specified location
    """
    screen.addstr(y,x,"")


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



def eventListener(screen,characters=True,timeout=100):
    try:
        screen.timeout(timeout)
        char = screen.getch()
        if(characters == True):
            if char == ord('q'):
                screen.timeout(-1)
                return "exit"
            elif (char == curses.KEY_UP or char == ord('w')):
                screen.timeout(-1)
                return "scrollUp"
            elif (char == curses.KEY_DOWN or char == ord('s')):
                screen.timeout(-1)
                return "scrollDown"
            elif(char == curses.KEY_LEFT or char == ord('a')):
                screen.timeout(-1)
                return "scrollLeft"
            elif(char == curses.KEY_RIGHT or char == ord('d')):
                screen.timeout(-1)
                return "scrollRight"
            elif(char == ord('r')):
                screen.timeout(-1)
                return "refresh"
            elif char == ord('e'):
                screen.timeout(-1)
                return "enter"
            elif char == ord('h'):
                screen.timeout(-1)
                return "help"
            elif char == ord('o'):
                screen.timeout(-1)
                return "open"
            elif char == ord('c'):
                screen.timeout(-1)
                return "copy"
            elif char == ord('m'):
                screen.timeout(-1)
                return "message"
            elif char == ord('u'):
                screen.timeout(-1)
                return "url"
            elif char == ord('i'):
                screen.timeout(-1)
                return "image"
        if(char == curses.KEY_RESIZE):
            screen.timeout(-1)
            return "resize"
        else:
            screen.timeout(-1)
            return "timeout"
    except curses.error:
        return "timeout" 
    