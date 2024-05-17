import time

from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand
from django.db import DEFAULT_DB_ALIAS
from django.conf import settings


class Command(BaseCommand):
    """Django command to pause execution until database is available"""

    def handle(self, *args, **options):
        """Handle the command"""
        self.stdout.write('Waiting for database...')
        while True:
            try:
                db_conn = connections[DEFAULT_DB_ALIAS]
                db_conn.ensure_connection()
                self.stdout.write(self.style.SUCCESS('Database available!'))
                break 
            except OperationalError:
                self.stdout.write(f'Database unavailable on {settings.DATABASES["default"]["HOST"]}:{settings.DATABASES["default"]["PORT"]}, waiting 1 second...')
                time.sleep(1)