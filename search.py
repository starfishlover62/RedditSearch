class SubredditSearch:
    def __init__(self,sub=None,titleWL=None,titleBL=None,flairWL=None,flairBL=None,postWL=None,postBL=None):
        self.name = sub
        self.titleWL = titleWL
        self.titleBL = titleBL
        self.flairWL = flairWL
        self.flairBL = flairBL
        self.postWL = postWL
        self.postBL = postBL
    def update(self,sub=None,titleWL=None,titleBL=None,flairWL=None,flairBL=None,postWL=None,postBL=None):
        # Updates values if they are presented
        if(not sub == None):
            self.name = sub
        if(not titleWL == None):
            self.titleWL = titleWL
        if(not titleBL == None):
            self.titleBL = titleBL
        if(not flairWL == None):
            self.flairWL = flairWL
        if(not flairBL == None):
            self.flairBL = flairBL
        if(not postWL == None):
            self.postWL = postWL
        if(not postBL == None):
            self.postBL = postBL

class Search:
    def __init__(self,name=None,lastSearchTime=None,subreddits=None):
        self.name = name
        self.lastSearchTime = lastSearchTime
        self.subreddits = subreddits
    def update(self,name=None,lastSearchTime=None,subreddits=None):
        # Updates values if they are presented
        if(not name == None):
            self.name = name
        if(not lastSearchTime == None):
            self.lastSearchTime = lastSearchTime
        if(not subreddits == None):
            self.subreddits = subreddits

    