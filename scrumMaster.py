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

#archieve_info = {'project_name1' : {'boardID' : '', 'sprint-finish' : '2018-01-01', 'participants': {'name1':'ID1', 'name2':'ID2'}}, 'project_name2': {}}
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
    speech_text = "Hey guys. Here I am, Alexa, your Scrum Master. Do you want to have a standup or design meeting?"
    set_teamCounter(0)
    set_SECRET_STATE("")
    global STAGE
    STAGE = 0
    return question(speech_text).reprompt(speech_text)

# @ask.intent('NewProjectIntent')
# def get_new_project():
#     speech_text = 'Please confirm the name of your new project.'
#     return question(speech_text).reprompt(speech_text)


# @ask.intent('getMemberIntent')
# def get_new_member():
#     speech_text = 'Please say the name of a new member'
#     return statement(speech_text)


# @ask.intent('ProjectNameIntent')
# def new_project(Text):
#     if ((Text) in archieve_info.keys()):
#         speech_text = "I have found an existed project, do you want to continue that session?"
#     else:
#         today = datetime.datetime.now().strftime("%Y-%m-%d")
#         archieve_info.update({Text : today})
#         speech_text = 'You said: {}, what a great name, shall we start the sprint?'.format(Text)
#         # add Text to the array
#     return question(speech_text).reprompt(speech_text)

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

    set_SECRET_STATE("STANDUP")

    #standup_meeting = True
    speech_text = "Great. It's time for the daily stand up. Let's take attendance. " + get_name() + "?"
    return question(speech_text).reprompt(speech_text).simple_card('Attendance', speech_text)

STAGE = 0
def change_STAGE():
    global STAGE
    if (get_STAGE() == 0):
        STAGE = 1
    elif (get_STAGE() == 1):
        STAGE = 2
    elif (get_STAGE() == 2):
        STAGE = 0
        set_SECRET_STATE("ATTENDANCE")


def get_STAGE():
    return STAGE

@ask.intent('AMAZON.YesIntent')
def yes_intent():
    speech_text = "Good. "
    if get_dialog_state() == "ATTENDANCE":
        if team_counter != team_size:
            set_SECRET_STATE("STANDUP")
            speech_text = "SHUT UP. "
            return question(speech_text + get_name())
        else:
            emails = readmail()
            return statement(speech_text + " My emails read: " + emails)
    elif get_dialog_state() == "STANDUP":
        if get_STAGE() == 0:
            change_STAGE()
            return question(speech_text + yesterday())
        elif get_STAGE() == 1:
            change_STAGE()
            return question(speech_text + today())
        elif get_STAGE() == 2:
            change_STAGE()
            return question(speech_text + problems())
    elif get_dialog_state() == "ADD_TASK_OR_NOT":
        set_SECRET_STATE("READ_TASK_NAME")
        return question("What should the task's title be?")
    elif get_dialog_state() == "ADD_USER_STORY_OR_NOT":
        set_SECRET_STATE("READ_USER_STORY_NAME")
        return question("What should the user story's title be?")
    else:
        return statement("Hi")


@ask.intent('AMAZON.NoIntent')
def no_intent():
    speech_text = "What a shame. "
    if get_dialog_state() == "ATTENDANCE":
        if team_counter != team_size:
            set_SECRET_STATE("STANDUP")
            return question(speech_text + get_name())
        else:
            emails = readmail()
            return statement(speech_text + " My emails read: " + emails)
    elif get_dialog_state() == "STANDUP":
        if get_STAGE() == 0:
            #change_STAGE()
            if (get_teamCounter() < team_size):
                return question(speech_text + get_name())
            else:
                emails = readmail()
                return statement(speech_text + " My emails read: " + emails)
        elif get_STAGE() == 1:
            change_STAGE()
            return question(speech_text + today())
        elif get_STAGE() == 2:
            change_STAGE()
            speech_text = "Good. "
            return question(speech_text + problems())
    elif get_dialog_state() == "ADD_TASK_OR_NOT":
        set_SECRET_STATE("ADD_USER_STORY_OR_NOT")
        return question("Okay. Would you like to add another user story?")
    elif get_dialog_state() == "ADD_USER_STORY_OR_NOT":
        emails = readmail()
        return statement("Okay. This meeting is over, then. My emails read: " + emails)
    else:
        return statement("Bye")


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
    word = 'Any problem happened?'
    return word

@ask.intent('DesignMeetingIntent')
def start_design_meeting():
    speech_text = "Excellent! I'm adding the first user story. What should it be called?"
    set_SECRET_STATE = "READ_USER_STORY_NAME";
    return question(speech_text).reprompt(speech_text)

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




@ask.intent('AMAZON.YesIntent')
def yes_intent():
    return statement("Hi")


@ask.intent('AMAZON.NoIntent')
def no_intent():
    return statement("What a shame.")


@ask.intent('SprintDateIntent')
def sprint_update():
    days_left = 5 # sprint end date - current date
    tasks_left = 5
    return question('There are' + days_left + 'days left in the sprint and' + tasks_left + 'tasks left to accomplish')

# @ask.intent('HelloWorldIntent')
# def hello_world():
#     speech_text = 'Hello world'
#     return statement(speech_text)


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
