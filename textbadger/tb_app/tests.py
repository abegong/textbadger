"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

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
