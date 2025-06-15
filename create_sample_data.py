import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from main.models import Moderator

User = get_user_model()

# Create a regular user
user1, created = User.objects.get_or_create(username='user1', email='user1@example.com')
if created:
    user1.set_password('testpass123')
    user1.mobile = '09123456789'
    user1.save()
    print("Regular user 'user1' created.")
else:
    print("Regular user 'user1' already exists.")

# Create a moderator user
mod_user, created = User.objects.get_or_create(username='mod1', email='mod1@example.com')
if created:
    mod_user.set_password('modpass123')
    mod_user.mobile = '09987654321'
    mod_user.save()
    print("Moderator user 'mod1' created.")
    moderator, created = Moderator.objects.get_or_create(user=mod_user)
    if created:
        moderator.bio = 'Expert in event moderation'
        moderator.expertise_areas = ['Tech', 'Education']
        moderator.save()
        print("Moderator profile for 'mod1' created.")
    else:
         print("Moderator profile for 'mod1' already exists.")
else:
     print("Moderator user 'mod1' already exists.")


print("Sample users and moderator script finished.") 