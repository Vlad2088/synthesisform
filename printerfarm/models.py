from django.db import models
from accounts.models import Customer


class Material(models.Model):
    """Материал для печати (PLA, ABS, PETG и т.д.)"""
    name = models.CharField('Название', max_length=100)
    manufacturer = models.CharField('Производитель', max_length=100, blank=True)
    color = models.CharField('Цвет', max_length=50, blank=True)
    diameter = models.FloatField('Диаметр (мм)', default=1.75)
    cost_per_gram = models.DecimalField('Себестоимость за грамм', max_digits=8, decimal_places=4, default=0)
    stock_grams = models.FloatField('Остаток (грамм)', default=0)
    created_at = models.DateTimeField('Создан', auto_now_add=True)

    class Meta:
        verbose_name = 'Материал'
        verbose_name_plural = 'Материалы'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.color})' if self.color else self.name


class Printer(models.Model):
    """3D-принтер"""
    STATUS_CHOICES = [
        ('idle', 'Свободен'),
        ('printing', 'Печатает'),
        ('paused', 'Пауза'),
        ('error', 'Ошибка'),
        ('maintenance', 'Обслуживание'),
    ]

    name = models.CharField('Название', max_length=100)
    model = models.CharField('Модель', max_length=100, blank=True)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='idle')
    loaded_material = models.ForeignKey(
        Material, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='Заправленный материал', related_name='printers'
    )
    created_at = models.DateTimeField('Создан', auto_now_add=True)

    class Meta:
        verbose_name = 'Принтер'
        verbose_name_plural = 'Принтеры'
        ordering = ['name']

    def __str__(self):
        return self.name


class OrderFile(models.Model):
    """Файл заказа (чертёж, STL и т.д.)"""
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='files', verbose_name='Заказ')
    file = models.FileField('Файл', upload_to='order_files/%Y/%m/')
    uploaded_at = models.DateTimeField('Загружен', auto_now_add=True)

    class Meta:
        verbose_name = 'Файл заказа'
        verbose_name_plural = 'Файлы заказов'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'{self.order} — {self.file.name.split("/")[-1]}'


class Order(models.Model):
    """Заказ клиента."""
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE,
        related_name='orders', verbose_name='Заказчик'
    )
    description = models.TextField(verbose_name='Описание заказа')
    price = models.DecimalField('Стоимость', max_digits=10, decimal_places=2, null=True, blank=True)
    estimated_time_min = models.PositiveIntegerField('Время изготовления (мин)', null=True, blank=True)
    printer = models.ForeignKey(
        Printer, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='Назначенный принтер', related_name='orders'
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('new', 'Новый'),
            ('in_progress', 'В работе'),
            ('done', 'Готов'),
        ],
        default='new',
        verbose_name='Статус'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлён')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Заказ #{self.pk} — {self.customer.name}'


class PrintJob(models.Model):
    """Задание на печать"""
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('printing', 'Печатается'),
        ('completed', 'Завершено'),
        ('failed', 'Ошибка'),
        ('cancelled', 'Отменено'),
    ]

    name = models.CharField('Название задания', max_length=200)
    printer = models.ForeignKey(
        Printer, on_delete=models.CASCADE, verbose_name='Принтер', related_name='jobs'
    )
    material = models.ForeignKey(
        Material, on_delete=models.SET_NULL, null=True, verbose_name='Материал', related_name='jobs'
    )
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='pending')
    estimated_time_min = models.PositiveIntegerField('Оценка времени (мин)', default=0)
    actual_time_min = models.PositiveIntegerField('Факт. время (мин)', null=True, blank=True)
    material_used_grams = models.FloatField('Израсходовано (грамм)', null=True, blank=True)
    notes = models.TextField('Заметки', blank=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    started_at = models.DateTimeField('Начато', null=True, blank=True)
    finished_at = models.DateTimeField('Завершено', null=True, blank=True)

    class Meta:
        verbose_name = 'Задание'
        verbose_name_plural = 'Задания'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} [{self.get_status_display()}]'
