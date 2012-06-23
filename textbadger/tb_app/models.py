from django.db.models import Model, TextField
from djangotoolbox.fields import ListField, EmbeddedModelField, DictField
from django.contrib.auth.models import User

#! Don't even bother.  We don't need this now.
#class UserWrapper(User):
#    user = TextField()
#    owned_projects = ListField()
##    account = EmbeddedModelField('Account')
#    permissions = ListField()

#class ObjectProfile(Model):
#    owner = TextField()
#    name = TextField()
#    description = TextField()

class Codebook(Model):
    name = TextField()
    description = TextField()
    questions = ListField()

class Collection(Model):
#    profile = EmbeddedModelField(ObjectProfile)
    name = TextField()
    description = TextField()
    documents = ListField()

class Batch(Model):
    codebook = TextField()
    collection = TextField()
    assignments = DictField() #e.g. {'agong': [1,2,3,4,5], 'mrchampe': [3,4,5,6,7]}
    reports = DictField()

##############################################################################

import csv, re, json

def convert_csv_to_bson(csv_text):
    C = csv.reader(csv.StringIO(csv_text))

    #Parse the header row
    H = C.next()

    #Capture the url/content column index
    url_index, content_index = None, None
    if 'url' in H:
        url_index = H.index('url')
    if 'content' in H:
        content_index = H.index('content')

    if url_index==None and content_index==None:
        raise Exception('You must specify either a "url" column or a "content" column in the .csv header.')

    #Identify metadata_fields
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

    #For each row in the collection
    for row in C:
        j = {}

        #Grab the content or url
        #If both are present, url gets precedence
        if url_index != None:
            j['url'] = row[url_index]
        elif content_index != None:
            j['content'] = row[content_index]

        #Grab metadata fields
        m = {}
        for f in meta_fields:
            #Don't include missing values
            #! Maybe include other missing values here
            if meta_fields[f] != '':
                m[f] = row[meta_fields[f]]

        #Don't include empty metadata objects
        if m != {}:
            j["metadata"] = m

        J['documents'].append(j)

#    print json.dumps(J, indent=2)
    return J


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
