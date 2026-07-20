from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    """Заказчик, связанный с учётной записью."""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='customer',
        verbose_name='Пользователь'
    )
    
    name = models.CharField(max_length=200, verbose_name='Название / ФИО')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    notes = models.TextField(blank=True, verbose_name='Заметки')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')

    class Meta:
       verbose_name = 'Заказчик'
       verbose_name_plural = 'Заказчики'
       ordering = ['name']

    def __str__(self):
        return self.name
     
