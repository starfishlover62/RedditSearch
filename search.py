class subSearch:
    def __init__(self,sub,titleWL,titleBL,flairWL,flairBL,postWL,postBL):
        self.subreddit = sub
        self.whiteListTitle = titleWL
        self.blackListTitle = titleBL
        self.whiteListFlair = flairWL
        self.blackListFlair = flairBL
        self.whiteListPost = postWL
        self.blackListPost = postBL


class search:
    def __init__(self,name,lastSearchTime,subreddits):
        self.name = name
        self.lastSearchTime = lastSearchTime
        self.subreddits = subreddits

    