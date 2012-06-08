from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

class Command(BaseCommand):
    args = '<username username ...>'
    help = 'Shows record info for specified usernames'

    def handle(self, *args, **options):
        for username in args:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise CommandError('User "%s" does not exist' % username)

            self.stdout.write('Info for user "%s"\n' % username)
            D = user.__dict__
            for f in D:
                self.stdout.write('\t%s : %s\n' % (f, D[f]) )


#            poll.opened = False
#            poll.save()


