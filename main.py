import praw
import prawcore
import curses
import math
import argparse

import configparser


import functions
import config
import dump
import constants
import formatString
import scroll
import json.decoder

parser = argparse.ArgumentParser(description="Gathers posts on Reddit that meets specific criteria. Note that the program can be run without any command-line options")
parser.add_argument("-n", "--name", metavar="NAME", help = "Name of the search to be performed. Case-sensitive")
args = vars(parser.parse_args())


# Checks that the config options are set
if(config.client_id == ""):
    print("Please specify a client id in config.py")
    exit(1)
if(config.client_secret == ""):
    print("Please specify a client secret in config.py")
    exit(1)
if(config.user_agent == ""):
    print("Please specify a user agent in config.py")
    exit(1)
    

# Read-only instance
reddit_read_only = praw.Reddit(client_id=config.client_id,          # your client id
                               client_secret=config.client_secret,  # your client secret
                               user_agent=config.user_agent)        # your user agent

# Pulls a post to test that config options are properly set
try:
    for post in reddit_read_only.subreddit("reddit").new(limit=1):
        post = post
except prawcore.exceptions.ResponseException:
    print("Bad HTTP Response")
    print("Please check that the client id, secret, and user agent are properly configured in config.py")
    exit(1)

# Ensures that the path to the searches file has been set
searchesPath = config.searches_file
if(searchesPath == ""):
    print("Please specify a path to the searches file in config.py")
    exit(1)

# Initialization work
screen = curses.initscr()
curses.noecho() # Does not display what user types
curses.cbreak() # User does not have to press enter for the input buffer to be read
screen.keypad(True) # Converts keys like arrow keys to a specific value

# Ensures the terminal is large enough to properly display (Can probably be changed in the future to be smaller)
minTermLines = 24
minTermCols = 80
if(curses.LINES < minTermLines or curses.COLS < minTermCols):
    curses.nocbreak(); screen.keypad(0); curses.echo()
    curses.endwin()
    print(f"The current terminal size {curses.LINES}x{curses.COLS} is too small. The minimum size supported is {minTermLines}x{minTermCols}")
    exit()

searches = []
try:
    searches = functions.getSearches(searchesPath)
except(FileNotFoundError, json.decoder.JSONDecodeError):
    searches = []

numPosts = 0 # Number of posts found meeting criteria
postNum = 0 # Number of the post to be viewed in full
lineNum = 0 # Current line number for paginating through post browsing
browseMode = True # True if browsing through posts, false if reading a specific post
choosingSearches = True # True if the user has yet to choose a search to perform, false if the search has been chosen
searchIndex = 0 # Index of the search to be performed
posts = [] # List of all the posts meeting criteria


page = scroll.ScrollingList(screen,[""])
toolTip = scroll.ToolTip(formatString.combineStrings("<-- Line 1 -- >","(press q to quit)",curses.COLS,0,curses.COLS-18))




      

try:
    
    

    while True:
        screen.clear()

        # If the user still has to choose a search to perform
        if(choosingSearches):
            # If searches were found in the search file
            if(searches):
                if(args["name"]):
                    valid = False
                    for item in range(len(searches)):
                        if (searches[item].name == args["name"]):
                            valid = True
                            searchIndex = item
                            break
                    if(not valid):
                        curses.nocbreak(); screen.keypad(0); curses.echo()
                        curses.endwin()
                        print(f"No search by the name of {args["name"]} exists\nThe following are valid searches:")
                        for item in searches:
                            print(f"\t{item.name}")
                        exit(1)

                else:
                    searchIndex = functions.getSearchNum(screen, searches)
            else: # If no searches were found in the file, or the file does not exist
                screen.addstr(0,0,"No searches found at the current searches file:")
                screen.addstr(1,4,f"{searchesPath}")
                screen.addstr(2,0,"If this is not the correct path, edit the value of 'searches_file' in config.py.")
                screen.addstr(3,0,f"Press q to quit the program.")
                screen.addstr(4,0,f"Press any other key to create a new search in the above search file")
                char = screen.getch()  
                if char == ord('q'):
                    break
                else:
                    searchIndex = -2

            screen.clear()
            screen.refresh()
            # If the user indicated that they wanted to quit the program in getSearchNum
            if(searchIndex == -1):
                break
            elif(searchIndex == -2):
                newSearch = functions.createSearch(screen)
                searches.append(newSearch)
                dump.saveSearches(searches,searchesPath)
                continue
            elif(searchIndex == -3):
                dump.saveSearches(searches,searchesPath)
                continue

            else:
                choosingSearches = False
                currentTime = functions.currentTimestamp()
                searchTime = searches[searchIndex].lastSearchTime # Gets the last time the specified search was performed

            # If search has never been performed
            if(searchTime == None or searchTime == 0):
                screen.clear()
                screen.addstr(0,0,"This search has never been performed. Gathering posts from the last week.")
                screen.addstr(1,0,"Press q to quit or any other key to continue")
                screen.refresh()
                char = screen.getch()  
                if char == ord('q'):
                    break
                searches[searchIndex].lastSearchTime = math.floor(functions.currentTimestamp() - constants.DAY * 7)

            # If search was last performed over a week ago
            elif(currentTime - searchTime > constants.DAY * 7):
                screen.clear()
                screen.addstr(0,0,f"This search was last performed {formatString.formatAge(currentTime-searchTime,"ago.")}")
                screen.addstr(1,0,"Press q to quit,")
                screen.addstr(2,0,"y to perform the search anyways,")
                screen.addstr(3,0,"or n to perform search on posts from the last week")
                screen.refresh()

                char = screen.getch()  
                if char == ord('q'):
                    break
                elif not char == ord('y'):
                    searches[searchIndex].lastSearchTime = math.floor(functions.currentTimestamp() - constants.DAY * 7)
            
            # Records the current timestamp before performing the search, then performs the search
            time = math.floor(functions.currentTimestamp())
            for sub in searches[searchIndex].subreddits:
                status = functions.isValidSubreddit(reddit_read_only,sub.name)
                if(status == -1):
                    curses.nocbreak(); screen.keypad(0); curses.echo()
                    curses.endwin()
                    print(f'Subreddit ({sub.name}) does not exist or has been banned')
                    exit(1)
                elif(status == -2):
                    curses.nocbreak(); screen.keypad(0); curses.echo()
                    curses.endwin()
                    print(f'Subreddit ({sub.name}) is private or under quarantine')
                    exit(1)
            posts = functions.performSearch(reddit_read_only,searches[searchIndex],screen)
            posts = functions.sortPosts(posts)

            # If no posts matched the criteria
            if(len(posts) <= 0):
                screen.clear()
                screen.addstr(0,0,"No posts found")
                screen.addstr(curses.LINES-1,0,"Press any key to exit")
                screen.getch()
                screen.refresh()
                searches[searchIndex].lastSearchTime = time
                dump.saveSearches(searches,searchesPath)
                break

            # If at least one post matching the criteria was found
            else:
                headers = functions.getHeaders(posts) # Returns the boxes containing post info
                numPosts = len(posts)
                page.updateStrings(screen,headers,0,toolTip) # Adds the headers list to the pagination controller
                searches[searchIndex].lastSearchTime = time # Sets the search time in the searc variable
                dump.saveSearches(searches,searchesPath) # Writes the search variable to the file

           

            # Clears screen after search choosing process
            screen.clear()
            screen.refresh()

        
        # Displays a single post
        elif(not browseMode):
            next = functions.viewPost(posts[postNum],screen)
            if(next == -1): # The user wants to view previous post
                if(postNum - 1 >= 0):
                    postNum = postNum - 1
            elif(next == 1): # The user wants to view next post
                if((postNum + 1) < len(posts)):
                    postNum = postNum + 1
            else: # User wanted to exit viewPost
                browseMode = True

        # Displays post headers for browsing
        else:
            # Updates the tooltip, and prints the headers to the screen
            toolTip.replace([formatString.combineStrings(f"<-- Line {lineNum + 1} -- >","(press e to view a post or q to quit)",80,0,curses.COLS-38)])
            page.print()           
            
            # Gets input from the user
            char = screen.getch()

            # Quits the program
            if char == ord('q'):
                break

            # Scrolls up if allowed
            elif(char == curses.KEY_UP or char == ord('w')):
                lineNum = page.scrollUp()
            
            # Scrolls down if allowed
            elif(char == curses.KEY_DOWN or char == ord('s')):
                lineNum = page.scrollDown()

            # Refreshes the search, gathering any new submissions that have been posted
            elif(char == ord('r')):
                # Records the current timestamp before performing the search, then performs the search
                time = math.floor(functions.currentTimestamp())
                posts = posts + functions.performSearch(reddit_read_only,searches[searchIndex],screen)
                posts = functions.sortPosts(posts)
                headers = functions.getHeaders(posts) # Returns the boxes containing post info
                numPosts = len(posts)
                page.updateStrings(screen,headers,0,toolTip) # Adds the headers list to the pagination controller
                searches[searchIndex].lastSearchTime = time # Sets the search time in the searc variable
                dump.saveSearches(searches,searchesPath) # Writes the search variable to the file
     
            # Allows the user to input a post number
            elif char == ord('e'):
                # Updates the tooltip and places the cursor for input
                toolTip.replace([formatString.combineStrings(f"Enter a post number (1-{len(posts)}), then press enter:","(press q to exit)",80,0,curses.COLS-18)])
                page.print()
                functions.placeCursor(screen,x=48,y=curses.LINES-1)
                c = screen.getch() # Gets the character they type
                if c == ord('q'): # Immediately exits if they pressed q
                    continue

                else: # Otherwise
                    # Update prompt to tell them to 'enter q" instead of 'press q"
                    toolTip.replace([formatString.combineStrings(f"Enter a post number (1-{len(posts)}), then press enter:","(enter q to exit)",80,0,curses.COLS-18)])
                    page.print()
                    functions.placeCursor(screen,x=48,y=curses.LINES-1)

                    # Gets input
                    curses.echo() # Displays what they type
                    curses.nocbreak() # Requires that they press enter
                    curses.ungetch(c) # Adds the first character back to the buffer
                    string = screen.getstr() # Their input

                    # Undo displaying input and requiring enter be pressed
                    curses.noecho()
                    curses.cbreak()

                    # Attempts to convert their input into an integer.
                    val = 0
                    try:
                        val = int(string)
                    except ValueError:
                        continue

                    # If the input was an integer, converts to an index, and checks if it is within the bounds of post numbers
                    val -= 1
                    if(val >= 0 and val < numPosts):
                        browseMode = False # Will display post in full on next iteration
                        postNum = val # Index of the post to be viewed

            
# Resets the terminal window for normal usage outside of the program
finally:
    curses.nocbreak(); screen.keypad(0); curses.echo()
    curses.endwin()
