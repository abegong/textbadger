"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.conf import settings

import json
from tb_app.models import Codebook, Collection, PrivateBatch, convert_csv_to_bson

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

    def test_convert_csv_to_bson(self):
        filename = settings.PROJECT_PATH+'/../dev/scrap/dummy-collections/collection-2959'
        csv_text = file(filename+'.csv', 'r').read()
        old_json = json.loads(file(filename+'.json', 'r').read())

        new_json = convert_csv_to_bson(csv_text)

#        self.assertEqual(old_json['name'], new_json['name'])
#        self.assertEqual(old_json['description'], new_json['description'])
        self.assertEqual(len(old_json['documents']), len(new_json['documents']))

        #! Be careful of string-to-int conversion here
        self.assertEqual(old_json['documents'], new_json['documents'])

"""
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

User.objects.create_user('lcata', email='agong@umich.edu', password='123')

user = authenticate(username='john', password='secret')
print user

user = authenticate(username='lcata', password='123')
print user
"""

"""
from tb_app.models import tbUser
tbUser.objects.create_user('lcata', email='agong@umich.edu', password='123')

user = authenticate(username='john', password='secret')
print user

user = authenticate(username='lcata', password='123')
print user



"""
