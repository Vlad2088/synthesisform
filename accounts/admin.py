from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'created_at']
    search_fields = ['name', 'user__username']
    ordering = ['name']


# Снимаем стандартную регистрацию User и вешаем свою
admin.site.unregister(User)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'get_role', 'is_active', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active']
    list_editable = []  # роль меняется через детальный вид, не инлайн
    ordering = ['-date_joined']

    @admin.display(description='Роль')
    def get_role(self, obj):
        if obj.is_superuser:
            return 'Администратор'
        if obj.is_staff:
            return 'Оператор'
        return 'Клиент'
