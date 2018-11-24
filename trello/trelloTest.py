from trello import *

board = {"id": "xax", "lists": {"5bf94330f69be717f2c19d8f": "Sprint backlog", "5bf94119b7c0ff5b494d440b": "Product Backlog"}}
memberId = "5bf93fcf6c1a3a2446b3d235"
i = getNumberOfTasksInSprint(memberId, board)
print(str(i))

y = addUserStory("Dummy", "01/01/2019")
print(y)

assignMemberToUserStory(memberId, y)

addTaskToUserStory("Cuddle the cats", y)
