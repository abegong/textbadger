from django.db.models import Model, TextField
from djangotoolbox.fields import ListField, EmbeddedModelField, DictField
from django.contrib.auth.models import User

#! Don't even bother.  We don't need this now.
#class UserWrapper(User):
#    user = TextField()
#    owned_projects = ListField()
##    account = EmbeddedModelField('Account')
#    permissions = ListField()

class ObjectProfile(Model):
    owner = TextField()
    name = TextField()
    description = TextField()

class Codebook(Model):
    profile = EmbeddedModelField(ObjectProfile)
    questions = ListField()

class Collection(Model):
    profile = EmbeddedModelField(ObjectProfile)
    doc_list = ListField()

class PrivateBatch(Model):
    profile = EmbeddedModelField(ObjectProfile)
    codebook = TextField()
    collection = TextField()
    assignments = DictField() #e.g. {'agong': [1,2,3,4,5], 'mrchampe': [3,4,5,6,7]}
    reports = DictField()

"""
class Label(Model):
    user_id = TextField()
#! All these fields need to be set to optional
    batch_id = TextField()
    doc_id = TextField() #! Integer?
    value = DictField()
#!    timestamp = #Timestamp field....?
"""

"""
        "sharing": "",
    },
    "results": [{
        "user_id":,
        "doc_id":,
        "value": {}
        "timestamp"
    }],
    "reports": {}
}
"""

"""
class Project(Model):
    profile = EmbeddedModelField('ObjectProfile')
    permissions = DictField() #e.g. {"agong" : ["codebooks", "collections", "batches"]}
    collections = ListField()
    codebooks = ListField()
    batches = ListField()
"""

#UserWrapper.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')

"""
Codebook:{
    "profile": {
        "owner": "",
        "description": "",
        "sharing": "",
    },
    "question_array":[]
}

Collection:{
    "profile": {
        "owner": user_id,
        "description": "",
        "sharing": "",
    },
    "question_array":[]
}

Batch: {
    "profile": {
        "description": "",
        "workforce" : public/private,
        "codebook" : codebook_id, 
        "collection" : collection_id,
        "sharing": "",
    },
    "results": [{
        "user_id":,
        "doc_id":,
        "value": {}
        "timestamp"
    }],
    "reports": {}
}

"""
