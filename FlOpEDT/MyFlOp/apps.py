import os

from django.apps import AppConfig


class MyflopConfig(AppConfig):
    name = 'MyFlOp'

    def ready(self):
        from django.conf import settings as ds

