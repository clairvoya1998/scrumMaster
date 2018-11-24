# board = {id: int, lists: {<id>: name, ...}}

import requests
import json

URL_AUTH = "?key=d51bef30a16e2cad69ad5c5878052378&token=74917a16e0990241b66b78172b86317fed00acbb3e9f5afb3b2e30585f6d3ee2"

def getNumberOfTasksInSprint(memberId, board):
    tasksInSprint = 0

    # Get all cards the member is on
    url = "https://api.trello.com/1/member/" + memberId + "/cards" + URL_AUTH
    cards = json.loads(requests.request("GET", url).text)
    #print(cards)

    for card in cards:
        #print(card)
        if board["lists"][card["idList"]] == "Sprint backlog":
            checklistId = card["idChecklists"][0]
            #print(checklistId)
            url = "https://api.trello.com/1/checklists/" + checklistId + URL_AUTH
            checklist = json.loads(requests.request("GET", url).text)
            for task in checklist["checkItems"]:
                if task["state"] == "incomplete":
                    tasksInSprint += 1

    return tasksInSprint

board = {"id": "xax", "lists": {"5bf94330f69be717f2c19d8f": "Sprint backlog"}}
i = getNumberOfTasksInSprint("5bf93fcf6c1a3a2446b3d235", board)
print(str(i))
