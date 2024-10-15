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
        if(sub is not None):
            self.name = sub
        if(titleWL is not None):
            self.titleWL = titleWL
        if(titleBL is not None):
            self.titleBL = titleBL
        if(flairWL is not None):
            self.flairWL = flairWL
        if(flairBL is not None):
            self.flairBL = flairBL
        if(postWL is not None):
            self.postWL = postWL
        if(postBL is not None):
            self.postBL = postBL

class Search:
    def __init__(self,name=None,lastSearchTime=None,subreddits=None):
        self.name = name
        self.lastSearchTime = lastSearchTime
        self.subreddits = subreddits
    def update(self,name=None,lastSearchTime=None,subreddits=None):
        # Updates values if they are presented
        if(name is not None):
            self.name = name
        if(lastSearchTime is not None):
            self.lastSearchTime = lastSearchTime
        if(subreddits is not None):
            self.subreddits = subreddits

    