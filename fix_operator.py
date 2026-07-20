import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
import django
django.setup()
from django.contrib.auth.models import User

# Назначаем пользователю is_staff
user = User.objects.get(username='vlad2088')
user.is_staff = True
user.save()
print(f'Пользователь {user.username}: is_staff=True (установлено)')
print(f'Проверка: is_staff={user.is_staff}, is_superuser={user.is_superuser}')
