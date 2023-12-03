import sys
import os
import pprint

import praw
import curses


from termcolor import colored, cprint

import functions
import config



# Read-only instance
reddit_read_only = praw.Reddit(client_id=config.client_id,         # your client id
                               client_secret=config.client_secret,      # your client secret
                               user_agent=config.client_secret)        # your user agent

subs = config.subReddits
numPostsPerSub = 5

desiredFlair = config.desiredFlair # Posts with at least one of these flairs will be kept
desiredTitle = config.desiredTitle # Posts with at least one of these titles will be kept
posts = []

postAgeLimit = 86400 * 2 # 2 days old

lowerAgeBound = 18
upperAgeBound = 23

numScraped = 0
for sub in subs:
    #print(f"{sub}:")
    subreddit = reddit_read_only.subreddit(sub)
    #pprint.pprint(vars(subreddit)) #prints all possible variables for subreddit


    currentTime = functions.currentTimestamp()
    for post in subreddit.new(limit = numPostsPerSub):
        numScraped += 1
        #print(post.subreddit_name_prefixed)
        needToSearchFlair = True;

        title = post.title
        for t in desiredTitle:
            if(title != None and t.lower() in title.lower()):
                # print(f"{colored(t,'red')} found in {title}")
                posts.append(post)
                needToSearchFlair = False;
                break

        if(needToSearchFlair):
            flair = post.link_flair_text
            for f in desiredFlair:
                if(flair != None and f.lower() in flair.lower()):
                    # print(f"{f} found in {flair}")
                    posts.append(post)
                    break



        #print(f"Created: ({int(currentTime-post.created_utc)}s ago)")
        #print(post.author_flair_text)

        
        # print()
    # print()
    print()

# Displays how many posts were searched through, and how many matched the criteria
print(f"Scraped {numScraped} post(s). Found {len(posts)} post(s) matching the criteria")

if (not posts): # If no posts were found matching the criteria
    
    # Lists all the flairs in desiredFlairs
    flairs = ""
    for flair in desiredFlair:
        flairs += flair + ", "
    flairs = flairs.removesuffix(", ")
    
    # Lists all the titles in desiredTitles
    titles = ""
    for title in desiredTitle:
        titles += title + ", "
    titles = titles.removesuffix(", ")

    # Prints information
    print(f"No posts were found containing the flairs: {flairs} or containing: {titles} in the title")
else:
    print()
    cprint("Posts matching filters:","yellow")
    
    currentSubreddit = ""
    ticker = 0
    for post in posts:
        if(post.subreddit_name_prefixed != currentSubreddit):
            currentSubreddit = post.subreddit_name_prefixed
            print()
            cprint(currentSubreddit,"green")
            print()
        ticker += 1
        print(f"{ticker}.")
        age = int(currentTime-post.created_utc)
        print(functions.enbox([post.title,post.link_flair_text,post.author.name,f"Created: {functions.formatAge(age)} ago"],80))
        # pprint.pprint(vars(post)) #prints all possible variables for post


while(True):
    response = input("Enter the number of a post above for more options: ")
    if(response.lower() == 'r'):
        print("Refresh command")
    else:
        try:
            response = int(response)
        except ValueError:
            print("Invalid input")
            continue

        if(response <= 0 or response > len(posts)):
            print("The value entered is out of bounds.")
            continue

        while(True):
            print("menu")
            menu = functions.getInput("Would you like to:\n1. Display post\n2. Copy post URL\n3. Display post URL\n4. Copy URL to message user",1,4,3)
            if(menu == -1):
                continue

            if(menu == 1):
                print(functions.enbox([posts[response-1].title,"%separator%",posts[response-1].selftext],80))
            elif(menu == 2):
                functions.copyToClipboard(posts[response-1].url)
            elif(menu == 3):
                print(posts[response-1].url)
            elif(menu == 4):
                print("Function to copy chat url")
            break

    break
      
screen = curses.initscr()
curses.noecho()
curses.cbreak()
screen.keypad(True)

try:
    numPosts = len(posts)
    postNum = 0
    while True:
        screen.clear()
        try:
            s = functions.enboxList([posts[postNum].title,"%separator%",posts[response-1].selftext],curses.COLS)
            num = 0
            for item in s:
                screen.addstr(num,0,str(item))
                num += 1
            screen.addstr(num,0,str(posts[postNum].url))
        except TypeError:
            screen.addstr(curses.LINES,0,"error")
            break

        char = screen.getch()
        
        if char == ord('q'):
            break
        elif char == curses.KEY_RIGHT:
            if(postNum < numPosts -1):
                postNum += 1
            else:
                postNum = numPosts - 1
        elif char == curses.KEY_LEFT:
            if(postNum > 0):
                postNum -= 1
            else:
                postNum = 0
        elif char == curses.KEY_UP:
            screen.addstr(0, 0, 'up   ')       
        elif char == curses.KEY_DOWN:
            screen.addstr(0, 0, 'down ')

finally:
    curses.nocbreak(); screen.keypad(0); curses.echo()
    curses.endwin()

