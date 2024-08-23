# RedditScraper

*** INCOMPLETE ***

Scrapes subreddits and filters by flair or title


Currently only tested on linux, however it should work on Windows.

Tested Python versions: 3.12.3

Utilizes ncurses library, which must be installed if it isn't already.

# Installation

1. clone the repository
2. Navigate to https://old.reddit.com/prefs/apps/, login, then create an id.
3. Open config.py
4. Copy the ID to client_id, the secret to client_secret, and your user agent to user_agent
* Note that the user agent can be found here https://whatmyuseragent.com/
6. (Optional) the path in searches_file can be edited to specify a different file to store saved searches
7. Install required libraries. They can be found in requirements.txt (Run `pip install -r requirements.txt`)
8. Finally, run program with `python3 main.py`


For pyperclip, if it doesn't work, run sudo apt-get install xclip. For more information see https://pypi.org/project/pyperclip/

# Usage

## Search Selection

On the screen listing searches, you have 3 options. Pressing q will close the program. pressing e will allow you to enter a number. This search will then be run.
Pressing d will also allow you to enter a number, this search will be deleted from the list *Warning! This can not be undone*




# Issues:

* scroll.py Tooltip class does not have proper spacing. It does not account for blank lines between rows
