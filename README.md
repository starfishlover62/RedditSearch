# RedditScraper

*** INCOMPLETE ***

Scrapes subreddits and filters by flair or title


Currently only tested on linux, however it should work on Windows.

Tested Python versions: 3.12.3

Utilizes ncurses library, which must be installed if it isn't already.


# Installation


* Clone the repository locally or download and extract the zipped folder.
* Open config.py
* Navigate to https://old.reddit.com/prefs/apps/
    * If you have an account, login, if not, create an account
    * Click on "are you a developer? Create an app..."
    * Enter "better-search" for the name of the app
    * Enter "Searches multiple subreddits and filters results" for the description
    * Enter "http://localhost:8080" for the redirect uri
    * Click on "create app"
    * In the top left will be a picture of a question mark inside of a diamond
        * To the right of this should be "better-search" and then "personal use script" below that. Below this will be a string of random characters. This is your client id. Navigate to config.py and replace the text that says "your_client_id" with this string.
        * Back on the website, below the client id, should be a section labelled "secret" copy this and replay "your_client_secret" with it.
        * Finally, within the user agent section on config.py, replace your_username with your username. If you have forgotten what it is, it should be located in the top right of the reddit website, to the left of a letter icon.
    * It is now safe to close the browser window.
* (Optional) the path in searches_file can be edited to specify a different file to store saved searches
* (Optional) the path in link_output can be edited to specify a different file to save urls too. See the Results - Interacting section for more information about this.
* (Optional) If you prefer to not use fancy characters, or your computer does not support them, change the value of fancy_characters to false. This will force the app to use only ASCII characters.

* Linux
* Windows
* Mac


## LINUX
1. Install Python 3 and PIP
    * For ubuntu or Debian based systems:
        ```sudo apt install python3 python3-pip```
2. Install required libraries. They can be found in requirements.txt (Run `pip install -r requirements.txt`)
3. For clipboard functionality, either xclip or xsel is needed. Check if they are installed with ```sudo apt show xclip``` or `sudo apt show xsel` See the pyperclip documentation (https://pypi.org/project/pyperclip/) for more information.


# Usage

The program can be started by executing the following command:
    `python3 main.py`

The next screen should be a list of names of searches. If the screen states that no searches were found, double check the path to the searches file in config.py. Is that the correct path? If it is, press any key in the terminal to start the process of creating a new search. If it is not, edit the value in config.py, press 'q' in the terminal, and relaunch the program.

## Creating a search

1. On the search creation screen, you will first be prompted to enter the name of the search. This will be the name referenced when you go to perform the search, so choose something relevant and descriptive.
2. You will then be prompted to enter the name of a subreddit. This is the subreddit that the rules you will define next will be applied to.
3. Next comes the whitelisted titles. You can add as many different words or phrases. Simply press y to add a new white listed title. Then enter the word or phrase then press enter. You will be brought back to the same prompt asking for a whitelist title. Continue this loop until you are finished, then press n to move on.
4. The same process continues, but this time with the blacklisted titles.
5. Repeat this process for the whitelisted flair, blacklisted flair, whitelisted word, and blacklisted word.
6. You will then be prompted if you want to add another subreddit. If you would like to search across multiple subreddits, press y, if not press n to finish.
* Note that filters are unique to the subreddit that they are defined for.

7. You will then be brought to a screen that has a list of names of searches. You should see the one you just created at the bottom of this list.

## Search Selection

On the screen listing searches, you have several options. 
*   Pressing a will allow you to create a new search. Reference the Creating a search section for help with this.
*   Pressing e will allow you to enter a number. This search will then be run. See the Results section for the next steps.
*   Pressing d will also allow you to enter a number, this search will be deleted from the list *Warning! This can not be undone*
*   Pressing v will allow you to enter a number. This search will then be displayed in a tree form. This is useful for seeing the filters and parameters of the search.
*   Pressing q will close the program.    

## Results

* While the search is being performed, you will see a screen that says "Searching..." simply wait and let the search commence
* After the search is finished, you will see boxed stacked on top of each other vertically. These are the "headers" of your results. Each box contains corresponds to a single post within your criteria. They each contain the following: 
    * A number followed by ): This is the reference number in the list of results. More on this later
    * Immediately following the reference number is the title of the post.
    * On a new line is author of the post, surrounded by square brackets
    * On another new line is the flairs that the author set for the post
    * Finally, is the subreddit that the post is in, as well as its age. Note that the age is rounded down to the closest significant time period. For example a post that is 80 minutes old will be described as being 1 hour old. A post that is 3 days, 6 hours, and 42 minutes old will be described as being 3 days old.
* The list of boxes can be scrolled through. Pressing the 'w' key or up arrow will scroll everything up a single line. Pressing the 's' or down arrow key will scroll everything down a single line. On most systems, these can also be held down to scroll quicker. Most systems also support mouse scrolling, which will perform the same function.
* Besides scrolling through the list, you have two other options for input:
    * Pressing e will allow you to enter a number. This number should correspond to a reference number of one of the posts. This will pull up a full screen view of the post, and will contain the actual body text of the post. Reference the Viewing a post section for the next steps.
    * Pressing q will quit the program.


## Viewing a post

* Posts viewed in full consist of three parts:
    * Head section. This is the first box. Notice that it contains the same contents as the headers found in the navigating results section. Reference the Results section for a description of these.
    * Body section. This contains the actual text of the post.
    * Foot section. This contains the url of the post. Note that due to limitations of the terminal, this link can not be clicked on. You will have to manually copy it over if you want to use it. This link is simply for information. More efficient methods exist for opening the link in a brower.

* There are numerous different shortcut keys for different actions that can be performed in this section:
    * Pressing h will bring up a cheatsheet help menu with a description of the available shortcuts. Press any key after this to return to the post.
    ### Navigation
    * Pressing or holding w or the up arrow will scroll up through the post
    * Pressing or holding s or the down arrow will scroll down through the post
    * Pressing a or the left arrow will pull up the post with the reference number one less than the current one. This is an easy way shift between different posts.
    * Pressing d or the right arrow will pull up the post with the reference number one greater than the current one.
    * Press q to return to the screen with all of the post headers. Refer to the Results section for details on this area

    ### Interacting
    * Pressing i will open up the image of the post, if it is an image post instead of a text post.
    * pressing o will open the post up on the official reddit website, in your default web browser
    * Pressing u will shift to another screen that displays a file name. All of the links in the post have been written to the file. Links are written in the order they are added. So the newest links will be at the bottom of the file. After you have viewed the links, it is safe to delete them from the file.
    * Pressing m will open up the page of the author on the official reddit website, in your default web browser.


## Advanced

* If you know which search you want to perform ahead of time, you can save time by specifying it in the command line. To do this, run `python3 main.py -n <search_name>` Do note that search names are case sensitive, such that "mysearch" is not the same as "MYSEARCH". If you specify a search that does not exist, the program will list out all available searches that are present in the specified search file. 
* Adding a -d flag prevents the lastSearchTime from being modified. This is useful if you want to run the search over the same timeframe multiple times.
* Adding a -y flag will automatically agree to prompts asking if you want to run a search that hasn't be run in a while (typically over a week)