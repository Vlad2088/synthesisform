import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
import django
django.setup()
from django.contrib.auth.models import User

user = User.objects.get(username='vlad2088')
user.set_password('123456qwerty@')
user.is_staff = True
user.save()
print(f'Пароль для {user.username} установлен. is_staff={user.is_staff}')
