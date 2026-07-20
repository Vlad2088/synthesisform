import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
import django
django.setup()
from django.contrib.auth import authenticate

# Проверка пароля
u = authenticate(username='vlad2088', password='3s65vzR2wmYJu')
if u:
    print(f'OK: {u.username}, is_staff={u.is_staff}')
else:
    print('FAIL: неверный логин или пароль')
    # Покажем хеш пароля для диагностики
    from django.contrib.auth.models import User
    user = User.objects.get(username='vlad2088')
    print(f'Хеш пароля: {user.password[:50]}...')
    print(f'is_active={user.is_active}')
