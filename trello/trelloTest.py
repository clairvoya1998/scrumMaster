from trello import *

memberId = "5bf93fcf6c1a3a2446b3d235"
tasks = getNumberOfTasksInSprint(memberId)
print(tasks)

y = addUserStory("Dummy", "01/01/2019")
print(y)

assignMemberToUserStory(memberId, y)

addTaskToUserStory("Cuddle the cats", y)
