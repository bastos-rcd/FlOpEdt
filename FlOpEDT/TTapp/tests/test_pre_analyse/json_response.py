import json

class JsonResponse: # TODO : est-ce necessaire de faire une classe ? non
    def loadJsonDict(self, filename):
        f = open(filename)
        # returns JSON object as a dictionary
        response_dict = json.load(f)
        f.close()

        return response_dict

    def getResponseStatus(self, json_response_dict):
        return json_response_dict["status"]

    def getResponseType(self, json_response_dict):
        return json_response_dict["messages"]["type"]