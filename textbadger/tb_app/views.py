from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.utils.datastructures import MultiValueDictKeyError 
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
import json, re, datetime

from django.contrib.auth.models import User
from django.conf import settings
from django.db import connections
from bson.objectid import ObjectId
from tb_app.models import Codebook, Collection, PrivateBatch, convert_csv_to_bson

def jsonifyRecord( obj, fields ):
    j = {}
    for f in fields:
        j[f] = obj.__dict__[f]
    return j

def jsonifyRecords( objs, fields ):
    j = []
    for o in objs:
        j.append(jsonifyRecord(o, fields))
    return j

import json
class MongoEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)

def gen_json_response( result ):
    return HttpResponse(json.dumps(result, indent=2, cls=MongoEncoder), mimetype='application/json')

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
### Object list pages ########################################################

@login_required(login_url='/')
def my_account(request):
    result = {
        'assignments' : []#! Get assignments from DB
    }
    return render_to_response('my-account.html', result, context_instance=RequestContext(request))

@login_required(login_url='/')
def shared_resources(request):
    conn = connections["default"]
    result = {
        'codebooks' : list(conn.get_collection("tb_app_codebook").find(sort=[('created_at',1)])),
        'collections' : list(conn.get_collection("tb_app_collection").find(fields={"id":1, "name":1, "description":1})),
        'batches' : jsonifyRecords(PrivateBatch.objects.all(), ['username', 'first_name', 'last_name', 'email']),
        'users' : jsonifyRecords(User.objects.all(), ['username', 'first_name', 'last_name', 'email', 'is_active', 'is_superuser']),
    }

    return render_to_response('shared-resources.html', result, context_instance=RequestContext(request))

@login_required(login_url='/')
def administration(request):
    result = {
        'users' : jsonifyRecords(User.objects.all(), ['username', 'first_name', 'last_name', 'email', 'is_active', 'is_superuser']),
    }
    return render_to_response('administration.html', result, context_instance=RequestContext(request))

### Object view pages ########################################################

@login_required(login_url='/')
def codebook(request, id_):
    conn = connections["default"] 
    result = {
        "codebook": conn.get_collection("tb_app_codebook").find_one(
            {"_id":ObjectId(id_)}
#            {"name":1, "description": 1}
        )}
    return render_to_response('codebook.html', result, context_instance=RequestContext(request))

@login_required(login_url='/')
def collection(request, id_):
    conn = connections["default"] 
    result = {
        "collection": conn.get_collection("tb_app_collection").find_one(
            {"_id":ObjectId(id_)},
            {"name":1, "description": 1}
        )}
    return render_to_response('collection.html', result, context_instance=RequestContext(request))

@login_required(login_url='/')
def batch(request, id_):
    return render_to_response('batch.html', {}, context_instance=RequestContext(request))

@login_required(login_url='/')
def assignment(request, id_):
    return render_to_response('assignment.html', {}, context_instance=RequestContext(request))

### Ajax calls ###############################################################

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
            result = {"status": "success", "msg": "Sign in succeeded.  Welcome back, "+username}
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
    try:
        new_user = User.objects.create_user(
                request.POST["username"],
                request.POST["email"],
                request.POST["username"],   #Password
                )
        new_user.first_name = request.POST["first_name"]
        new_user.last_name = request.POST["last_name"]
        new_user.is_staff = "admin" in request.POST
        new_user.is_superuser = "admin" in request.POST
        new_user.save()
    except MultiValueDictKeyError as e:
#        print e.args
        return gen_json_response({"status": "failed", "msg": "Missing field."})

    return gen_json_response({"status": "success", "msg": "Successfully created account."})

@login_required(login_url='/')
def update_permission(request):
    if not request.user.is_superuser:
        return gen_json_response({"status": "failed", "msg": "You must be an administrator to change account privileges."})

    try:
        user = User.objects.get(username=request.POST["username"])
    except MultiValueDictKeyError as e:
        return gen_json_response({"status": "failed", "msg": "Missing field 'username.'"})

    if "active" in request.POST:
        new_status = request.POST["active"]=='true'
        if not new_status and user.is_superuser:
            return gen_json_response({"status": "failed", "msg": "Sorry, you can't deactivate a user with admin privileges."})
        else:
            user.is_active = new_status
            if user.is_active:
                user.set_password(user.username)
        
    if "admin" in request.POST:
        new_status = request.POST["admin"]=='true'
        if not new_status and User.objects.filter(is_superuser=True).count() < 2:
            return gen_json_response({"status": "failed", "msg": "Sorry, you can't remove admin privileges from the last administrator."})
        elif new_status and not user.is_active:
            return gen_json_response({"status": "failed", "msg": "Sorry, you can't grant admin privileges to an inactive user."})
        else:
            user.is_superuser =  new_status
    user.save()

    return gen_json_response({"status": "success", "msg": "Successfully updated permissions.", "new_status": new_status})


@login_required(login_url='/')
def upload_collection(request):
    #Get name and description
    try:
        name = request.POST["name"]
        csv_file = request.FILES["fileInput"]
        filename = unicode(csv_file)

        #! This isn't quite right.  Description shouldn't be required.
        #description = get_argument(request,"description", "")
        description = request.POST["description"]

        print name, description
    except MultiValueDictKeyError as e:
        print e.args
        return gen_json_response({"status": "failed", "msg": "Missing field."})

    #Detect filetype
    if re.search('\.csv$', filename.lower()):
        csv_text = csv_file.read()
        J = convert_csv_to_bson(csv_text)

    elif re.search('\.json$', filename.lower()):
        J = json.load(file(filename, 'r'))
        #! Validate json object here

    J['name'] = name
    J['description'] = description

    conn = connections["default"]
    result = conn.get_collection("tb_app_collection").insert(J)

#    return gen_json_response({"status": "success", "msg": "Everything all good AFAICT."})
    return redirect('/shared-resources/')

@login_required(login_url='/')
def get_collection_docs(request):
    id_ = request.POST["id"]
    conn = connections["default"]
    collection = conn.get_collection("tb_app_collection").find_one({"_id":ObjectId(id_)})

    #! Need error checking for invalid Ids

    return gen_json_response({
            "status": "success",
            "msg": "Everything all good AFAICT.",
            "documents" : collection["documents"]
            })

@login_required(login_url='/')
def create_codebook(request):
    #Get name and description
    try:
        name = request.POST["name"]

        #! This isn't quite right.  Description shouldn't be required.
        description = request.GET.get("description", "")
        #description = request.POST["description"]

        print name, description
    except MultiValueDictKeyError as e:
        print e.args
        return gen_json_response({"status": "failed", "msg": "Missing field."})

    if len(name) < 4:
        return gen_json_response({"status": "failed", "msg": "This name is too short.  Please give a name at least 4 letters long."})

    #Construct object
    J = {}
    J['name'] = name
    J['description'] = description
    J['created_at'] = datetime.datetime.utcnow()
    J['version'] = 1
    J['children'] = []
    J['batches'] = []
    J['parent'] = None
    J['questions'] = [{
            "question_type" : "Static text",
            "var_name" : "default_question",
            "params" : {
                "header_text" : "<h2> New codebook </h2><p><strong>Use the controls at right to add questions.</strong></p>",
            }
        },
        {
            "question_type" : "Multiple choice",
            "var_name" : "mchoice",
            "params" : {
                "header_text" : "Here is an example of a multiple choice question.  Which answer do you like best?",
                "answer_array" : ["This one","No, this one","A third option"],
            }
        },
        {
            "question_type" : "Short essay",
            "var_name" : "essay",
            "params" : {
                "header_text" : "Here's a short essay question.",
            }
        }]

    conn = connections["default"]
    result = conn.get_collection("tb_app_codebook").insert(J)

    return gen_json_response({"status": "success", "msg": "Everything all good AFAICT."})

@login_required(login_url='/')
def get_codebook(request):
    id_ = request.POST["id"]
    conn = connections["default"]
    codebook = conn.get_collection("tb_app_codebook").find_one({"_id":ObjectId(id_)})

    #! Need error checking for invalid Ids

    return gen_json_response({
            "status": "success",
            "msg": "Successfully retrieved codebook.",
            "codebook" : codebook
            })

@login_required(login_url='/')
def save_codebook(request):
    parent_id = request.POST["parent_id"]
    questions = json.loads(request.POST["questions"])["questions"]

    #Retrieve parent codebook
    conn = connections["default"]
    coll = conn.get_collection("tb_app_codebook")
    parent_codebook = coll.find_one({"_id":ObjectId(parent_id)})
    #!Handle parent_codebook == None

    #Create new codebook
    J = {}

    if parent_codebook["children"]:
        J['name'] = parent_codebook["name"]+" (branch)"
    else:
        J['name'] = parent_codebook["name"]

    J['description'] = parent_codebook["description"]
    J['created_at'] = datetime.datetime.utcnow()
    J['version'] = parent_codebook["version"]+1
    J['children'] = []
    J['batches'] = []
    J['parent'] = ObjectId(parent_id)
    J['questions'] = questions

    result_id = coll.insert(J)

    parent_codebook["children"].append(result_id)
    result = coll.update({"_id":ObjectId(parent_id)}, parent_codebook)
    print result
    print parent_codebook

    return gen_json_response({
            "status": "success",
            "msg": "Successfully saved codebook.",
            "_id": result_id,
            "codebook" : J,
            })

@login_required(login_url='/')
def start_batch(request):
    #Get name and description
    try:
        codebook_id = request.POST["codebook_id"]
        collection_id = request.POST["collection_id"]
        coders = request.POST["coders"]
        overlap = request.POST["overlap"]

        #! This isn't quite right.  Description shouldn't be required.
        description = request.GET.get("description", "")
        #description = request.POST["description"]

    except MultiValueDictKeyError as e:
#        print e.args
        return gen_json_response({"status": "failed", "msg": "Missing field."})

    if len(name) < 4:
        return gen_json_response({"status": "failed", "msg": "This name is too short.  Please give a name at least 4 letters long."})

    #Construct object
    J = {}
    J['name'] = name
    J['description'] = description
    J['created_at'] = datetime.datetime.utcnow()
    J['version'] = 1
    J['children'] = []
    J['batches'] = []
    J['parent'] = None
    J['questions'] = [{
            "question_type" : "Static text",
            "var_name" : "default_question",
            "params" : {
                "header_text" : "<h2> New codebook </h2><p><strong>Use the controls at right to add questions.</strong></p>",
            }
        },
        {
            "question_type" : "Multiple choice",
            "var_name" : "mchoice",
            "params" : {
                "header_text" : "Here is an example of a multiple choice question.  Which answer do you like best?",
                "answer_array" : ["This one","No, this one","A third option"],
            }
        },
        {
            "question_type" : "Short essay",
            "var_name" : "essay",
            "params" : {
                "header_text" : "Here's a short essay question.",
            }
        }]

    conn = connections["default"]
    result = conn.get_collection("tb_app_codebook").insert(J)

    return gen_json_response({"status": "success", "msg": "Everything all good AFAICT."})

