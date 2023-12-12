import json


def serializeSub(sub):
    string = f'"name":"{sub.name}", "whiteListTitle":{sub.titleWL}, "blackListTitle":{sub.titleBL}, "whiteListFlair":{sub.flairWL}, "blackListFlair":{sub.flairBL}, "whiteListPost":{sub.postWL}, "blackListPost":{sub.postBL}'
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


def saveSearches(searches, filepath = "searches.json"):
    dumpStr = serializeSeaches(searches)
    parsed = json.loads(dumpStr)
    with open(filepath,"w") as write:
        json.dump(parsed,write,indent=2)