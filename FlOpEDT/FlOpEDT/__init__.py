import os
import sys
from django.core.management import execute_from_command_line


def django_manage():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FlOpEDT.settings.production")
    execute_from_command_line(sys.argv)
