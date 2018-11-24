# Pseudocode on alexa skills

# Add an user story
userStory_name = ask_user("What's the user story name?")   # e.g. "Dummy"
userStory_deadline = sprint_deadline # e.g. "01/01/2019"
userStoryId = addUserStory(userStory_name, userStory_deadline)

person_name = ask_user("And who should we assign to this task?")
assignMemberToUserStory(participants[person_name], userStoryId)

task_wanted = ask_user("Do you want to add a task to this user story?")
while task_wanted:
    taskName = ask_user("What is the task name?")
    addTaskToUserStory(taskName, userStoryId)
    task_wanted = ask_user("Do you want to add a task to this user story?")
tell_user("This user story has been added to the board")
