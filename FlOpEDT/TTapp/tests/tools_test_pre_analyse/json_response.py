import json

def loadJsonDict(filename):
    f = open(filename)
    # returns JSON object as a dictionary
    response_dict = json.load(f)
    f.close()

    return response_dict

def getResponseStatus(json_response_dict):
    return json_response_dict["status"]

def getResponseType(json_response_dict):
    return json_response_dict["messages"]["type"]