
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
if not User.objects.filter(username='test').exists():
    User.objects.create_user('test', 'test@test.com', 'testpass')
    print("User 'test' created.")
else:
    print("User 'test' already exists.")
