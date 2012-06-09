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

##############################################################################

import csv, re, json

def convert_csv_to_bson(csv_text):
    C = csv.reader(csv.StringIO(csv_text))
    H = C.next()
    print H

    
    url_index, content_index = None, None
    if 'url' in H:
        url_index = H.index('url')
    if 'content' in H:
        content_index = H.index('content')

    if url_index==None and content_index==None:
        raise Exception('You must specify either a "url" column or a "content" column')

    meta_fields = {}
    for h in H:
        if re.match('META_', h):
            name = re.sub('^META_', '', h)
            index = H.index(h)
            if name in meta_fields:
                raise Exception('Duplicate META_ name : '+name)
            meta_fields[name] = index

#    print json.dumps(meta_fields, indent=2)

    J = {
#        'name' : None,
#        'description': None,
        'documents' : []
    }

    for row in C:
        j = {}

        if url_index != None:
            j['url'] = row[url_index]
        elif content_index != None:
            j['content'] = row[content_index]

        m = {}
        for f in meta_fields:
            #! Maybe include other missing values here
            if meta_fields[f] != '':
                m[f] = row[meta_fields[f]]
        if m != {}:
            j["metadata"] = m

        J['documents'].append(j)

    print json.dumps(J, indent=2)
    return J



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
