from django.http import HttpResponse, HttpResponseRedirect  # ?
from django.contrib.auth import authenticate, login, logout
from django.utils.datastructures import MultiValueDictKeyError
from django.shortcuts import render_to_response, get_object_or_404, redirect  # ?
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

import json, re, datetime, csv
from collections import defaultdict

from django.contrib.auth.models import User
from django.conf import settings  # ?
from django.db import connections
from bson.objectid import ObjectId
from pymongo.errors import InvalidId

#from tb_app.models import Codebook, Collection, Batch
#from tb_app.models import convert_csv_to_bson
from tb_app import models


def jsonifyRecord(obj, fields):
    j = {}
    for f in fields:
        j[f] = obj.__dict__[f]
    return j


def jsonifyRecords(objs, fields):
    j = []
    for o in objs:
        j.append(jsonifyRecord(o, fields))
    return j


class MongoEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


def gen_json_response(result):
    return HttpResponse(json.dumps(result, indent=2, cls=MongoEncoder), mimetype='application/json')

def sluggify(string):
    ustring = unicode.decode(string).lower()
    return re.sub(r'\W+','-',ustring)

'''
from django.core.exceptions import PermissionDenied

def superuser_only(function):
    """
    Limit view to superusers only.
    Usage:
    --------------------------------------------------------------------------
    @superuser_only
    def my_view(request):
        ...
    --------------------------------------------------------------------------
    or in urls:
    --------------------------------------------------------------------------
    urlpatterns = patterns('',
        (r'^foobar/(.*)', is_staff(my_view)),
    )
    --------------------------------------------------------------------------
    """
    def _inner(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return function(request, *args, **kwargs)
    return _inner
'''

def uses_mongo(function):
    def _inner(request, *args, **kwargs):
        mongo = connections["default"]
        return function(request, mongo, *args, **kwargs)
    return _inner

### Object list pages ########################################################


@login_required(login_url='/')
@uses_mongo
def my_account(request, mongo):
    batches = list(mongo.get_collection("tb_app_batch").find(
        {"profile.coders": {"$in": [request.user.username]}},
        fields={"profile": 1, "reports.progress": 1}, sort=[('profile.created_at', 1)]
    ))

    """
    #Find all the batches that have assignments for this use, and repackage the object for templates
    #This is sort of a hassle.  Something we would *not* have to do in cyclone.
    assignments = []
    for b in batches:
        assignments.append({
            "batch": {
                "name": b["profile"]["name"],
                "index": b["profile"]["index"],
                "_id": b["_id"],
            },
            "progress": b["reports"]["progress"]["coders"][request.user.username],
        })

    result = {
        'assignments': assignments,
    }
    """
    
    result = {
        'assignments': batches,
    }

    return render_to_response('my-account.html', result, context_instance=RequestContext(request))


@login_required(login_url='/')
@uses_mongo
def shared_resources(request, mongo):
    batches = list(mongo.get_collection("tb_app_batch").find(fields={"profile": 1, "reports": 1}, sort=[('profile.created_at', 1)]))

    for b in batches:
        models.update_batch_progress(b["_id"])

#    print list(mongo.get_collection("tb_app_codebook").find(sort=[('created_at',1)]))
    result = {
        'codebooks': list(mongo.get_collection("tb_app_codebook").find(sort=[('profile.created_at', 1)])),
        'collections': list(mongo.get_collection("tb_app_collection").find(fields={"profile":1})),#fields={"id": 1, "name": 1, "description": 1})),
        'batches': batches,
        'users': jsonifyRecords(User.objects.all(), ['username', 'first_name', 'last_name', 'email', 'is_active', 'is_superuser']),
    }
    #print json.dumps(result, indent=2, cls=MongoEncoder)

    return render_to_response('shared-resources.html', result, context_instance=RequestContext(request))


@login_required(login_url='/')
def administration(request):
    result = {
        'users': jsonifyRecords(User.objects.all(), ['username', 'first_name', 'last_name', 'email', 'is_active', 'is_superuser', 'last_login']),
    }
    return render_to_response('administration.html', result, context_instance=RequestContext(request))

### Object view pages ########################################################


@login_required(login_url='/')
@uses_mongo
def codebook(request, mongo, id_):
    result = {
        "codebook": mongo.get_collection("tb_app_codebook").find_one( {"_id": ObjectId(id_)} )}
    return render_to_response('codebook.html', result, context_instance=RequestContext(request))


@login_required(login_url='/')
@uses_mongo
def collection(request, mongo, id_):
    result = {
        "collection": mongo.get_collection("tb_app_collection").find_one(
            {"_id": ObjectId(id_)},
            {"profile": 1}
        )}
    return render_to_response('collection.html', result, context_instance=RequestContext(request))


@login_required(login_url='/')
@uses_mongo
def batch(request, mongo, id_):
    models.update_batch_progress(id_)
    models.update_batch_reliability(id_)

    batch = mongo.get_collection("tb_app_batch").find_one({"_id": ObjectId(id_)}, fields={"profile": 1, "reports": 1, "documents": 1})
    #print json.dumps(batch, cls=MongoEncoder, indent=1)
    

    result = {
        'batch': batch,
        'codebook': mongo.get_collection("tb_app_codebook").find_one(
            {"_id": ObjectId(batch["profile"]["codebook_id"])},
            {"profile":1}
        ),
        'collection': mongo.get_collection("tb_app_collection").find_one(
            {"_id": ObjectId(batch["profile"]["collection_id"])},
            {"profile":1}
        ),
        'users': jsonifyRecords(User.objects.all(), ['username', 'first_name', 'last_name', 'email', 'is_active', 'is_superuser']),
    }
    return render_to_response('batch.html', result, context_instance=RequestContext(request))


@login_required(login_url='/')
@uses_mongo
def assignment(request, mongo, batch_index):#, username):
    query = {"profile.index": int(batch_index)}
    #fields =  { "profile": 1, "documents.labels."+username: [], "documents.index": 1 }

    #print query
    #print fields

    batch = mongo.get_collection("tb_app_batch").find_one(query, {"profile": 1})
    docs = mongo.get_collection("tb_app_batch").find_one(query, {"documents": 1})["documents"]

    seq_list = []
    for d in docs:
        if request.user.username in d["labels"]:
            if d["labels"][request.user.username] == []:
                seq_list.append(d["index"])
    #print doc_list

    result = {'batch': batch, 'seq_list': seq_list}
    #print json.dumps(batch, cls=MongoEncoder, indent=2)

    return render_to_response('assignment.html', result, context_instance=RequestContext(request))


@login_required(login_url='/')
@uses_mongo
def review(request, mongo, batch_index):
    batch = mongo.get_collection("tb_app_batch").find_one(
        {"profile.index": int(batch_index)},
        {"profile":1, "reports":1, "documents":1}
    )
    codebook = mongo.get_collection("tb_app_collection").find_one(
        {"_id": ObjectId(batch["profile"]["codebook_id"])},
        {}
    )

    #print json.dumps(batch, cls=MongoEncoder, indent=2)

    #Reshape label dictionaries for display
    #! This should go in mondels.py
    label_list = []
    for doc in batch["documents"]:
        label_set = defaultdict(dict)

        for coder in doc["labels"]:
            #print "\t", coder
            answer_set = models.get_most_recent_answer_set(doc["labels"][coder])

            #Append question labels to the label_set object
            for question in answer_set:
                label_set[question][coder] = answer_set[question]

        label_list.append(label_set)

    #print json.dumps(label_list, cls=MongoEncoder, indent=2)
    result = {
        'batch': batch,
        'label_list': json.dumps(label_list, cls=MongoEncoder, indent=2),
        'label_list_2': json.dumps(batch["documents"], cls=MongoEncoder, indent=2),
    }
    #print json.dumps(batch, cls=MongoEncoder, indent=2)

    return render_to_response('review.html', result, context_instance=RequestContext(request))


### Ajax calls #################################################################

def signin(request):
    try:
        username = request.POST['username']
        password = request.POST['password']
    except MultiValueDictKeyError:
        result = {"status": "failed", "msg": "Missing email or password.  Both fields are required."}
        return HttpResponse(json.dumps(result, indent=2), mimetype='application/json')

    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            # Redirect to a success page.
            result = {"status": "success", "msg": "Sign in succeeded.  Welcome back, " + username}
        else:
            # Return a 'disabled account' error message
            result = {"status": "failed", "msg": "Sorry, this account has been disabled."}
    else:
        # Return an 'invalid login' error message.
        result = {"status": "failed", "msg": "Sorry, this username and password don't go together.  Try again?"}

    return HttpResponse(json.dumps(result, indent=2), mimetype='application/json')


#This is only kinda sorta ajax, but it belongs with signin.
def signout(request):
    logout(request)
    return redirect('/')


#! Is there an auth required decorator?
@login_required(login_url='/')
def create_account(request):
    if not request.user.is_superuser:
        return gen_json_response({"status": "failed", "msg": "You must be an administrator to create new accounts."})

    #! No response validation performed!
    if len(request.POST["first_name"]) == 0:
        return gen_json_response({"status": "failed", "msg": "First name cannot be blank."})

    try:
        new_user = User.objects.create_user(
                request.POST["username"],
                request.POST["email"],
                request.POST["username"],   # Password
                )
        new_user.first_name = request.POST["first_name"]
        new_user.last_name = request.POST["last_name"]
        new_user.is_staff = "admin" in request.POST
        new_user.is_superuser = "admin" in request.POST
        new_user.save()
    except MultiValueDictKeyError:
        return gen_json_response({"status": "failed", "msg": "Missing field."})

    return gen_json_response({"status": "success", "msg": "Successfully created account."})


@login_required(login_url='/')
def update_account(request):
    #Performed response validation
    if len(request.POST["first_name"]) == 0:
        return gen_json_response({"status": "failed", "msg": "First name cannot be blank."})

    if len(request.POST["password"]) < 4:
        return gen_json_response({"status": "failed", "msg": "Password must be at least 4 characters long."})

    #! More validation needed

    user = request.user
    try:
        user.first_name = request.POST["first_name"]
        user.last_name = request.POST["last_name"]
        user.email = request.POST["email"]
        user.set_password(request.POST["password"])
        user.save()
    except MultiValueDictKeyError:
        return gen_json_response({"status": "failed", "msg": "Missing field."})

    return gen_json_response({"status": "success", "msg": "Successfully updated account."})


@login_required(login_url='/')
def update_permission(request):
    if not request.user.is_superuser:
        return gen_json_response({"status": "failed", "msg": "You must be an administrator to change account privileges."})

    try:
        user = User.objects.get(username=request.POST["username"])
    except MultiValueDictKeyError:
        return gen_json_response({"status": "failed", "msg": "Missing field 'username.'"})

    if "active" in request.POST:
        new_status = request.POST["active"] == 'true'
        if not new_status and user.is_superuser:
            return gen_json_response({"status": "failed", "msg": "Sorry, you can't deactivate a user with admin privileges."})
        else:
            user.is_active = new_status
            if user.is_active:
                user.set_password(user.username)

    if "admin" in request.POST:
        new_status = request.POST["admin"] == 'true'
        if not new_status and User.objects.filter(is_superuser=True).count() < 2:
            return gen_json_response({"status": "failed", "msg": "Sorry, you can't remove admin privileges from the last administrator."})
        elif new_status and not user.is_active:
            return gen_json_response({"status": "failed", "msg": "Sorry, you can't grant admin privileges to an inactive user."})
        else:
            user.is_superuser = new_status
    user.save()

    return gen_json_response({"status": "success", "msg": "Successfully updated permissions.", "new_status": new_status})


@login_required(login_url='/')
@uses_mongo
def upload_collection(request, mongo):
    #Get name and description
    try:
        name = request.POST["name"]
        csv_file = request.FILES["fileInput"]
        filename = unicode(csv_file)
        description = request.POST.get("description", '')

    except MultiValueDictKeyError:
        return gen_json_response({"status": "failed", "msg": "Missing field."})

    if len(name) == 0:
        return gen_json_response({"status": "failed", "msg": "Name cannot be blank."})

    #Detect filetype
    if re.search('\.csv$', filename.lower()):
        csv_text = csv_file.read()
        documents = models.convert_document_csv_to_bson(csv_text)

    elif re.search('\.json$', filename.lower()):
        documents = json.load(file(filename, 'r'))
        #! Validate json object here

    J = models.get_new_collection_json( name, description, documents )
    mongo.get_collection("tb_app_collection").insert(J)

#    return gen_json_response({"status": "success", "msg": "Everything all good AFAICT."})
    return redirect('/shared-resources/')

@login_required(login_url='/')
@uses_mongo
def create_collection(request, mongo):
    #Get name and description
    try:
        name = request.POST["name"]
        description = request.POST.get("description", '')

    except MultiValueDictKeyError:
        return gen_json_response({"status": "failed", "msg": "Missing field."})

    #Retrieve codebooks
    total_docs = 0
    collections = {}
    for field in request.POST:
        if re.match('codebook_', field):
            try:
                val = int(request.POST[field])
                collections[field[9:]] = val
                total_docs += val
            except ValueError:
                return gen_json_response({"status": "failed", "msg": "Invalid entry in one or more codebook field(s)."})

    #Validate name
    if len(name) == 0:
        return gen_json_response({"status": "failed", "msg": "Name cannot be blank."})

    if total_docs == 0:
        return gen_json_response({"status": "failed", "msg": "Total document count must be greater than zero."})

    J = models.create_collection_json(name, description, collections)
    #print json.dumps(J, cls=MongoEncoder, indent=2)
    
    #return gen_json_response({"status": "failed", "msg": "Can't do this yet."})
    mongo.get_collection("tb_app_collection").insert(J)

    return redirect('/shared-resources/')


@login_required(login_url='/')
@uses_mongo
def get_collection_docs(request, mongo):
    #! Check for missing id
    id_ = request.POST["id"]

    try:
        collection = mongo.get_collection("tb_app_collection").find_one({"_id": ObjectId(id_)})

    # Error checking for invalid Ids
    except InvalidId:
        return gen_json_response({"status": "failed", "msg": "Not a valid collection ID."})

    return gen_json_response({
            "status": "success",
            "msg": "Everything all good AFAICT.",
            "documents": collection["documents"]
            })


@login_required(login_url='/')
@uses_mongo
def update_collection(request, mongo):
    #Get name and description
    try:
        id_ = request.POST["id_"]
        name = request.POST["name"]
        if len(request.POST["name"]) == 0:
            return gen_json_response({"status": "failed", "msg": "Name cannot be blank."})

        description = request.POST.get("description", '')

    except MultiValueDictKeyError:
        return gen_json_response({"status": "failed", "msg": "Missing field."})

    coll = mongo.get_collection("tb_app_collection")
    J = coll.find_one({"_id": ObjectId(id_)})
    J["profile"]['name'] = name
    J["profile"]['description'] = description
    mongo.get_collection("tb_app_collection").update({"_id": ObjectId(id_)}, J)

    return gen_json_response({"status": "success", "msg": "Successfully updated collection."})


@login_required(login_url='/')
@uses_mongo
def update_meta_data(request, mongo):
    #updates collection meta data
    if request.method == 'POST':
        try:
            q = request.POST
            id_ = q.get("id_")
            doc_index = q.get("doc-index")
            keys = q.getlist("key")
            values = q.getlist("value")
        except MultiValueDictKeyError:
            return gen_json_response({"status": "failed", "msg": "Missing field."})

        coll = mongo.get_collection("tb_app_collection")
        t_coll = coll.find_one({"id_": ObjectId(id_)}, {"documents.metadata": 1, "documents": {"$slice": [doc_index, 1]}})
        for key, value in zip(keys, values):
            t_coll["documents"][0]["metadata"][key] = value

        #coll.update({"id_": ObjectId(id_)}, {"documents.metadata": 1, "documents": {"$slice": [doc_index, 1]}}, {"documents.$.metadata": t_coll})
        mongo.get_collection("tb_app_collection").update(
        {"_id": ObjectId(id_)},
        {"$set": {'documents.' + str(doc_index) + '.metadata': t_coll}}
    )

        return gen_json_response({"status": "success", "msg": "Successfully updated collection."})

@login_required(login_url='/')
@uses_mongo
def create_codebook(request, mongo):
    #Get name and description
    try:
        name = request.POST["name"]
        description = request.POST["description"]

    except MultiValueDictKeyError:
        return gen_json_response({"status": "failed", "msg": "Missing field."})

    if len(name) == 0:
        return gen_json_response({"status": "failed", "msg": "Name cannot be blank."})

    J = models.get_new_codebook_json( name, description )
    mongo.get_collection("tb_app_codebook").insert(J)

    return gen_json_response({"status": "success", "msg": "Everything all good AFAICT."})


@login_required(login_url='/')
@uses_mongo
def get_codebook(request, mongo):
    id_ = request.POST["id"]
    codebook = mongo.get_collection("tb_app_codebook").find_one({"_id": ObjectId(id_)})

    #! Need error checking for invalid Ids

    return gen_json_response({
            "status": "success",
            "msg": "Successfully retrieved codebook.",
            "codebook": codebook
            })


@login_required(login_url='/')
@uses_mongo
def save_codebook(request, mongo):
    parent_id = request.POST["parent_id"]
    questions = json.loads(request.POST["questions"])["questions"]

    #Retrieve parent codebook
    coll = mongo.get_collection("tb_app_codebook")
    parent_codebook = coll.find_one({"_id": ObjectId(parent_id)})

    #!Handle parent_codebook == None

    #Create new codebook
    J = models.get_revised_codebook_json(parent_codebook, questions)
    result_id = coll.insert(J)

    #Update parent codebook
    parent_codebook["profile"]["children"].append(result_id)
    result = coll.update({"_id": ObjectId(parent_id)}, parent_codebook)

    return gen_json_response({
            "status": "success",
            "msg": "Successfully saved codebook.",
            "_id": result_id,
            "codebook": J,
            })


@login_required(login_url='/')
@uses_mongo
def update_codebook(request, mongo):
    #Get name and description
    try:
        id_ = request.POST["id_"]
        name = request.POST["name"]

        if len(name) == 0:
            return gen_json_response({"status": "failed", "msg": "Name cannot be blank."})

        description = request.POST.get("description", '')

    except MultiValueDictKeyError:
        return gen_json_response({"status": "failed", "msg": "Missing field."})

    coll = mongo.get_collection("tb_app_codebook")
    J = coll.find_one({"_id": ObjectId(id_)})
    J['profile']['name'] = name
    J['profile']['description'] = description

    mongo.get_collection("tb_app_codebook").update({"_id": ObjectId(id_)}, J)

    return gen_json_response({"status": "success", "msg": "Successfully updated collection."})


@login_required(login_url='/')
@uses_mongo
def start_batch(request, mongo):
    #Get fields from form
    try:
        codebook_id = request.POST["codebook_id"]
        collection_id = request.POST["collection_id"]
        pct_overlap = request.POST["pct_overlap"]

        coders = []
        for field in request.POST:
            if re.match('coder\d+', field):
                coders.append(request.POST[field])

        shuffle = "shuffle" in request.POST

    except MultiValueDictKeyError:
        return gen_json_response({"status": "failed", "msg": "Missing field."})

    #! Validate fields
    try:
        assert len(coders) > 0
    except (AssertionError,) as e:
        return gen_json_response({"status": "failed", "msg": "You must include at least one coder."})

    try:
        pct_overlap = float(pct_overlap)
        assert pct_overlap >= 0
        assert pct_overlap <= 100
    except (AssertionError, ValueError) as e:
        return gen_json_response({"status": "failed", "msg": "Overlap must be a percentage between 0 and 100."})

    #Get a handle to the batch collection in mongo
    coll = mongo.get_collection("tb_app_batch")

    #Count existing batches
    count = coll.find().count()

    #Retrieve the codebook and collection
    codebook = mongo.get_collection("tb_app_codebook").find_one({"_id": ObjectId(codebook_id)})
    collection = mongo.get_collection("tb_app_collection").find_one({"_id": ObjectId(collection_id)})

    batch = models.get_new_batch_json(count, coders, pct_overlap, shuffle, codebook, collection)

    batch_id = coll.insert(batch)
    models.update_batch_progress(batch_id)

    return gen_json_response({"status": "success", "msg": "New batch created."})


@login_required(login_url='/')
@uses_mongo
def submit_batch_code(request, mongo):
    #Get indexes
    try:
        batch_id = request.POST["batch_id"]
        doc_index = int(request.POST["doc_index"])

    except MultiValueDictKeyError:
        return gen_json_response({"status": "failed", "msg": "Missing field."})

    username = request.user.username

    #Construct labels object
    labels = { 'created_at' : datetime.datetime.now() }
    for field in request.POST:
        #print '\t', field, '\t', request.POST[field], '\t', re.match("Q[0-9]+", field) != None
        if re.match("Q[0-9]+", field):
            labels[field] = request.POST[field]

    #print labels
    #print doc_index, batch_id

    #!? Validate responses against codebook questions
    #! Not for now.  This would be medium hard.

    #Update DB
    coll = mongo.get_collection("tb_app_batch")

    query1 = {"_id": ObjectId(batch_id), "documents.index": doc_index}
    query2 = "documents.$.labels."+username
    mongo.get_collection("tb_app_batch").update(
        query1,
        {"$push": {query2: labels}}
    )
#    print json.dumps(batch, cls=MongoEncoder, indent=2)
    return gen_json_response({"status": "success", "msg": "Added code to batch."})

@login_required(login_url='/')
@uses_mongo
def export_batch(request, mongo, batch_id):
    #! These should be populated from a form, but said form doesn't exist yet.
    include_empty_rows = False
    include_doc_content = False

    #Retrieve the relevant objects
    batch = mongo.get_collection("tb_app_batch").find_one( {"_id": ObjectId(batch_id)} )
    documents = batch["documents"]
    collection = mongo.get_collection("tb_app_collection").find_one({"_id": ObjectId(batch["profile"]["collection_id"])} )
    codebook = mongo.get_collection("tb_app_codebook").find_one({"_id": ObjectId(batch["profile"]["codebook_id"])} )

    #Get column names...
    col_names = models.gen_codebook_column_names(codebook)
    col_index = models.gen_col_index_from_col_names(col_names)

    #Generate filename
    filename = sluggify(collection["profile"]["name"])+"-"+datetime.datetime.now().strftime("%Y-%M-%d-%H-%M-%S")+".csv"

    #Begin constructing a response
    #response = HttpResponse(mimetype='text')

    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename='+filename+'.csv'
    writer = csv.writer(response)

    #Generate and write column headers
    header = ['index', 'username']
    if include_doc_content:
        header += ['document']
    header += col_names
    writer.writerow(header)

    for i,doc in enumerate(documents):
        for coder in doc["labels"]:
            answer_set = models.get_most_recent_answer_set(doc["labels"][coder])
            if answer_set != {} or include_empty_rows:
                row = [i, coder]
                if include_doc_content:
                    row += [collection["documents"][i]["content"]]
                row += models.gen_csv_column_from_batch_labels(answer_set, col_index)
                writer.writerow(row)

    return response

@login_required(login_url='/')
def update_batch_reliability(request):
    batch_id = request.POST["batch_id"]
    
    #! Validate batch_id
    
    models.update_batch_reliability(batch_id)

    return gen_json_response({"status": "success", "msg": "Successfully updated reliability report."})


"""
@login_required(login_url='/')
@uses_mongo
def test_update_collection_metadata(request, mongo):
    collection_id = '4ff63d5d2fa6cd211b000001'
    doc_index = 0
    new_metadata = {"foo":"blahblah", "bar":7}

    mongo.get_collection("tb_app_collection").update(
        { "_id": ObjectId(collection_id) },
        { "$set": { 'documents.'+str(doc_index)+'.metadata' : new_metadata}}
    )

    result = mongo.get_collection("tb_app_collection").find_one(
        {"_id": ObjectId(collection_id)},
        {"documents":{"$slice":[doc_index,1]}}
    )

    return gen_json_response({"status": "success", "msg": "Added code to batch.", "r":result})

@login_required(login_url='/')
@uses_mongo
def variable_tester(request, mongo):
    codebook = mongo.get_collection("tb_app_codebook").find()[1]
    result = {
        'questions': codebook["questions"],
        'variables': models.get_codebook_variables_from_questions( codebook["questions"] ),
    }

    return gen_json_response({"status": "success", "msg": "Added code to batch.", "r":result})
"""
