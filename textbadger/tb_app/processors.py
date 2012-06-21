from django.contrib.auth.models import User

def admin_names(request):
    admin_users = User.objects.filter(is_superuser=True)
    names = [u.first_name + ' ' + u.last_name for u in admin_users]

    if len(names) == 0:
        admin_names = "This instance of TextBadger has no administrators yet."
    elif len(names) == 1:
        admin_names = "This instance of TextBadger is administered by "+names[0]+"."
    elif len(names) > 1:
        admin_names = "This instance of TextBadger is administered by "+", ".join(names[:-1])+" and "+names[-1]+"."

    return {'admin_names': admin_names}

