def placeItem(name,showBeginning,showMiddle,last,width=80,fancy=False):
    """
    Used by search tree for the third tier items
    """
    pipe="|"
    branch="|->"
    end="|->"
    space="  "
    spaceStart=""
    if(fancy == True):
        pipe="│"
        branch="├─"
        end="└─"
        space=" "

    if(showBeginning == True):
        string = f"{spaceStart}{pipe}"
    else:
        string = f"{spaceStart} "

    if(showMiddle == True):
        string = f"{string}{space}{pipe}"
    else:
        string = f"{string}{space} "
    if(last == True):
        string = f"{string}{space}{end}"
    else:
        string = f"{string}{space}{branch}"
    
    lenTest = f"{spaceStart}{pipe}{space}{pipe}{space}{branch}"
    if(len(name) > ((width-1)-len(lenTest))):
        name = f"{name[:(width-4)-(len(lenTest))]}..."

    return (f"{string}{name}")

def placeTitle(name,showBeginning,last,fancy=False):
    """
    Used by search tree for the second tier items
    """

    pipe="|"
    branch="|->"
    end="|->"
    space="  "
    spaceStart=""
    if(fancy == True):
        pipe="│"
        branch="├─"
        end="└─"
        space=" "

    if(showBeginning == True):
        string = f"{spaceStart}{pipe}"
    else:
        string = f"{spaceStart} "
    if(last == True):
        string = f"{string}{space}{end}"
    else:
        string = f"{string}{space}{branch}"
    
    return (f"{string}{name}")
    
    



def searchTree(search,width=80,fancy=False):
    """
    Returns a list of strings representing a tree-style view of a search
    """
    if(search is not None):
        stringList = []
        if(not search.name == None):
            stringList.append(search.name)
            if(not search.subreddits == None):
                if(fancy == True):
                    tierOne="├─"
                    tierOneLast="└─"
                else:
                    tierOne="|->"
                    tierOneLast=tierOne
                
                subNum=0
                lastSub=len(search.subreddits)
                finalSub=True
                for sub in search.subreddits:
                    subNum = subNum+1
                    if(subNum >= lastSub):
                        finalSub = False
                    if(not sub.titleWL == None and len(sub.titleWL) > 0):
                        subLast = 0
                    if(not sub.titleBL == None and len(sub.titleBL) > 0):
                        subLast = 1
                    if(not sub.flairWL == None and len(sub.flairWL) > 0):
                        subLast = 2
                    if(not sub.flairBL == None and len(sub.flairBL) > 0):
                        subLast = 3
                    if(not sub.postWL == None and len(sub.postWL) > 0):
                        subLast = 4
                    if(not sub.postBL == None and len(sub.postBL) > 0):
                        subLast = 5
                    
                    if(finalSub == False):
                        stringList.append(f"{tierOneLast}{sub.name}")
                    else:
                        stringList.append(f"{tierOne}{sub.name}")
                    if(not sub.titleWL == None and len(sub.titleWL) > 0):
                        stringList.append(placeTitle("Title whitelist",finalSub,subLast==0,fancy))
                        numItems = 0
                        for item in sub.titleWL:
                            numItems = numItems + 1
                            last = (numItems == len(sub.titleWL))
                            if(subLast == 0):
                                stringList.append(placeItem(item,finalSub,False,last,width,fancy))
                            else:
                                stringList.append(placeItem(item,finalSub,True,last,width,fancy))

                    if(not sub.titleBL == None and len(sub.titleBL) > 0):
                        stringList.append(placeTitle("Title blacklist",finalSub,subLast==1,fancy))
                        numItems = 0
                        for item in sub.titleBL:
                            numItems = numItems + 1
                            last = (numItems == len(sub.titleBL))
                            if(subLast == 1):
                                stringList.append(placeItem(item,finalSub,False,last,width,fancy))
                            else:
                                stringList.append(placeItem(item,finalSub,True,last,width,fancy))

                    if(not sub.flairWL == None and len(sub.flairWL) > 0):
                        numItems = 0
                        stringList.append(placeTitle("Flair whitelist",finalSub,subLast==2,fancy))
                        for item in sub.flairWL:
                            numItems = numItems + 1
                            last = (numItems == len(sub.flairWL))
                            if(subLast == 2):
                                stringList.append(placeItem(item,finalSub,False,last,width,fancy))
                            else:
                                stringList.append(placeItem(item,finalSub,True,last,width,fancy))

                    if(not sub.flairBL == None and len(sub.flairBL) > 0):
                        numItems = 0
                        stringList.append(placeTitle("Flair blacklist",finalSub,subLast==3,fancy))
                        for item in sub.flairBL:
                            numItems = numItems + 1
                            last = (numItems == len(sub.flairBL))
                            if(subLast == 3):
                                stringList.append(placeItem(item,finalSub,False,last,width,fancy))
                            else:
                                stringList.append(placeItem(item,finalSub,True,last,width,fancy))

                    if(not sub.postWL == None and len(sub.postWL) > 0):
                        numItems = 0
                        stringList.append(placeTitle("Post whitelist",finalSub,subLast==4,fancy))
                        for item in sub.postWL:
                            numItems = numItems + 1
                            last = (numItems == len(sub.postWL))
                            if(subLast == 4):
                                stringList.append(placeItem(item,finalSub,False,last,width,fancy))
                            else:
                                stringList.append(placeItem(item,finalSub,True,last,width,fancy))

                    if(not sub.postBL == None and len(sub.postBL) > 0):
                        numItems = 0
                        stringList.append(placeTitle("Post blacklist",finalSub,subLast==5,fancy))
                        for item in sub.postBL:
                            numItems = numItems + 1
                            last = (numItems == len(sub.postBL))
                            if(subLast == 5):
                                stringList.append(placeItem(item,finalSub,False,last,width,fancy))
                            else:
                                stringList.append(placeItem(item,finalSub,True,last,width,fancy))
        return stringList
    else:
        return None
