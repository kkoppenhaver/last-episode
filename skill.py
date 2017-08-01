import urllib
import urllib2
import json
import re
import datetime

API_BASE = "http://api.tvmaze.com/"

# Input the ID for your particular skill here
SKILL_ID = ""

def lambda_handler(event, context):
    if (event['session']['application']['applicationId'] != SKILL_ID):
        raise ValueError("Invalid Application ID")
        
    ## Handle the bare launch intent
    if(event["request"]["type"] == "LaunchRequest"):
        return build_response("T.V. Last", "Welcome to T.V. Last. Ask me about a T.V. series. For example, when was the last episode of How I Met Your Mother?", True)
        
    intent_name = event["request"]["intent"]["name"]
    
    ## Handle the help intent
    if intent_name == "AMAZON.HelpIntent":
        return build_response("T.V. Last", "Welcome to T.V. Last. Ask me about a T.V. series. For example, when was the last episode of How I Met Your Mother?", True)
    
    ## Handle the stop intent
    elif intent_name == "AMAZON.StopIntent" or intent_name == "AMAZON.CancelIntent":
        return build_response( "Thanks!", "Thanks for using T.V. Last. Goodbye!", True)
    
    elif intent_name == "GetLastEpisodeIntent":
        return query_series(event["request"]["intent"]["slots"]["series_name"]["value"])
        
def query_series(series_name):
    title = "Last Episode of " + series_name
    output_text = "You asked for the last episode of " + series_name
    should_end_session = False
    
    api_url = API_BASE + "singlesearch/shows?" + urllib.urlencode({"q": series_name})
    
    response = urllib2.urlopen(api_url)
	
    series_data = json.load(response)

    prev_ep_link = series_data["_links"]["previousepisode"]["href"]

    prev_ep_response = urllib2.urlopen(prev_ep_link)

    prev_ep_data = json.load(prev_ep_response)

    prev_ep_data["summary"] = re.sub('<[^<]+?>', '', prev_ep_data["summary"])

    prev_ep_date = datetime.datetime.strptime(prev_ep_data["airstamp"], "%Y-%m-%dT%H:%M:%S+00:00").date()
    prev_ep_date = prev_ep_date.strftime('%A %B %-d, %Y')

    output_text = prev_ep_data["name"] + ", episode " + str(prev_ep_data["number"]) + " of season " + str(prev_ep_data["season"]) + ", aired on " + prev_ep_date + ". In this episode, " + prev_ep_data["summary"]
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
    
    
    