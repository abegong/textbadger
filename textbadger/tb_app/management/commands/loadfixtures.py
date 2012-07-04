#from django.core.management.base import BaseCommand, CommandError
from django.core import management
#from django.db import connections
from django.conf import settings

import json, glob, bson
from bson import json_util
#import pymongo.json_util

from pymongo import Connection

class Command(management.BaseCommand):
    """Flush and initialize, or re-initialize, the database."""
    args = '<...>'
    help = 'Loads database fixtures'

    def handle(self, *args, **options):        
        #Get DB connection
        #conn = connections["default"]
        db_name = settings.DATABASES['default']['NAME']
        conn = Connection()

        #Flush database
        #management.call_command('flush', interactive=False)
        conn.drop_database(db_name)

        #Sync database
        management.call_command('syncdb', interactive=False)

        #Ensure indexes
#        collection = mongo['database']['hosts']
        #This is right...
        conn[db_name]['tb_app_batch'].ensure_index('profile.index', unique=True)

        #Get all fixtures
        print 'Loading fixtures from', settings.PROJECT_PATH+'/fixtures/*'
        fixtures = glob.glob(settings.PROJECT_PATH+'/fixtures/*.json')

        for f in fixtures:
            name = f.split('/')[-1].split('.')[0]
            print '\tLoading fixtures for collection', name, '...'
            contents = json.loads(file(f).read(), object_hook=json_util.object_hook)
            #conn.get_collection(name).insert(contents)
            conn[db_name][name].insert(contents)


#        management.call_command('syncdb', interactive=False)

