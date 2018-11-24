import logging
import os

from flask import Flask
from flask_ask import Ask, request, session, question, statement


app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger('flask_ask').setLevel(logging.DEBUG)

team_members_size = 0


@ask.launch
def launch():
    speech_text = "Hey guys. Here I am, Alexa, your Scrum Master. What's your project?"
    return question(speech_text).reprompt(speech_text)

@ask.intent('NewProjectIntent')
def get_new_project():
    speech_text = 'Please confirm the name of your new project.'
    return statement(speech_text)

@ask.intent('ProjectNameIntent')
def new_project(Text):
    if ((Text) in array):
        speech_text = "I have found an existed project, do you want to continue that session?"
    else:
        speech_text = 'You said: {}, what a great name, shall we start the meeting?'.format(Text)
        # add Text to the array
    return question(speech_text).reprompt(speech_text)

#set up project
@ask.intent('TeamSizeIntent', convert = {"answer": int})
def ask_team_size():
    speech_text = "How many in the team?"
    team_members_size = answer
    return question(speech_text).reprompt(speech_text)

@ask.intent('HelloWorldIntent')
def hello_world():
    speech_text = 'Hello world'
    return statement(speech_text)

@ask.intent('AMAZON.HelpIntent')
def help():
    speech_text = 'You can say hello to me!'
    return question(speech_text).reprompt(speech_text)


#STAND UP MEETING
#Alexa, where's my scrum master
#Hello, what's your project
#projectName
#IF NOT END OF SPRINT
#i THINK it's time for a stand up meeting
@ask.intent('StandUpMeetingIntent')
def start_stand_up():
    standup_meeting = True
    speech_text = "Great. It's time for the daily stand up. Let's take attendance."
    return question(speech_text).reprompt(speech_text).simple_card('Attendance', speech_text)

def take_attendance(self):
    for i in range(team_members_size):
        attendance(i)
     return 0

@ask.intent("AttendanceIntent")
def attendance(self, i):
    speech_text = "<p>{}</p>".format(team_members[i])
    # check user says "Here"
    # else "Oh no. user is not here."
    return question(speech_text)


@ask.intent('SprintDateIntent')
def sprint_update():
    days_left = 5 # sprint end date - current date
    tasks_left = 5
    return statement('There are' + days_left + 'days left in the sprint and' + tasks_left + 'tasks left to accomplish')


def ask_team_about_work():
    for i in range(team_members_size):
        ask_about_yesterday(i)
        ask_about_today(i)
    return 0


@ask.intent('AskAboutYesterdayIntent')
def ask_about_yesterday(self, i):
    speech_text = format(team_members[i]) + 'what did you do yesterday?'
    return question(speech_text)


@ask.intent('AskAboutTodayIntent')
def ask_about_today(self, i):
    speech_text = format(team_members[i]) + 'what are you going to do today?'
    return question(speech_text)

@ask.session_ended
def session_ended():
    return "{}", 200


if __name__ == '__main__':
    if 'ASK_VERIFY_REQUESTS' in os.environ:
        verify = str(os.environ.get('ASK_VERIFY_REQUESTS', '')).lower()
        if verify == 'false':
            app.config['ASK_VERIFY_REQUESTS'] = False
    app.run(debug=True)
