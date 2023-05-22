
import json
import re
import os
from pathlib import Path
from MyFlOp.colors import Tcolors
from TTapp.onLaunch.settings import settings
LANG_LIST = settings()["langs"]


def createDiscardFile():
    if os.environ.get('RUN_MAIN') != 'true':
            #lists of discarted files
            corrupted = []
            unavailable_pics = []
            #available languages
            path = 'FlOpEDT/TTapp/TTConstraints/doc/'
            for language in LANG_LIST:
                language += "/"
                entries = next(os.walk(path+language))[2]
                for file_name in entries:
                    f = open(path+language+file_name,'r')
                    fString = f.read()
                    #Discard files with components tags
                    if((re.findall("<[ ]*component[ ]*",fString))):
                        corrupted.append(file_name)
                    #Discard files with unavailable pics's path
                    else:
                        invalid_path = False
                        founds = re.findall("(?:[!]\[(.*?)\])\((\.\.(.*?))\)",fString)
                        for found in founds:
                            if(not invalid_path):
                                pic = found[2]
                                pathPic = Path(path+pic)
                                if(not pathPic.is_file()):
                                    invalid_path = True
                        if(invalid_path):
                            unavailable_pics.append(file_name)
                    f.close()
            #Warning in red when a file is corrupted
            if(len(corrupted)>0):
                print(Tcolors.FAIL,"WARNING!! Check corrupted files:",Tcolors.ENDC)
                for file in corrupted:
                    print(" - "+file)
            #Warning to see discarded files
            if(len(unavailable_pics)>0):
                print(Tcolors.WARNING,"Files discarded because of an incorrect pic's path:",Tcolors.ENDC)
                for file in unavailable_pics:
                    print(" - "+file)

            #Append lists of discarded files and write them in a json
            list_discarded = list(set().union(list(corrupted), list(unavailable_pics)))
            version_json = json.dumps(list_discarded)
            with open("discarded.json",'w') as file:
                file.write('{"discarded": '+version_json+'}')
            file.close()
