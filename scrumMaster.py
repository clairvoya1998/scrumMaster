import logging
import os
import datetime
import pickle
import time
from trello.trello import *
from scrumEmail import *

import boto3

from flask import Flask
from flask_ask import Ask, request, session, question, statement, delegate


app = Flask(__name__)
ask = Ask(app, "/")
client = boto3.client('s3')
log = logging.getLogger('flask_ask')
bucket = 'scrummaster.oxfordhack'
key = 'projects'

#OLD ONE archieve_info = {'project_name1' : {'boardID' : '', 'sprint-finish' : '2018-01-01', 'participants': {'name1':'ID1', 'name2':'ID2'}}, 'project_name2': {}}
#archieve_info = {'the scrum master': '2018-11-26'}
obj = client.get_object(Bucket=bucket, Key=key)
raw_data = obj['Body'].read()
archieve_info = pickle.loads(raw_data)
SECRET_STATE = ""
last_user_story_id = -1

participantsDict = getParticipants("5bf94119b7c0ff5b494d440a")

def set_SECRET_STATE(newstate):
    global SECRET_STATE
    SECRET_STATE = newstate


standup_meeting = False

team_size = 3
team_counter = 0
team_members = ['Elsa', 'Ville', 'Amy']

def set_teamCounter(num):
    global team_counter
    team_counter = num

def get_teamCounter():
    return team_counter

team_size = 0
team_members = []

@ask.launch
def launch():
    speech_text = "Hey guys. I'm Alexa, your Scrum Master. What project would you like to work on?"
    set_teamCounter(0)
    set_SECRET_STATE("")
    global STAGE
    STAGE = 0
    return question(speech_text).reprompt(speech_text)

# @ask.intent('NewProjectIntent')
# def get_new_project():
#     speech_text = 'Please confirm the name of your new project.'
#     return question(speech_text).reprompt(speech_text)

@ask.intent('ProjectNameIntent')	
def new_project(Text):	
    if ((Text) in archieve_info.keys()):	
        speech_text = "Great. Do you want to have a design meeting or a stand up meeting?"	
    else:	
        today = datetime.datetime.now().strftime("%Y-%m-%d")	
        archieve_info.update({Text : today})	
        speech_text = 'You said: {}, this is not the name of an existing project. I will create this new project now.' \
                      'So, do you want to have a design meeting or a stand up meeting?'.format(Text)
        # add Text to the array
        archieve_info.add({Text: today})
    return question(speech_text).reprompt(speech_text)


# @ask.intent('getMemberIntent')
# def get_new_member():
#     speech_text = 'Please say the name of a new member'
#     return statement(speech_text)

#STAND UP MEETING
#IF NOT END OF SPRINT
#i THINK it's time for a stand up meeting

def get_dialog_state():
    return SECRET_STATE

def get_name():
    team_counter = get_teamCounter()
    if (team_counter != team_size):
        temp = team_members[team_counter]
        set_teamCounter(team_counter + 1)
        return temp

@ask.intent('StandUpMeetingIntent')
def start_stand_up():

    set_SECRET_STATE("ATTENDANCE")
    speech_text = "Great. It's time for the daily stand up. Let's take attendance. " + get_name() + "?"
    return question(speech_text).reprompt(speech_text).simple_card('Attendance', speech_text)


def get_mydialog_state():
    return session['dialogState']


@ask.intent('StandupRoutineIntent', convert= {"yesterday" : str, "today" : str, "problem" : str})
def routine():

    yesterday = routine_yesterday()
    today = routine_today()
    problem = routine_problem()
    speech_text = "Okay. "

    dialog_state = get_mydialog_state()
    if dialog_state != "COMPLETED":
        return delegate()

    if get_teamCounter()< team_size:
        speech_text = speech_text + "next, please confirm your attendance, " + get_name() + "?"
        return question(speech_text)
    else:
        emails = readmail()
        return statement(speech_text + " My emails read: " + emails)

@ask.intent('BlockIntent', convert={"problem" : str})
def routine_problem():
    routine_problem_prompt = problems()
    return question(routine_problem_prompt)

@ask.intent('yesterdayIntent', convert={"yesterday" : str})
def routine_yesterday():
    routine_yesterday_prompt = yesterday()
    return question(routine_yesterday_prompt)

@ask.intent('todayIntent', convert={"today" : str})
def routine_today():
    routine_today_prompt = today()
    return question(routine_today_prompt)




@ask.intent('AMAZON.YesIntent')
def yes_intent():
    speech_text = "Good. "
    if get_dialog_state() == "ATTENDANCE":
        speech_text = speech_text + trelloCount() + "Please say stand up to continue. "
        return question(speech_text)
    elif get_dialog_state() == "ADD_TASK_OR_NOT":
        set_SECRET_STATE("READ_TASK_NAME")
        return question("What should the task's title be?")
    elif get_dialog_state() == "ADD_USER_STORY_OR_NOT":
        set_SECRET_STATE("READ_USER_STORY_NAME")
        return question("What is the user story's title?")
    else:
        return statement("Hi")

@ask.intent('AMAZON.NoIntent')
def no_intent():
    speech_text = "what a shame. "
    if get_dialog_state() == "ATTENDANCE":
        if get_teamCounter() < team_size:
            speech_text = speech_text + "next, please confirm your attendance, " + get_name() + "?"
            return question(speech_text)
        else:
            emails = readmail()
            return statement(speech_text + " My emails read: " + emails)
    elif get_dialog_state() == "ADD_TASK_OR_NOT":
        set_SECRET_STATE("ADD_USER_STORY_OR_NOT")
        return question("Okay. Would you like to add another user story?")
    elif get_dialog_state() == "ADD_USER_STORY_OR_NOT":
        emails = readmail()
        return statement("Okay. This meeting is over, then. My emails read: " + emails)
    else:
        return statement("Bye")

def trelloCount():
    tasks= getNumberOfTasksInSprint(participantsDict[team_members[team_counter-1]])
    word = "You have " + str(tasks['complete']) + " cOmpLeTe tasks, "
    if tasks['complete'] == 0:
        word = word + "YOU BETTER WORK BITCH. "
    word = word + "You also have " + str(tasks['incomplete']) + " incOmpLeTe tasks remain. "
    return word


def today():
    tasks = getNumberOfTasksInSprint(participantsDict[team_members[team_counter-1]])
    word1 = "You have " + str(tasks['incomplete']) + " incOmpLeTe tasks, "
    #log.info(word1)
    word = "what are you going to do today?"
    return word1+ word

def yesterday():
    tasks = getNumberOfTasksInSprint(participantsDict[team_members[team_counter - 1]])
    word1 = "You have " + str(tasks['complete']) + " cOmpLeTeD tasks, "
    if tasks['complete'] == 0:
        word1 = word1 + "YOU BETTER WORK BITCH. "
    word = 'what did you do yesterday?'
    return word1 + word

def problems():
    word = 'Any blockers?'
    return word

@ask.intent('DesignMeetingIntent')
def start_design_meeting():
    speech_text = "Excellent! I'm adding the first user story. What should it be called?"
    set_SECRET_STATE = "READ_USER_STORY_NAME";
    return question(speech_text).reprompt(speech_text)

@ask.intent('SprintDateIntent')
def sprint_update():
    days_left = 5 # sprint end date - current date
    tasks_left = 5
    return question('There are' + days_left + 'days left in the sprint and' + tasks_left + 'tasks left to accomplish')

# @ask.intent('HelloWorldIntent')
# def hello_world():
#     speech_text = 'Hello world'
#     return statement(speech_text)

# TODO define an intent for reading a title
@ask.intent('CardTitleIntent')
def write_card_title():
    name = "" #TODO what the user wants to call it
    speech_text = ""
    if SECRET_STATE == "READ_USER_STORY_NAME":
        card_id = addUserStory(name, "")  #TODO add user story due date
        last_user_story_id = card_id
        speech_text = "I have added this to the product backlog. Now, who should we assign to this user story?"
        set_SECRET_STATE("READ_ASSIGNEE_NAME")
    elif SECRET_STATE == "READ_TASK_NAME":
        addTaskToUserStory(name, last_user_story_id)
        speech_text = "Task added to user story. Would you like to add another task for this user story?"
        set_SECRET_STATE("ADD_TASK_OR_NOT")
    return question(speech_text)

# TODO define an intent for reading a person's name
@ask.intent('NameIntent')
def write_assignee_name():
    name = ""   #TODO get from user
    speech_text = ""
    if SECRET_STATE == "READ_ASSIGNEE_NAME":
        assignMemberToUserStory(participantsDict[name], last_user_story_id)
        speech_text = "I have assigned " + name + " to this user story. Now, what task is required to complete ?"
        set_SECRET_STATE("READ_TASK_NAME")
    return question(speech_text)


@ask.intent('AMAZON.HelpIntent')
def help():
    speech_text = 'You can say hello to me!'
    return question(speech_text).reprompt(speech_text)



@ask.session_ended
def session_ended():
    data = pickle.dumps(archieve_info)
    response = client.put_object(
        Bucket=bucket,
        Body= data,
        Key=key)
    return "{}", 200


if __name__ == '__main__':
    if 'ASK_VERIFY_REQUESTS' in os.environ:
        verify = str(os.environ.get('ASK_VERIFY_REQUESTS', '')).lower()
        if verify == 'false':
            app.config['ASK_VERIFY_REQUESTS'] = False
    app.run(debug=True)
