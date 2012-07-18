"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.conf import settings

from django.test.client import Client
from django.contrib.auth.models import User
from django.db import connections

import json
from tb_app import models

class SimpleTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        self.mongo = connections["default"]

    def test_convert_csv_to_bson(self):
        filename = settings.PROJECT_PATH+'/../dev/scrap/dummy-collections/collection-2959'
        csv_text = file(filename+'.csv', 'r').read()
        old_json = json.loads(file(filename+'.json', 'r').read())
        
        new_json = models.convert_document_csv_to_bson(csv_text)
        
        self.assertEqual(len(old_json['documents']), len(new_json))

        #! Be careful of string-to-int conversion here
        self.assertEqual(old_json['documents'], new_json)

    def test_pageload_status(self):
        print
        self.client.login(username='john', password='johnpassword')

        url_list = ['/', '/about/', '/my-account/', '/shared-resources/']
        #!!!!! self.mongo.get_collection("tb_app_collection").find({},{})
        
        for url in url_list:
            print 'Attempting to load url', url
            response = self.client.get(url)
            self.assertEqual( response.status_code, 200 )

        """
        url(r'^$', TemplateView.as_view(template_name="home.html")),
        url(r'^sign-in/$', TemplateView.as_view(template_name="sign-in.html")),
        url(r'^about/$', TemplateView.as_view(template_name="about.html")),

        #Object list pages
        url(r'^my-account/$', 'textbadger.tb_app.views.my_account' ),
        url(r'^shared-resources/$', 'textbadger.tb_app.views.shared_resources' ),
        url(r'^administration/$', 'textbadger.tb_app.views.administration' ),

        #Object view pages
        url(r'^codebook/(.*)/$', 'textbadger.tb_app.views.codebook' ),
        url(r'^collection/(.*)/$', 'textbadger.tb_app.views.collection' ),
        
        url(r'^batch/(.*)/export/$', 'tb_app.views.export_batch'),
        url(r'^batch/(.*)/$', 'textbadger.tb_app.views.batch' ),

        #Assignment and review page(s)
        url(r'^assignment/(.*)/(.*)$', 'textbadger.tb_app.views.assignment' ),
        url(r'^review/(.*)/$', 'textbadger.tb_app.views.review' ),
        """

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
