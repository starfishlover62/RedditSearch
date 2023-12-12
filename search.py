class SubredditSearch:
    def __init__(self,sub,titleWL=None,titleBL=None,flairWL=None,flairBL=None,postWL=None,postBL=None):
        self.name = sub
        self.titleWL = titleWL
        self.titleBL = titleBL
        self.flairWL = flairWL
        self.flairBL = flairBL
        self.postWL = postWL
        self.postBL = postBL


class Search:
    def __init__(self,name,lastSearchTime,subreddits):
        self.name = name
        self.lastSearchTime = lastSearchTime
        self.subreddits = subreddits

    