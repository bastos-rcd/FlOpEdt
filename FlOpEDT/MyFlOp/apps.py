from django.apps import AppConfig
import os

class MyflopConfig(AppConfig):
    name = 'MyFlOp'

    def ready(self):
        from django.conf import settings as ds

