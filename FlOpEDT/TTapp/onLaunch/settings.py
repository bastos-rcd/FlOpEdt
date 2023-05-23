import json
import os

module_dir = os.path.abspath(__file__)
SETTINGS_DIR = os.path.join(os.path.dirname(module_dir),'settings.json')
def settings():
    f = open(SETTINGS_DIR)
    data = json.load(f)
    return data 
