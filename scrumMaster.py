import logging
import os
import datetime
import pickle

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

SECRET_STATE = "";



standup_meeting = False

team_size = 3
team_counter = 0
team_members = ['a', 'b', 'c']


@ask.launch
def launch():
    speech_text = "Hey guys. Here I am, Alexa, your Scrum Master. What's your project?"
    return question(speech_text).reprompt(speech_text)

@ask.intent('NewProjectIntent')
def get_new_project():
    speech_text = 'Please confirm the name of your new project.'
    return question(speech_text).reprompt(speech_text)


@ask.intent('ProjectNameIntent')
def new_project(Text):
    if ((Text) in archieve_info.keys()):
        speech_text = "I have found an existed project, do you want to continue that session?"
    else:
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        archieve_info.update({Text : today})
        speech_text = 'You said: {}, what a great name, shall we start the sprint?'.format(Text)
        # add Text to the array
    return question(speech_text).reprompt(speech_text)







def get_dialog_state():
    return SECRET_STATE

def get_name():
    if (team_counter != team_size):
        temp = team_members[team_counter]
        name_counter = team_counter + 1
        return temp

@ask.intent('StandUpMeetingIntent')
def start_stand_up():

    SECRET_STATE = "ATTENDANCE"

    #standup_meeting = True
    speech_text = "Great. It's time for the daily stand up. Let's take attendance. " + get_name() + "?"
    return question(speech_text).reprompt(speech_text).simple_card('Attendance', speech_text)

@ask.intent('AMAZON.YesIntent')
def yes_intent():
    if SECRET_STATE != "ATTENDANCE":
        return question();
    else:

        return statement("Hi")


@ask.intent('AMAZON.NoIntent')
def no_intent():
    return statement("What a shame.")










#STAND UP MEETING
#Alexa, where's my scrum master
#Hello, what's your project
#projectName
#IF NOT END OF SPRINT
#i THINK it's time for a stand up meeting

def take_attendance():
    for i in range(team_size):
        attendance(i)
    return 0

@ask.intent("AttendanceIntent")
def attendance(i):
    speech_text = "<p>{}?</p>".format(team_members[i])

    # check user says "Here"
    # else "Oh no. user is not here."
    return question(speech_text)


@ask.intent('SprintDateIntent')
def sprint_update():
    days_left = 5 # sprint end date - current date
    tasks_left = 5
    return question('There are' + days_left + 'days left in the sprint and' + tasks_left + 'tasks left to accomplish')


def ask_team_about_work():
    for i in range(team_size):
        ask_about_yesterday(i)
        ask_about_today(i)
    return 0


@ask.intent('AskAboutYesterdayIntent')
def ask_about_yesterday(i):
    speech_text = format(team_members[i]) + 'what did you do yesterday?'
    return question(speech_text)


@ask.intent('AskAboutTodayIntent')
def ask_about_today(i):
    speech_text = format(team_members[i]) + 'what are you going to do today?'
    return question(speech_text)





@ask.intent('HelloWorldIntent')
def hello_world():
    speech_text = 'Hello world'
    return statement(speech_text)


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
