import requests
import json

URL_AUTH = "key=d51bef30a16e2cad69ad5c5878052378&token=74917a16e0990241b66b78172b86317fed00acbb3e9f5afb3b2e30585f6d3ee2"

def getNumberOfTasksInSprint(memberId):
    tasksInSprint = 0

    # Get all cards the member is on
    url = "https://api.trello.com/1/member/" + memberId + "/cards?" + URL_AUTH
    cards = json.loads(requests.request("GET", url).text)
    #print(cards)

    for card in cards:
        print(card)
        if card["idList"] == "5bf94330f69be717f2c19d8f":    # hard-coded, Sprint Backlog
            checklistId = card["idChecklists"][0]
            #print(checklistId)
            url = "https://api.trello.com/1/checklists/" + checklistId + "?" + URL_AUTH
            checklist = json.loads(requests.request("GET", url).text)
            for task in checklist["checkItems"]:
                if task["state"] == "incomplete":
                    tasksInSprint += 1

    return tasksInSprint


# Adding a new user story:
    # add user story
    # Assign (one) person to the user story
    # add tasks (one by one)

# dueDate: dd/mm/yyyy
# auto-set idList to product backlog
# For now, assign users later
# RETURN: id of the inserted user story
def addUserStory(name, dueDate):
    pplId = "5bf94119b7c0ff5b494d440b"
    card = {"name": name, "dueDate": dueDate, "idList": pplId}
    url = "https://api.trello.com/1/cards/?" + URL_AUTH
    createdCard = json.loads(requests.request("POST", url, params=card).text)
    id = createdCard["id"]

    url = "https://api.trello.com/1/checklists?" + URL_AUTH
    querystring = {"idCard": id}
    response = requests.request("POST", url, params=querystring)

    return id

# Returns a mapping of first names and ids
def getParticipants(boardId):
    url = "https://api.trello.com/1/boards/" + boardId + "/members?" + URL_AUTH
    response = json.loads(requests.request("GET", url).text)

    participants = {}
    for person in response:
        firstName = person["fullName"].split(" ")[0]
        participants[firstName] = person["id"]
    return participants

def assignMemberToUserStory(memberId, cardId):
    url = "https://api.trello.com/1/cards/" + cardId + "/idMembers?value=" + memberId + "&" + URL_AUTH
    print(url)
    print(requests.request("PUT", url).text)

def addTaskToUserStory(taskName, cardId):
    url = "https://api.trello.com/1/cards/" + cardId + "/checklists?" + URL_AUTH
    checklist = json.loads(requests.request("GET", url).text)[0]

    url = "https://api.trello.com/1/checklists/" + checklist["id"] + "/checkItems?" + URL_AUTH
    querystring = {"name": taskName}
    print(json.loads(requests.request("POST", url, params=querystring).text))
