from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.utils.datastructures import MultiValueDictKeyError 
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
import json, re

from django.contrib.auth.models import User
from django.conf import settings
from django.db import connections
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

def gen_json_response( result ):
    return HttpResponse(json.dumps(result, indent=2), mimetype='application/json')

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

    print list(conn.get_collection("tb_app_collection").find(fields={"name":1, "description":1}))
    result = {
        'codebooks' : jsonifyRecords(Codebook.objects.all(), ['username', 'first_name', 'last_name', 'email']),
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
    result = {
        'codebook' : {}#!jsonifyRecord(Codebook.objects.get(pk=id_), ['username', 'first_name', 'last_name', 'email']),
    }

    return render_to_response('codebook.html', result, context_instance=RequestContext(request))

@login_required(login_url='/')
def collection(request, id_):
    #4fd2b3572fa6cd14b100002d
    result = {
        'collection' : {}#!jsonifyRecord(Codebook.objects.get(pk=id_), ['username', 'first_name', 'last_name', 'email']),
    }

    return render_to_response('collection.html', result, context_instance=RequestContext(request))

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

    print request.POST
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
    except MultiValueDictKeyError as e:
        print e.args
        return gen_json_response({"status": "failed", "msg": "Missing field."})

    return gen_json_response({"status": "success", "msg": "Everything all good AFAICT."})

@login_required(login_url='/')
def upload_collection(request):
#    print request.POST
#    print request._files
#    print request._raw_post_data
#    print '\n'.join(request.__dict__.keys())

    #Get name and description
    try:
        name = request.POST["name"]

        #! This isn't quite right.  Description shouldn't be required.
        #description = get_argument(request,"description", "")
        description = request.POST["description"]

        print name, description
    except MultiValueDictKeyError as e:
        print e.args
        return gen_json_response({"status": "failed", "msg": "Missing field."})

    #! Get the filename from the request object.
    #! Need to mess with jquery to get this to work.
    filename = settings.PROJECT_PATH+'/../dev/scrap/dummy-collections/collection-2959.csv'

    #Detect filetype
    if re.search('\.csv$', filename.lower()):
        csv_text = file(filename, 'r').read()
        J = convert_csv_to_bson(csv_text)

    elif re.search('\.json$', filename.lower()):
        J = json.load(file(filename, 'r'))
        #! Validate json object here

    J['name'] = name
    J['description'] = description

    conn = connections["default"]
    result = conn.get_collection("tb_app_collection").insert(J)

    return gen_json_response({"status": "success", "msg": "Everything all good AFAICT."})


