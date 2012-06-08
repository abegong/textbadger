#from django.core.management.base import BaseCommand, CommandError
from django.core import management
from django.db import connections
from django.conf import settings

import json, glob, bson
from bson import json_util
#import pymongo.json_util

class Command(management.BaseCommand):
    args = '<...>'
    help = 'Loads database fixtures'

    def handle(self, *args, **options):
        #Flush database
        management.call_command('flush', interactive=False)

        #Sync database
        management.call_command('syncdb', interactive=False)

        #Get DB connection
        conn = connections["default"]
#        print list(conn.get_collection("auth_user").find())

        #Get all fixtures
        print 'Loading fixtures from', settings.PROJECT_PATH+'/fixtures/*'
        fixtures = glob.glob(settings.PROJECT_PATH+'/fixtures/*.json')

        for f in fixtures:
            name = f.split('/')[-1].split('.')[0]
            print '\tLoding fixtures for collection', name, '...'
            contents = json.loads(file(f).read(), object_hook=json_util.object_hook)
#            print json.dumps(contents, indent=2, default=json_util.default)
            conn.get_collection(name).insert(contents)


#        print connections.databases["default"]#.__dict__
#        conn = connections['my_db_alias']
#        print conn
#        eggs_collection = database_wrapper.get_collection('eggs')
#        eggs_collection.find_and_modify(...)

        management.call_command('syncdb', interactive=False)

