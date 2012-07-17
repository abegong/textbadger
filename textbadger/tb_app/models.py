#from django.db.models import Model, TextField
#from djangotoolbox.fields import ListField, EmbeddedModelField, DictField
from django.contrib.auth.models import User
from django.db import connections
from bson.objectid import ObjectId
from pymongo.errors import InvalidId

import csv, re, json, datetime, random
from collections import defaultdict
import tb_app.kripp as kripp

def uses_mongo(function):
    def _inner(*args, **kwargs):
        mongo = connections["default"]
        return function(mongo, *args, **kwargs)
    return _inner

class MongoEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)

##############################################################################

#This is one way new collections are created
def convert_document_csv_to_bson(csv_text):
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

    documents_json = []

    #http://lethain.com/handling-very-large-csv-and-xml-files-in-python/
    print csv.field_size_limit()
    csv.field_size_limit(1000000)
    
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

        documents_json.append(j)

#    print json.dumps(documents_json, indent=2)
    return documents_json

def get_new_collection_json(name, description, documents):
    """ Create a new collection, given the name, description, and documents """
    J = {
        'profile' : {
            'name' : name,
            'description' : description,
            'created_at' : datetime.datetime.now(),
            'size' : len(documents),
        },
        'documents' : documents,
    }
    
    return J

@uses_mongo
def create_collection_json(mongo, name, description, collections):
    """ Create a new collection using documents from other collections
    
        collections is an array with the form:
            [{tb_app_collection.$id : docs to retrieve from this collection}]
    """
    coll = mongo.get_collection("tb_app_collection")
    
    documents = []    
    for id_ in collections:
        collection = coll.find_one({"_id": ObjectId(id_)})

        doc_count = collections[id_]
        doc_list = collection["documents"]
        random.shuffle( doc_list )
        
        for doc in doc_list[:doc_count]:
            doc["metadata"]["source_id"] = id_
            doc["metadata"]["source_name"] = collection["profile"]["name"]

        documents += doc_list[:doc_count]
        
    random.shuffle(documents)
    return get_new_collection_json(name, description, documents)



def get_default_codebook_questions():
    return [
        {
            "question_type": "Static text",
            "var_name": "default_question",
            "params": {
                "header_text": "<h2> New codebook </h2><p><strong>Use the controls at right to add questions.</strong></p>",
                }
        },
        {
            "question_type": "Multiple choice",
            "var_name": "mchoice",
            "params": {
                "header_text": "Here is an example of a multiple choice question.  Which answer do you like best?",
                "answer_array": ["This one", "No, this one", "A third option"],
            }
        },
        {
            "question_type": "Short essay",
            "var_name": "essay",
            "params": {
                "header_text": "Here's a short essay question.",
            }
        }
    ]

def get_new_codebook_json(name, description):
    #Construct object
    return {
        'profile' : {
            'name' : name,
            'description' : description,
            'created_at' : datetime.datetime.now(),
            'version' : 1,
            'children' : [],
            'batches' : [],
            'parent' : None,
        },
        'questions' : get_default_codebook_questions()
    }


def get_revised_codebook_json(parent_codebook, question_json):
    print parent_codebook
    J = {
        'profile' : {
            'description' : parent_codebook['profile']["description"],
            'created_at' : datetime.datetime.now(),
            'version' : parent_codebook['profile']["version"] + 1,
            'children' : [],
            'batches' : [],
            'parent' : parent_codebook['_id'],#ObjectId(parent_id),
        },
        'questions' : question_json,
    }

    if parent_codebook['profile']["children"]:
        J['profile']['name'] = parent_codebook['profile']["name"] + " (branch)"
    else:
        J['profile']['name'] = parent_codebook['profile']["name"]

    return J

def gen_codebook_column_names(codebook):
    """
        codebook should be in json format, hot off a mongodb query
    """
    
    col_names = ['created_at']
    
    for i,q in enumerate(codebook["questions"]):
        if q["var_name"]:
            var_name = "_"+q["var_name"]
        else:
            var_name = ''

        if q["question_type"] in ['Static text', 'Multiple choice', 'Check all that apply', 'Two-way scale', 'Text box', 'Short essay']:
            col_names.append("Q"+str(i+1)+var_name)

        elif q["question_type"] in ['Radio matrix', 'Checkbox matrix']:
            for j,p in enumerate(q["params"]["question_array"]):
                col_names.append("Q"+str(i+1)+"_"+str(j+1)+var_name)

        elif q["question_type"] == 'Two-way matrix':
            for j,p in enumerate(q["params"]["left_statements"]):
                col_names.append("Q"+str(i+1)+"_"+str(j+1)+var_name)

        elif q["question_type"] == 'Text matrix':
            for j,p in enumerate(q["params"]["answer_array"]):
                col_names.append("Q"+str(i+1)+"_"+str(j+1)+var_name)

        """    
        if q["question_type"] == 'Static text':
            col_names.append("Q"+str(i)+var_name)
        elif q["question_type"] == 'Multiple choice':
            col_names.append("Q"+str(i)+var_name)
        elif q["question_type"] == 'Check all that apply':
            col_names.append("Q"+str(i)+var_name)
        elif q["question_type"] == 'Two-way scale':
            col_names.append("Q"+str(i)+var_name)
        elif q["question_type"] == 'Radio matrix':
            for j,p in enumerate(q["params"]["question_array"]):
                col_names.append("Q"+str(i)+"_"+str(j)+var_name)
            
        elif q["question_type"] == 'Checkbox matrix':
            for j,p in enumerate(q["params"]["question_array"]):
                col_names.append("Q"+str(i)+"_"+str(j)+var_name)

        elif q["question_type"] == 'Two-way matrix':
            for j,p in enumerate(q["params"]["left_statements"]):
                col_names.append("Q"+str(i)+"_"+str(j)+var_name)

        elif q["question_type"] == 'Text box':
            col_names.append("Q"+str(i)+var_name)
        elif q["question_type"] == 'Short essay':
            col_names.append("Q"+str(i)+var_name)
        elif q["question_type"] == 'Text matrix':
            for j,p in enumerate(q["params"]["answer_array"]):
                col_names.append("Q"+str(i)+"_"+str(j)+var_name)
        """

    return col_names

def gen_col_index_from_col_names(col_names):
    return dict([(v,k) for (k,v) in enumerate(col_names)])

def gen_csv_column_from_batch_labels(labels, col_index):
    csv_col = [None for i in range(len(col_index))]
    print labels
    for q in labels:
        csv_col[col_index[q]] = labels[q]
    return csv_col

### Batches ###################################################################

def get_batch_documents_json(coders, pct_overlap, shuffle, collection):
    k = len(collection["documents"])
    overlap = int((k * pct_overlap) / 100)
    
    import random
    doc_ids = range(k)
    if shuffle:
          # ? This can stay here until we do our DB refactor.
        random.shuffle(doc_ids)
    shared = doc_ids[:overlap]
    unique = doc_ids[overlap:]

    #Construct documents object
    documents = []
    empty_labels = dict([(x, []) for x in coders])
    for i in shared:
        documents.append({
            'index': i,
#            'content': collection["documents"][i]["content"],
            'labels': empty_labels
        })

    for i in unique:
        documents.append({
            'index': i,
#            'content': collection["documents"][i]["content"],
            'labels': { coders[i%len(coders)] : [] }
            #Populate the list with a random smattering of fake labels
            #'labels': {coders[i % len(coders)]: random.choice([None for x in range(2)] + range(20))}
        })
    if shuffle:
        random.shuffle(documents)

    return documents

def get_new_batch_json(count, coders, pct_overlap, shuffle, codebook, collection):
    #construct profile object
    profile = {
        'name': 'Batch ' + str(count + 1),
        'description': collection["profile"]["name"][:20] + " * " + codebook["profile"]["name"][:20] + " (" + str(codebook["profile"]["version"]) + ")",
        'index': count + 1,
        'codebook_id': codebook['_id'],#codebook_id,
        'collection_id': collection['_id'],#collection_id,
        'coders': coders,
        'pct_overlap': pct_overlap,
        'shuffle': shuffle,
        'created_at': datetime.datetime.now(),
    }
    
    documents = get_batch_documents_json(coders, pct_overlap, shuffle, collection)

    #Construct batch object
    batch = {
        'profile' : profile,
        'documents': documents,
        'reports': {
            'progress': {},
            'reliability': {},
        },
    }
    
    return batch

def get_most_recent_answer_set(answer_set_list):
    #Get the most recent answer set for this coder (important if the coder used did an "undo")
    
    most_recent_answer_set = {}
    most_recent_date = None
    for answer_set in answer_set_list:
        if not most_recent_date or answer_set["created_at"] > most_recent_date:
            most_recent_answer_set = answer_set
            most_recent_date = answer_set["created_at"]

    return most_recent_answer_set

#! This is the only method that includes a DB connection right now.
#! Eventually, we might want to do more like this
def update_batch_progress(id_):
    #Connect to the DB
    conn = connections["default"]
    coll = conn.get_collection("tb_app_batch")

    #Retrieve the batch
    batch = coll.find_one({"_id": ObjectId(id_)})
#    print json.dumps(batch, indent=2, cls=MongoEncoder)

    #Scaffold the progress object
    coders = batch["profile"]["coders"]
    progress = {
        "coders": dict([(c, {"assigned":0, "complete":0}) for c in coders]),
        "summary": {}
    }

    #Count total and complete document codes
    assigned, complete = 0, 0
    for doc in batch["documents"]:
        for coder in doc["labels"]:
            assigned += 1
            progress["coders"][coder]["assigned"] += 1

            if doc["labels"][coder] != []:
                complete += 1
                progress["coders"][coder]["complete"] += 1

    #Calculate percentages
    for coder in progress["coders"]:
        c = progress["coders"][coder]
        c["percent"] = round(float(100 * c["complete"]) / c["assigned"], 1)

    progress["summary"] = {
        "assigned": assigned,
        "complete": complete,
        "percent": round(float(100 * complete) / assigned, 1),
    }

    batch["reports"]["progress"] = progress
#    print json.dumps(progress, indent=2, cls=MongoEncoder)

    coll.update({"_id": ObjectId(id_)}, batch)
#    print result#json.dumps(progress, indent=2, cls=MongoEncoder)

def convert_batch_to_2d_arrays(batch, col_names, missing_val=None):
    #2-D arrays wrapped in a dictionary : [question][document][coder]
    coder_index = dict([(c,i) for i,c in enumerate(batch["profile"]["coders"])])
    
    #Create empty arrays
    code_arrays = dict([ (n, [[missing_val for c in coder_index] for d in batch["documents"]]) for n in col_names])
    
    for i, doc in enumerate(batch["documents"]):
        for coder in doc["labels"]:
            answer_set = get_most_recent_answer_set(doc["labels"][coder])
#            print answer_set
            for question in answer_set:
                if question in code_arrays.keys():
                    try:
#                        print '\t'.join([str(x) for x in [question, i, coder, answer_set[question]]])
                        code_arrays[question][i][coder_index[coder]] = float(answer_set[question])
                    except ValueError:
                        code_arrays[question][i][coder_index[coder]] = missing_val

    return code_arrays
    


@uses_mongo
def update_batch_reliability(mongo, batch_id):
    batch = mongo.get_collection("tb_app_batch").find_one({"_id": ObjectId(batch_id)})
    codebook = mongo.get_collection("tb_app_codebook").find_one({"_id": ObjectId(batch["profile"]["codebook_id"])})
    
    col_names = gen_codebook_column_names(codebook)
    col_names.remove("created_at")

    data_arrays = convert_batch_to_2d_arrays(batch, col_names)

    summary = {}
    for q in data_arrays:
        print q, '\t', kripp.alpha(data_arrays[q], kripp.interval)
        summary[q] = kripp.alpha(data_arrays[q], kripp.interval)
    
    #print json.dumps(code_array, indent=2, cls=MongoEncoder)

    #Scaffold the reliability object
    reliability = {
        #"docs": {},
        #"coders": dict([(c, {}) for c in coders]),
        "summary": summary,
    }
    
    
#    #Create confusion matrices
#    for question in code_array:
#        conf_m = get_confusion_matrix(code_array[question])
#        reliability["summary"][question] = kripp_alpha( conf_m )


#    for q in code_array:
#        summary, coders, docs = kripp_alpha(code_array[q])
#        reliability["summary"][q] = summary

    batch["reports"]["reliability"] = reliability
    print json.dumps(reliability, indent=2, cls=MongoEncoder)

    mongo.get_collection("tb_app_batch").update(
        { "_id": ObjectId(batch_id) },
        { "$set": { 'reports.reliability' : reliability}}
    )

    #coll.update({"_id": ObjectId(id_)}, batch)


