from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.utils.datastructures import MultiValueDictKeyError 
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
import json

from django.contrib.auth.models import User
from tb_app.models import Codebook, Collection, PrivateBatch

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
    result = {
        'codebooks' : jsonifyRecords(Codebook.objects.all(), ['username', 'first_name', 'last_name', 'email']),
        'collections' : jsonifyRecords(Collection.objects.all(), ['username', 'first_name', 'last_name', 'email']),
        'batches' : jsonifyRecords(PrivateBatch.objects.all(), ['username', 'first_name', 'last_name', 'email']),
        'users' : jsonifyRecords(User.objects.all(), ['username', 'first_name', 'last_name', 'email', 'is_active', 'is_superuser']),
    }

    return render_to_response('shared-resources.html', result, context_instance=RequestContext(request))

@login_required()#login_url='/')
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
    if 1:
        new_user = User.objects.create_user(
                request.POST["username"],
                request.POST["email"],
                request.POST["username"],   #Password
                )
        new_user.first_name = request.POST["first_name"]
        new_user.last_name = request.POST["last_name"]
        new_user.is_staff = "admin" in request.POST
        new_user.is_superuser = "admin" in request.POST

    try:
        pass
    except MultiValueDictKeyError as e:
        print e.args
        return gen_json_response({"status": "failed", "msg": "Missing field."})

    return gen_json_response({"status": "success", "msg": "Everything all good AFAICT."})



