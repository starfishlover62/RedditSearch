class subredditSearch:
    def __init__(self,sub,titleWL,titleBL,flairWL,flairBL,postWL,postBL):
        self.name = sub
        self.titleWL = titleWL
        self.titleBL = titleBL
        self.flairWL = flairWL
        self.flairBL = flairBL
        self.postWL = postWL
        self.postBL = postBL


class search:
    def __init__(self,name,lastSearchTime,subreddits):
        self.name = name
        self.lastSearchTime = lastSearchTime
        self.subreddits = subreddits

    