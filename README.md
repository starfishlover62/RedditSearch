# RedditScraper
Scrapes subreddits and filters by flair or title


For pyperclip, if it doesn't work, run sudo apt-get install xclip. For more information see https://pypi.org/project/pyperclip/

Issues:

* scroll.py Tooltip class does not have proper spacing. It does not account for blank lines between rows
* Scrolling will sometimes be allowed when it shouldnt, leading to instances of being at a negative line number
* main.py browsing mode still uses old method of tool tip, needs to be updated
* No user / subreddit shown on full post view
* Does not fully check that config is proper
* No command line options
* Formatting of post text can be a little wonky at times
* Doesn't handle banned, quarantined, private, or nonexistent subreddits