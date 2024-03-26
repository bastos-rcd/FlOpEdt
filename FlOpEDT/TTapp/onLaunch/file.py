import os
import shutil
from pathlib import Path

from django.conf import settings as ds

from MyFlOp.colors import Tcolors
from TTapp.onLaunch.settings import settings

TEMP_DIR = os.path.join(ds.TMP_DIRECTORY,'constraints')
CLEAR_TEMP_FILES = settings()["clearTempFile"]

LANG_LIST = settings()["langs"]


def initTemp():
    
    if( not(Path.exists(Path(TEMP_DIR))) ):
        print(Tcolors.WARNING,"Temp dir does not exist, creating it",Tcolors.ENDC)
        try:
            os.mkdir(TEMP_DIR)
        except:
            print(Tcolors.WARNING,"Temp dir has not been    created, aborting creation",Tcolors.ENDC)
            return
    purgeTempFolder()
    

    

def purgeTempFolder():
    if(CLEAR_TEMP_FILES):
        for l in LANG_LIST:
            lang_dir_path = os.path.join(TEMP_DIR,l)

            try:
                shutil.rmtree(lang_dir_path)
            except:
                print(Tcolors.OKBLUE,"Directory",lang_dir_path,"does not exist",Tcolors.ENDC)

            try:
                os.mkdir(lang_dir_path)
            except:
                print(Tcolors.WARNING,"Directory",lang_dir_path,"has not been created",Tcolors.ENDC)
    else:
        print(Tcolors.WARNING,"Temp directory will not be cleared, you can modify it in : \n","FlopEDT/MyFlOp/apps.py", Tcolors.ENDC)

