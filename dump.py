import json
import search



def serializeSub(sub):
    string = f'"name":"{sub.subreddit}", "whiteListTitle":{sub.whiteListTitle}, "blackListTitle":{sub.blackListTitle}, "whiteListFlair":{sub.whiteListFlair}, "blackListFlair":{sub.blackListFlair}, "whiteListPost":{sub.whiteListPost}, "blackListPost":{sub.blackListPost}'
    string = "{" + string + "}"
    string = string.replace("'",'"')
    string = string.replace("None","null")
    return string

def serializeSeach(search):
    string = f'"name":"{search.name}", "lastSearchTime":{search.lastSearchTime}, "subreddits":['
    for item in search.subreddits:
        string = string + serializeSub(item) + ","
    
    string = string.rstrip(",")
    string = string + "]"
    string = "{" + string + "}"
    string = string.replace("'",'"')
    string = string.replace("None","null")
    return string


def serializeSeaches(searches):
    string = f'"searches":['
    for item in searches:
        string = string + serializeSeach(item) + ","
    
    string = string.rstrip(",")
    string = string + "]"
    string = "{" + string + "}"
    string = string.replace("'",'"')
    string = string.replace("None","null")

    return string