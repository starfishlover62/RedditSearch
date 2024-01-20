# RedditScraper
Scrapes subreddits and filters by flair or title


For pyperclip, if it doesn't work, run sudo apt-get install xclip. For more information see https://pypi.org/project/pyperclip/

Issues:

* scroll.py Tooltip class does not have proper spacing. It does not account for blank lines between rows
* Scrolling will sometimes be allowed when it shouldnt, leading to instances of being at a negative line number
* Text display is not centered, nor does it keep words together at the end of the line. Need to have words not be wrapped across lines, unless necessary
* Search selection display and prompts are a bit lackluster
* Does not fully check that config is proper
* No command line options
