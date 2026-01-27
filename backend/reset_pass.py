
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
try:
    u = User.objects.get(username='test')
    u.set_password('testpass')
    u.save()
    print("Password for 'test' reset to 'testpass'.")
except User.DoesNotExist:
    User.objects.create_user('test', 'test@test.com', 'testpass')
    print("User 'test' created with password 'testpass'.")
