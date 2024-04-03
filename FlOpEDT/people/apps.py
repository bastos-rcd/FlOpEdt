# -*- coding: utf-8 -*-


from django.apps import AppConfig


class PeopleConfig(AppConfig):
    name = "people"

    def ready(self):
        import people.signals  # pylint: disable=import-outside-toplevel, unused-import
