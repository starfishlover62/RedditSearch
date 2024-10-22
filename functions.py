# Libraries
from io import BytesIO
import curses
import datetime
import math
import json
from PIL import Image
import PIL
import prawcore
import pyperclip
import re
import requests
from datetime import timezone
import webbrowser

# Provided
import search
from tree import searchTree
import formatString
import scroll
import dump
import page as p

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
    """
    Gathers all search objects that can be found in the JSONPath file
    """
    searches = []
    with open(JSONPath, "r") as read:
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
                subSearches.append(
                    search.SubredditSearch(
                        name, titleWL, titleBL, flairWL, flairBL, postWL, postBL
                    )
                )

            searches.append(
                search.Search(item["name"], item["lastSearchTime"], subSearches)
            )

    return searches


def getNumPosts(reddit, searchCriteria, numPosts=20):
    """
    reddit is the reddit instance, searchCriteria is a search object,
    and numPosts is the number of posts to fetch per subreddit in
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
    Displays a list of searches, and has the user select one to be performed.
    Also allows the user to create or delete searches.
    Return Values:
        -3 : Search was deleted (therefore save)
        -2 : Searches parameter is empty, or the user selected to create a new search
        -1 : User pressed q to quit
        >=0: The index of the searches list that was chosen
    """
    if searches is not None:
        # Defines the different tooltips
        toolTipType = "main"
        toolTipTypes = {
            "main": [
                scroll.Line("", 0, curses.COLS),
                scroll.Line(
                    [
                        "<-- Line %i -- >",
                        "(a) add, (e) select, (d) delete, (v) view, or (q) quit",
                    ],
                    [0, curses.COLS - 55],
                    curses.COLS,
                ),
            ],
            "press": [
                scroll.Line("", 0, curses.COLS),
                scroll.Line(
                    ["Enter a search number, then press enter: ", "(press q to exit)"],
                    [0, curses.COLS - 18],
                    curses.COLS,
                ),
            ],
            "enter": [
                scroll.Line("", 0, curses.COLS),
                scroll.Line(
                    ["Enter a search number, then press enter: ", "(enter q to exit)"],
                    [0, curses.COLS - 18],
                    curses.COLS,
                ),
            ],
        }
        toolTip = scroll.ToolTip(toolTipTypes[toolTipType])

        # Creates the scrolling list page
        ls = []
        ticker = 1
        for item in searches:
            ls.append(f"{ticker}. {item.name}")
            ticker = ticker + 1
        lineNum = 0
        page = scroll.ScrollingList(screen, ls, 0, toolTip)

        while True:
            # Updates tooltip and prints page to screen
            if not toolTipType == "main":
                toolTipType = "main"
                toolTip.replace(toolTipTypes[toolTipType])
            toolTip.updateVars(lineNum + 1, 1)
            page.print()

            # Gets single character input from user
            char = eventListener(screen)
            if char == "timeout":
                continue

            if char == "exit":  # Returns from function, signalling to quit program
                return -1

            elif char == "scrollUp":  # Scrolls up
                lineNum = page.scrollUp()
                continue

            elif char == "scrollDown":  # Scrolls down
                lineNum = page.scrollDown()
                continue

            elif char == "scrollLeft":  # 'a' was pressed. Adds a search
                return -2

            # User wants to perform, view, or delete a search
            elif char == "enter" or char == "scrollRight" or char == "view":
                toolTipType = "press"  # Indicates that user will press 'q' to exit
                text = ""
                # Adds text describing which of the three actions they are performing
                if char == "enter":
                    text = "~Selecting~"

                elif char == "view":
                    text = "~Viewing~"

                else:
                    text = "~Deleting~"

                # Updates tooltip and prints page
                prompt = toolTipTypes[toolTipType]
                prompt[0] = scroll.Line(text, 0, curses.COLS)
                toolTip.update(prompt)
                page.print()

                # Moves cursor to end of prompt
                placeCursor(screen, x=41, y=curses.LINES - 1)

                # Gets a single character from user
                c = screen.getch()  # Allows immediate exit if they press q
                if c == ord("q"):
                    continue

                toolTipType = "enter"  # User has to enter 'q' to exit
                prompt = toolTipTypes[toolTipType]
                prompt[0] = scroll.Line(text, 0, curses.COLS)

                # Gets multi-character input from the user
                string = getInput(
                    prompt=prompt,
                    screen=screen,
                    page=page,
                    tooltip=toolTip,
                    unget=c,
                    col=41,
                )

                # Attempts to convert their input to an integer
                val = 0
                try:
                    val = int(string)
                except ValueError:
                    continue

                val -= 1  # Offsets input, so it is an index
                if val >= 0 and val < len(
                    searches
                ):  # The val must be a valid index in the list of searches
                    if char == "scrollRight":  # 'd' key for delete
                        del searches[val]
                        return -3
                    elif char == "view":  # Views search
                        viewSearch(screen, searches[val])
                    else:  # Selects search
                        return val
    else:
        return -2


def viewSearch(screen, search):
    """
    Enters a screen with a tree depicting the specified search is displayed
    """

    if search is not None:
        view = searchTree(search, curses.COLS, config.fancy_characters)
        lineNum = 0
        toolTipType = "main"
        toolTipTypes = {
            "main": [
                scroll.Line("", 0, curses.COLS),
                scroll.Line(
                    ["<-- Line %i -- >", "press (q) to exit"],
                    [0, curses.COLS - 18],
                    curses.COLS,
                ),
            ]
        }
        toolTip = scroll.ToolTip(toolTipTypes[toolTipType])
        page = scroll.ScrollingList(screen, view, lineNum, toolTip)
        while True:
            # Changes toolTip if necessary
            if not toolTipType == "main":
                toolTipType = "main"
                toolTip.replace(toolTipTypes[toolTipType])

            # Updates line number and prints page
            toolTip.updateVars([lineNum + 1], 1)
            page.print()

            # Gets input from user
            viewChar = eventListener(screen)
            if viewChar == "exit":  # Returns from function, signalling to quit program
                break

            elif viewChar == "scrollUp":  # Scrolls up
                lineNum = page.scrollUp()
                continue

            elif viewChar == "scrollDown":  # Scrolls down
                lineNum = page.scrollDown()
                continue


def getInput(screen, page, tooltip, prompt=None, unget=None, row=None, col=None):
    """
    Gets multi-character input from the user and returns it.
    """
    if prompt is not None: # Display the prompt for input that was specified
        if isinstance(prompt, list):
            tooltip.replace(prompt)
        else:
            tooltip.replace([prompt])
    page.print()

    # Places the curser at the end of the prompt, or where specified by row and col
    if row is None:
        if col is None:
            placeCursor(screen, x=(len(prompt) + 1), y=curses.LINES - 1)
        else:
            placeCursor(screen, x=col, y=curses.LINES - 1)
    else:
        if col is None:
            placeCursor(screen, x=(len(prompt) + 1), y=row)
        else:
            placeCursor(screen, x=col, y=row)

    # Gets input
    curses.echo()  # Displays what they type
    curses.nocbreak()  # Requires that they press enter
    if unget is not None:
        curses.ungetch(unget)
    string = screen.getstr().decode("ASCII")  # Their input

    # Undo displaying input and requiring enter be pressed
    curses.noecho()
    curses.cbreak()

    return string


def createSearch(screen):
    """
    Creates a search object found in search.py. Prompts user to input data to create this object
    """

    # Clears out the screen to prepare it for creating the search
    screen.clear()
    screen.refresh()

    stringList = []
    questions = [
        "Name of search:",
        "Subreddit:",
        "Whitelisted title:",
        "Blacklisted title:",
        "Whitelisted flair:",
        "Blacklisted flair:",
        "Whitelisted word in post:",
        "Blacklisted word in post:",
    ]
    questionIndex = 0  # The current index of questions array
    returnSearch = search.Search()
    lineNum = 0
    quit = False
    toolTip = scroll.ToolTip(
        [
            questions[questionIndex],
            formatString.combineStrings(
                f"<-- Line {lineNum + 1} -- >",
                "(press q to quit)",
                curses.COLS,
                0,
                curses.COLS - 18,
            ),
        ]
    )
    page = scroll.ScrollingList(screen, stringList, 0, toolTip)
    temp = []

    while True:
        if quit:
            break

        page.print()
        if questionIndex == 0:
            # Gets search name
            prompt = questions[questionIndex]
            string = getInput(prompt=prompt, screen=screen, page=page, tooltip=toolTip)
            returnSearch.update(name=string)
            questionIndex = questionIndex + 1
            stringList = searchTree(returnSearch, curses.COLS, config.fancy_characters)
            page.updateStrings(screen, stringList, 0, toolTip)

        elif questionIndex == 1:
            # Gets first subreddit name
            prompt = questions[questionIndex]
            string = getInput(prompt=prompt, screen=screen, page=page, tooltip=toolTip)
            if (
                returnSearch.subreddits is None
            ):  # If this is the first sub search, set subreddits value
                returnSearch.update(subreddits=[search.SubredditSearch()])
            else:  # Otherwise, append a new subreddit search
                returnSearch.update(
                    subreddits=returnSearch.subreddits.append(search.SubredditSearch())
                )
            returnSearch.subreddits[-1].update(sub=string)
            questionIndex = questionIndex + 1
            stringList = searchTree(returnSearch, curses.COLS, config.fancy_characters)
            page.updateStrings(screen, stringList, 0, toolTip)

        else:  # For all questions except name of search
            while True:
                prompt = f"Add a {questions[questionIndex]} (y/n):"
                toolTip.replace([prompt])
                page.print()
                placeCursor(screen, x=(len(prompt) + 1), y=curses.LINES - 1)
                c = screen.getch()  # Gets the character they type

                # User entered n. Moves on to next question. If this was the last question, asks
                # user if they want to add another subreddit.
                if c == ord("n"):
                    questionIndex = questionIndex + 1
                    temp = []
                    if questionIndex >= len(questions):
                        prompt = "Add another Subreddit (y/n):"
                        toolTip.replace([prompt])
                        page.print()
                        placeCursor(screen, x=(len(prompt) + 1), y=curses.LINES - 1)
                        answer = screen.getch()
                        if answer == ord("n"):
                            quit = True
                            break
                        else:
                            questionIndex = 1
                            break
                elif c == ord("y"):  # Otherwise
                    # Update prompt to remove option to quit
                    prompt = f"{questions[questionIndex]}"
                    string = getInput(
                        prompt=prompt, screen=screen, page=page, tooltip=toolTip
                    )
                    if not string.strip() == "":
                        temp.append(string)
                        if questionIndex == 2:
                            returnSearch.subreddits[-1].update(titleWL=temp)
                        elif questionIndex == 3:
                            returnSearch.subreddits[-1].update(titleBL=temp)
                        elif questionIndex == 4:
                            returnSearch.subreddits[-1].update(flairWL=temp)
                        elif questionIndex == 5:
                            returnSearch.subreddits[-1].update(flairBL=temp)
                        elif questionIndex == 6:
                            returnSearch.subreddits[-1].update(postWL=temp)
                        elif questionIndex == 7:
                            returnSearch.subreddits[-1].update(postBL=temp)
                        stringList = searchTree(
                            returnSearch, curses.COLS, config.fancy_characters
                        )
                        page.updateStrings(screen, stringList, 0, toolTip)

    return returnSearch


def completeSearch(reddit,searches,searchIndex,posts=None,screen=None,minCols=80,minLines=24,save=True,searchesPath=None):
    """
    Calls performSearch and saves the search timestamp to the searches file. Saving the timestamp can be disabled with the save parameter.
    """
    time = math.floor(currentTimestamp())
    posts = posts + performSearch(reddit,searches[searchIndex],screen,minCols,minLines)
    posts = sortPosts(posts)
    searches[
                searchIndex
            ].lastSearchTime = (
                time  # Sets the search time in the search variable
            )
    if save and searchesPath is not None:
        dump.saveSearches(
            searches, searchesPath
        )  # Writes the search variable to the file
    return posts


def performSearch(reddit,search,screen=None,minCols=80,minLines=24):
    """
    Gathers posts that meat the search object criteria, using the reddit object.
    If a screen object is provided, displays a simple search in progress message.
    """
    posts = []
    ticker = 0
    if screen is not None:
        screen.clear()
        screen.refresh()
        string = "Searching..."
        stringTicker = 0
    for sub in search.subreddits:
        subreddit = reddit.subreddit(sub.name)
        for post in subreddit.new(limit=None): # Gets all posts in the current subreddit
            if post.created_utc is None:
                continue
            if post.created_utc < search.lastSearchTime: # continues until it finds a post older than the last search time
                break
            else:
                if filterPost(post, sub): # If post meets the specified filters, append it to the list
                    posts.append(post)
            ticker = ticker + 1

            if screen is not None:
                resize = eventListener(screen, characters=False, timeout=5) # Gets input from user. Only listens for terminal resizing

                if resize == "resize": # Resizes content if terminal was resized
                    size = list(screen.getmaxyx())
                    if size[0] < minLines:
                        size[0] = minLines
                    if size[1] < minCols:
                        size[1] = minCols
                    curses.resize_term(size[0], size[1])

                screen.clear()
                waitMessage = "(This may take a while, depending on time since the search was last performed)"
                # Prints the wait message at the bottom of the screen
                screen.addstr(
                    curses.LINES - 1,
                    int((curses.COLS - len(waitMessage)) / 2),
                    waitMessage,
                )

                # Displays searching... in the middle of the screen, with an animation.
                # starts with s, and adds characters after that, then once it reaches the end of the string,
                # starts removing characters from the beginning of the string. Once
                # no characters remain, starts over

                stringTicker = int(ticker / 98)
                stringTicker = stringTicker % (len(string) * 2)
                if stringTicker >= len(string):
                    screen.addstr(
                        int((curses.LINES / 2) - 1),
                        int((curses.COLS - len(string)) / 2)
                        + stringTicker
                        - len(string),
                        string[stringTicker - len(string) :],
                    )
                else:
                    screen.addstr(
                        int((curses.LINES / 2) - 1),
                        int((curses.COLS - len(string)) / 2),
                        string[:stringTicker],
                    )

                screen.refresh()

    return posts


def filterPost(post, subSearch):
    """
    Determines if the post should be included, based off of the filters. Blacklisted items are removed before
    whitelisted items are added.
    """

    # Easier reference to post contents
    title = post.title
    flair = post.link_flair_text
    content = post.selftext

    # Check blacklists

    if title is not None and subSearch.titleBL is not None:
        for t in subSearch.titleBL:
            if t.lower() in title.lower():
                return False

    if flair is not None and subSearch.flairBL is not None:
        for f in subSearch.flairBL:
            if f.lower() in flair.lower():
                return False

    if content is not None and subSearch.postBL is not None:
        for c in subSearch.postBL:
            if c.lower() in content.lower():
                return False

    # Check whitelists

    if title is not None and subSearch.titleWL is not None:
        for t in subSearch.titleWL:
            if t.lower() in title.lower():
                return True

    if flair is not None and subSearch.flairWL is not None:
        for f in subSearch.flairWL:
            if f.lower() in flair.lower():
                return True

    if content is not None and subSearch.postWL is not None:
        for c in subSearch.postWL:
            if c.lower() in content.lower():
                return True

    return False


def getHeaders(posts):
    """
    Formats and returns post header information. This includes: subreddit, title, flair, author, and age
    """
    headers = []
    ticker = 1
    if posts is not None:
        for post in posts: # Loops through each post
            info = getPostInfo(post) # Gets the information about the post

            try:
                headers += formatString.enbox( # Enboxes and stores the results
                    [
                        f"{ticker}). {info["title"]}",
                        info["author"],
                        info["flair"],
                        f"Posted in ({info["sub"]}), {info["age"]}",
                    ],
                    curses.COLS,
                    fancy=config.fancy_characters,
                )
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
    """
    Returns basic information about a post, including age, subreddit it was posted into, title, flair, and author
    """
    # Age
    age = "<NONE>"
    if post.created_utc is not None:
        age = (
            f"{formatString.formatAge(int(currentTimestamp()-post.created_utc),"ago")}"
        )

    # Subreddit
    sub = formatString.removeNonAscii(post.subreddit.display_name)
    if sub is None:
        sub = "<NO SUBREDDIT>"

    # Title
    title = formatString.removeNonAscii(post.title)
    if title is None:
        title = "<NO TITLE>"

    # Flair
    flair = formatString.removeNonAscii(f"~Flair: {post.link_flair_text}~")
    if flair is None:
        flair = "~<NO FLAIR>~"

    # Author
    author = post.author
    if author is None:
        author = "[deleted]"
    else:
        author = f"[{author.name}]"

    return {"age": age, "sub": sub, "title": title, "flair": flair, "author": author}


def viewPostUpdate(content):
    """
    Used by viewPost to re-enbox its content. Necessary for its resize function
    """
    return formatString.enbox(
                    content,
                    curses.COLS,
                    fancy=config.fancy_characters,
                )


def viewPost(post, screen, minCols=80, minLines=24):
    """
    Enters a viewing mode for a single post. Arrow keys can be used to move through and between posts.
    """
    resized = False # Stores whether the terminal was resized while in this function.

    # Gets information about the post, and puts it into the form for viewing
    info = getPostInfo(post)
    content = [
        info["title"],
        info["author"],
        info["flair"],
        f"Posted in ({info["sub"]}), {info["age"]}",
        "%separator%",
        formatString.removeNonAscii(post.selftext),
        "%separator%",
        post.url,
    ]
    try:
        stringList = viewPostUpdate(content) # Enboxes the content
    except AttributeError:
        stringList = ""


    # Sets the tooltip
    toolTipType = "main"
    toolTipTypes = {
        "main": [
            scroll.Line(
                ["<-- Line %i/%i -- >", "press (q) to exit"],
                [0, curses.COLS - 18],
                curses.COLS,
            )
        ]
    }
    toolTip = scroll.ToolTip(toolTipTypes[toolTipType])

    # Creates a page with the content and tooltip
    page = scroll.ScrollingList(screen, stringList, 0, toolTip)
    viewPage = p.Page(screen=screen,scrollingList=page,tooltip=toolTip,tooltipTypes=toolTipTypes,onUpdate=viewPostUpdate,content=content,minRows=minLines,minCols=minCols)
    viewPage.switchTooltip("main")

    skip = False # Stores whether gathering a character should be done. Used when exiting from the help screen

    while True:
        if not skip: # Refreshes the tooltip's line number and gets input
            viewPage.refreshTooltip("main",[viewPage.scrollingList.currentLine + 1, page.maxLine + 1], 0,print=True)
            input = eventListener(screen)
        skip = False

        match input:
            # User didn't enter anything within the window, repeats loop
            case "timeout":
                continue

            # Exits function
            case "exit":
                return (0,resized)
            
            # Terminal was resized
            case "resize":
                viewPage.resize()
                resized=True

            # Scrolls up through the content list
            case "scrollUp":
                page.scrollUp()

            # Scrolls to line 0 of the content
            case "scrollTop":
                page.scrollTop()

            # Scrolls down through the content list
            case "scrollDown":
                page.scrollDown()

            # Scrolls to the last line of the content list
            case "scrollBottom":
                page.scrollBottom()

            # Returns value specifying to view previous post
            case "scrollLeft":
                return (-1, resized)
            
            # Returns value specifying to view next post
            case "scrollRight":
                return (1, resized)
            
            # Displays a help screen
            case "help": 
                screen.clear()
                helpPage = scroll.ScrollingList(
                    screen,
                    [
                        "Press the button in () to execute its command",
                        "(w) or (up arrow) scroll up",
                        "(s) or (down arrow) scroll down",
                        "(a) or (left arrow) view previous post",
                        "(d) or (right arrow) view next post",
                        "(h) Displays this menu",
                        "(i) If post is an image, opens image",
                        "(o) Opens the post in a new tab of the default web browser",
                        "(c) Copies the post url to the clipboard",
                        "(u) Prints the post urls to a file. (link_output in config.py)",
                        "(m) Opens the author's page in a new tab of the default web browser",
                        "Press any key to exit this screen",
                    ],
                    0,
                    None,
                )
                placeCursor(screen, x=0, y=curses.LINES - 1)
                helpPage.print()
                while True:
                    char = eventListener(
                        screen, anyChar=True
                    )  # Screen stays up until user does some action
                    if not (char == "timeout"):
                        if char == "resize":
                            skip = True
                        else:
                            skip = False
                        break
            # Open post in web browser
            case "open":
                webbrowser.open_new_tab(post.url)

            # Copy url to clipboard
            case "copy":
                copyToClipboard(post.url)

            # Open image, if present
            case "image":
                response = requests.get(post.url)  # Gets information from Internet
                if (
                    response.status_code == 200
                ):  # Code 200 means information was sucessfully gathered
                    try:
                        img = Image.open(
                            BytesIO(response.content)
                        )  # Converts binary data to image
                        img.show()  # Opens the image in default image viewer
                    except (
                        PIL.UnidentifiedImageError
                    ):  # Typically thrown if the link was not an image.
                        pass

            # Open author's page
            case "message":
                webbrowser.open_new_tab(f"https://www.reddit.com/user/{post.author.name}/")

            # Displays url of post
            case "url":
                links = findURLs(post.selftext)
                with open(config.link_output, "a") as f:
                    f.write(f"{info["title"]}:\n")
                    f.write(f"\t{post.url}\n")
                    for link in links:
                        f.write(f"\t{link}\n")

                screen.clear()
                screen.addstr(0, 0, f"URLs saved to {config.link_output}")
                screen.addstr(curses.LINES - 1, curses.COLS - 24, "(press any key to exit)")
                placeCursor(screen, x=0, y=curses.LINES - 1)
                screen.refresh()
                while True:
                    char = eventListener(
                        screen, anyChar=True
                    )  # Screen stays up until user does some action
                    if not (char == "timeout"):
                        if char == "resize":
                            skip = True
                        else:
                            skip = False
                        break


def findURLs(text):
    """
    Returns a list of all the valid urls in the text
    """
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex, text)
    return [x[0] for x in url]


def placeCursor(screen, x, y):
    """
    Moves the cursor to the specified location
    """
    screen.addstr(y, x, "")


def isValidSubreddit(userReddit, name):
    """
    Pulls a single post from the subreddit specified in name, using the praw reddit instance userReddit.  
    Returns 1 if sub is valid, -1 if it does not exist or has been banned, or -2 if it is private
    """
    try:
        for submission in userReddit.subreddit(name).new(limit=1):
            s = submission.id # Attempts to pull a submission from the subreddit
    except (
        prawcore.exceptions.NotFound,
        prawcore.exceptions.Redirect,
        prawcore.exceptions.BadRequest,
        AttributeError,
    ):  # Errors that arise when the subreddit does not exist
        return -1
    except prawcore.exceptions.Forbidden:
        return -2
    return 1


def eventListener(screen, characters=True, anyChar=False, timeout=100):
    """
    Waits for a single character input from the user.  
    characters: is whether it will listen for characters for input, or just terminal resizing.   
    anyChar: will return any for any character input.   
    timeout: is the number of milliseconds the function will wait for a response before returning timeout
    """
    try:
        screen.timeout(timeout)
        char = screen.getch()
        if characters:
            if char == ord("q"):
                screen.timeout(-1)
                return "exit"
            elif char == curses.KEY_UP or char == ord("w"):
                screen.timeout(-1)
                return "scrollUp"
            elif char == curses.KEY_DOWN or char == ord("s"):
                screen.timeout(-1)
                return "scrollDown"
            elif char == curses.KEY_LEFT or char == ord("a"):
                screen.timeout(-1)
                return "scrollLeft"
            elif char == curses.KEY_RIGHT or char == ord("d"):
                screen.timeout(-1)
                return "scrollRight"
            elif char == ord("t"):
                screen.timeout(-1)
                return "scrollTop"
            elif char == ord("b"):
                screen.timeout(-1)
                return "scrollBottom"
            elif char == ord("r"):
                screen.timeout(-1)
                return "refresh"
            elif char == ord("e"):
                screen.timeout(-1)
                return "enter"
            elif char == ord("v"):
                screen.timeout(-1)
                return "view"
            elif char == ord("h"):
                screen.timeout(-1)
                return "help"
            elif char == ord("o"):
                screen.timeout(-1)
                return "open"
            elif char == ord("c"):
                screen.timeout(-1)
                return "copy"
            elif char == ord("m"):
                screen.timeout(-1)
                return "message"
            elif char == ord("u"):
                screen.timeout(-1)
                return "url"
            elif char == ord("i"):
                screen.timeout(-1)
                return "image"
        if char == curses.KEY_RESIZE:
            screen.timeout(-1)
            return "resize"
        else:
            if anyChar:
                if char == -1:
                    screen.timeout(-1)
                    return "timeout"
                else:
                    screen.timeout(-1)
                    return "any"
            else:
                screen.timeout(-1)
                return "timeout"
    except curses.error:
        return "timeout"
