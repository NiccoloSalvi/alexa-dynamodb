from __future__ import print_function
import boto3

client = boto3.resource('dynamodb')
table = client.Table('YOUR_TABLE_NAME')

def build_speechlet_response(output, should_end_session):
    return {
        'outputSpeech': { 'type': 'PlainText', 'text': output },
        'shouldEndSession': should_end_session
    }
    
def build_response(speechlet_response):
    return { 'version': '1.0', 'response': speechlet_response }
    
def WelcomeHandler():
    speech_output = "Bentornato!"
    shouldEndSession = False
    
    return build_response(build_speechlet_response(speech_output, shouldEndSession))

def MarksHandler(intent):
    last_subject = intent['slots']['subject']['value']
    last_mark = intent['slots']['mark']['value']
    
    getItem = table.get_item(Key = { 'subject': last_subject })
    marks = float(getItem['Item']['marks'])
    num = getItem['Item']['num']
    num += 1
    marks += float(last_mark)
    var = table.put_item(Item = { 'subject': last_subject, 'marks': str(marks), 'num': num })
    
    if float(last_mark) > 8:
        speech_output = "Ottimo, continua così!"
    else:
        speech_output = "OK, ma potevi fare di meglio"
    shouldEndSession = True
    
    return build_response(build_speechlet_response(speech_output, shouldEndSession))
    
def AverageHandler(intent):
    last_subject = intent['slots']['subject']['value']
    
    getItem = table.get_item(Key = { 'subject': last_subject })
    marks = float(getItem['Item']['marks'])
    num = float(getItem['Item']['num'])
    
    average = round((marks / num), 2)
    
    speech_output = "La tua media in " + last_subject + " è " + str(average)
    shouldEndSession = True
    
    return build_response(build_speechlet_response(speech_output, shouldEndSession))
    
def ResetSubjectHanlder(intent):
    last_subject = intent['slots']['subject']['value']

    var = table.put_item(Item = { 'subject': last_subject, 'marks': 0, 'num': 0 })
     
    speech_output = "OK, ho azzerato voti e la media di " + last_subject
    shouldEndSession = True
    
    return build_response(build_speechlet_response(speech_output, shouldEndSession))
    
def ResetAllHanlder(intent):
    for i in range(len(subjects)):
        var = table.put_item(Item = { 'subject': subjects[i], 'marks': 0, 'num': 0 })
    
    speech_output = "OK, ho azzerato i voti e le medie di tutte le materie!"
    shouldEndSession = True
    
    return build_response(build_speechlet_response(speech_output, shouldEndSession))

def HelpHandler():
    speech_output = "Puoi aggiungere un voto o chiedermi di calcolare la media di una materia. Come posso aiutarti?"
    should_end_session = False
    
    return build_response(build_speechlet_response(speech_output, should_end_session))
    
def handle_session_end_request():
    speech_output = "A presto!" 
    should_end_session = True
    
    return build_response(build_speechlet_response(speech_output, should_end_session))

def on_session_started(session_started_request, session):
    pass

def on_launch(launch_request, session):
    return WelcomeHandler()
    
def find_intent(intent_name):
    for i in range(len(intents)):
        if intent_name == intents[i][0]:
            return i
    return -1

def on_intent(intent_request, session):
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
    
    index = find_intent(intent_name)
    if index != -1:
        current_intent = intents[index][1]
        return current_intent(intent)
    else:
        if intent_name == "AMAZON.HelpIntent":
            return HelpHandler()
        elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
            return handle_session_end_request()
        else:
            raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    print("on_session_ended requestId=" + session_ended_request['requestId'] + ", sessionId=" + session['sessionId'])

def lambda_handler(event, context):
    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},event['session'])
    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])

intents = [
    ["Marks", MarksHandler],
    ["Average", AverageHandler],
    ["ResetSubject", ResetSubjectHanlder],
    ["ResetAll", ResetAllHanlder]
]

#YOUR SUBJECTS, THE SAME YOU ADD IN THE AMAZON-DB TABLE
subjects = [
    "",
    "",
    "",
    "",
    ""
]
