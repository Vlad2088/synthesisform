from django.contrib import admin
from .models import Material, Printer, Order, PrintJob

admin.site.site_header = "Администрирование Synthesisform"
admin.site.site_title = "Synthesisform"
admin.site.index_title = "Управление производством"

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'manufacturer', 'color', 'diameter', 'stock_grams')
    search_fields = ('name', 'manufacturer')
    

@admin.register(Printer)
class PrinterAdmin(admin.ModelAdmin):
    list_display = ('name', 'model', 'status', 'loaded_material')
    list_filter = ('status',)
    search_fields = ('name',)
    
    
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('customer__name', 'description')
    
    
@admin.register(PrintJob)
class PrintJobAdmin(admin.ModelAdmin):
    list_display = ('printer', 'material', 'status', 'created_at')
    list_filter = ('status',)

  