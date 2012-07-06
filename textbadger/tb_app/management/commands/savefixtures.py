from django.core import management
from django.conf import settings

import json, glob, bson
from bson import json_util
#import pymongo.json_util
import subprocess

from pymongo import Connection

class Command(management.BaseCommand):
    """Dump auth_user, tb_app_codebook, tb_app_collection, and tb_app_batch collections to files."""
    args = '<...>'
    help = 'Dumps database fixtures as json'

    def handle(self, *args, **options):
        #Get DB connection
        db_name = settings.DATABASES['default']['NAME']
        conn = Connection()

        try:
            path = args[0]
        except IndexError:
            path = './'

        for x in ['auth_user', 'tb_app_codebook', 'tb_app_collection', 'tb_app_batch']:
            print '=== Exporting collection :', x, '==='
            command_string = 'mongoexport -d textbadger -c '+x+' --jsonArray -o '+path+x+'.json'
            subprocess.call(command_string.split(' '))
