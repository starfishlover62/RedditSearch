import praw
import curses
import math

import configparser


import functions
import config
import dump
import constants
import formatString
import scroll

if(config.client_id == "" or config.client_secret == "" or config.user_agent == ""):
    print("Either the client id, client secret, or user agent are not specified. Please enter these values in config.py")
    exit()

# Read-only instance
reddit_read_only = praw.Reddit(client_id=config.client_id,          # your client id
                               client_secret=config.client_secret,  # your client secret
                               user_agent=config.user_agent)        # your user agent

searchesPath = config.searches_file

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
except FileNotFoundError:
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
                searchIndex = functions.getSearchNum(screen, searches)
                # If the user indicated that they wanted to quit the program in getSearchNum
                if(searchIndex == -1):
                    break

                else:
                    choosingSearches = False
                    currentTime = functions.currentTimestamp()
                    searchTime = searches[searchIndex].lastSearchTime # Gets the last time the specified search was performed

                # If search has never been performed
                if(searchTime == None):
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
                    screen.addstr(0,0,f"This search was last performed {formatString.formatAge(currentTime-searchTime)} ago.")
                    screen.addstr(1,0,"Press q to quit,")
                    screen.addstr(2,0,"y to perform the search any ways,")
                    screen.addstr(3,0,"or n to perform search on posts from the last week")
                    screen.refresh()

                    char = screen.getch()  
                    if char == ord('q'):
                        break
                    elif not char == ord('y'):
                        searches[searchIndex].lastSearchTime = math.floor(functions.currentTimestamp() - constants.DAY * 7)
                
                # Records the current timestamp before performing the search, then performs the search
                time = math.floor(functions.currentTimestamp())
                posts = functions.performSearch(reddit_read_only,searches[searchIndex],screen)

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

            # If no searches were found in the file, or the file does not exist
            else:
                screen.addstr(0,0,"No searches found. Press e to create a new search.")
                screen.addstr(1,0,"Alternatively, press q to exit, and edit the searches file")
                screen.addstr(2,0,f"The current searches file is {searchesPath}. Is this correct?")
                screen.addstr(3,0,"If not, edit the value of searches_file in config.py")

                char = screen.getch()  
                if char == ord('q'):
                    break

            # Clears screen after search choosing process
            screen.clear()
            screen.refresh()

        
        # Displays a single post
        elif(not browseMode):
            functions.viewPost(posts[postNum],screen)
            browseMode = True

        # Displays post headers for browsing
        else:
            # ticker = 0

            toolTip.replace([formatString.combineStrings(f"<-- Line {lineNum + 1} -- >","(press q to quit)",80,0,curses.COLS-18)])
            page.print()
            # for item in page.getLines():
            #     screen.addstr(ticker,0,f"{item}")
            #     ticker = ticker + 1
            
            
            screen.refresh()
            char = screen.getch()

            
            if char == ord('q'):
                break

            elif(char == curses.KEY_UP or char == ord('w')):
                lineNum = page.scrollUp()
            
            elif(char == curses.KEY_DOWN or char == ord('s')):
                lineNum = page.scrollDown()
     
            elif char == ord('e'):
                toolTip.replace([formatString.combineStrings(f"Enter a post number, then press enter:","(press q to exit)",80,0,curses.COLS-18)])
                page.print()
                functions.placeCursor(screen,x=40,y=curses.LINES-1)

                # ticker = 0
                # for item in page.getLines():
                #     screen.addstr(ticker,0,f"{item}")
                #     ticker = ticker + 1
                # screen.addstr(curses.LINES-1,curses.COLS-18,"(press q to exit)")
                # screen.addstr(curses.LINES-1,0,f"Enter a post number, then press enter: ")
                c = screen.getch() # Allows immediate exit if they press q
                if c == ord('q'):
                    continue

                # Otherwise update prompt
                # screen.addstr(curses.LINES-1,0,"")
                # screen.clrtoeol()
                # screen.refresh()
                toolTip.replace([formatString.combineStrings(f"Enter a post number, then press enter:","(press q to exit)",80,0,curses.COLS-18)])
                page.print()
                functions.placeCursor(screen,x=40,y=curses.LINES-1)
                # ticker = 0
                # for item in page.getLines():
                #     screen.addstr(ticker,0,f"{item}")
                #     ticker = ticker + 1
                # screen.addstr(curses.LINES-1,curses.COLS-18,"(enter q to exit)")
                # screen.addstr(curses.LINES-1,0,f"Enter a post number, then press enter: ")

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
                if(val >= 0 and val < numPosts):
                    browseMode = False
                    postNum = val

            
# Resets the terminal window for normal usage outside of the program
finally:
    curses.nocbreak(); screen.keypad(0); curses.echo()
    curses.endwin()
