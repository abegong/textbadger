#from django.core.management.base import BaseCommand, CommandError
from django.core import management
from django.db import connections
from django.conf import settings

import json, glob, bson
from bson import json_util
#import pymongo.json_util

class Command(management.BaseCommand):
    """Flush and initialize, or re-initialize, the database."""
    args = '<...>'
    help = 'Loads database fixtures'

    def handle(self, *args, **options):
        #Flush database
        management.call_command('flush', interactive=False)

        #Sync database
        management.call_command('syncdb', interactive=False)

        #Get DB connection
        conn = connections["default"]

        #Get all fixtures
        print 'Loading fixtures from', settings.PROJECT_PATH+'/fixtures/*'
        fixtures = glob.glob(settings.PROJECT_PATH+'/fixtures/*.json')

        for f in fixtures:
            name = f.split('/')[-1].split('.')[0]
            print '\tLoding fixtures for collection', name, '...'
            contents = json.loads(file(f).read(), object_hook=json_util.object_hook)
            conn.get_collection(name).insert(contents)

        management.call_command('syncdb', interactive=False)

