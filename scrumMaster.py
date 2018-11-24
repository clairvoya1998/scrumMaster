import logging
import os
import datetime
import pickle

import boto3

from flask import Flask
from flask_ask import Ask, request, session, question, statement


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