import json
import os

SETTINGS_DIR = os.path.join(os.getcwd(),'TTapp/onLaunch/settings.json')
def settings():
    f = open(SETTINGS_DIR)
    data = json.load(f)
    return data 
