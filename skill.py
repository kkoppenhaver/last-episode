import urllib
import urllib2
import json
import re
import datetime

API_BASE = "http://api.tvmaze.com/"

def lambda_handler(event, context):
    if (event['session']['application']['applicationId'] != "amzn1.ask.skill.c73a51ae-b7c0-4082-b1d8-55a357eddae5"):
        raise ValueError("Invalid Application ID")
        
    ## Handle the bare launch intent
    if(event["request"]["type"] == "LaunchRequest"):
        return build_response("Last Episode", "Welcome to Last Episode. Ask me about a T.V. series. For example, when was the last episode of How I Met Your Mother?", False)
        
    intent_name = event["request"]["intent"]["name"]
    
    ## Handle the help intent
    if intent_name == "AMAZON.HelpIntent" or intent_name == "TroubleshootIntent":
        return build_response("Last Episode", "Welcome to Last Episode. Ask me about a T.V. series. For example, when was the last episode of How I Met Your Mother?", False)
    
    ## Handle the stop intent
    elif intent_name == "AMAZON.StopIntent" or intent_name == "AMAZON.CancelIntent":
        return build_response( "Thanks!", "Thanks for using Last Episode. Goodbye!", True)
    
    elif intent_name == "GetLastEpisodeIntent":
        if "value" in event["request"]["intent"]["slots"]["series_name"] and event["request"]["intent"]["slots"]["series_name"]["value"] != '':
            return query_series(event["request"]["intent"]["slots"]["series_name"]["value"])
        else:
            return build_response("Last Episode", "Sorry, I didn't quite get that. Ask me about a T.V. series. For example, when was the last episode of How I Met Your Mother?", False)
        
def query_series(series_name):
    title = "Last Episode of " + series_name
    output_text = "You asked for the last episode of " + series_name
    should_end_session = True
    
    api_url = API_BASE + "singlesearch/shows?" + urllib.urlencode({"q": series_name})
    
    try:
        response = urllib2.urlopen(api_url)
    except urllib2.HTTPError, e:
        return build_response("Last Episode", "Sorry, I didn't quite get that. Ask me about a T.V. series. For example, when was the last episode of How I Met Your Mother?", False)
    
    series_data = json.load(response)
    
    prev_ep_link = series_data["_links"]["previousepisode"]["href"]

    prev_ep_response = urllib2.urlopen(prev_ep_link)

    prev_ep_data = json.load(prev_ep_response)
    
    if(prev_ep_data["summary"]):
        prev_ep_data["summary"] = re.sub('<[^<]+?>', '', prev_ep_data["summary"])

    prev_ep_date = datetime.datetime.strptime(prev_ep_data["airstamp"], "%Y-%m-%dT%H:%M:%S+00:00").date()
    prev_ep_date = prev_ep_date.strftime('%A %B %-d, %Y')
    
    prev_ep_summary = prev_ep_data["summary"]
    
    if(prev_ep_summary and prev_ep_summary != ''):
        prev_ep_summary = "In this episode, " + prev_ep_summary
    else:
        prev_ep_summary = "No summary was found."

    output_text = prev_ep_data["name"] + ", episode " + str(prev_ep_data["number"]) + " of season " + str(prev_ep_data["season"]) + ", aired on " + prev_ep_date + ". " + prev_ep_summary
    return build_response(title, output_text, should_end_session)
    
def build_response( title, output_text, should_end_session ):
    return {
      "version": "1.0",
      "response": {
        "outputSpeech": {
          "type": "PlainText",
          "text": output_text
        },
        "card": {
          "content": output_text,
          "title": title,
          "type": "Simple"
        },
        "reprompt": {
          "outputSpeech": {
            "type": "PlainText",
            "text": ""
          }
        },
        "shouldEndSession": should_end_session
      },
      "sessionAttributes": {}
    }