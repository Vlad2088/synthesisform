from django.urls import path
from . import views

app_name = 'operators'

urlpatterns = [
    path('', views.dashboard, name='operator_dashboard'),
    path('orders/', views.order_list, name='operator_orders'),
    path('orders/<int:order_id>/', views.order_detail, name='operator_order_detail'),
    path('printers/', views.printer_list, name='operator_printers'),
    path('printers/<int:printer_id>/', views.printer_update, name='operator_printer_update'),
    path('materials/', views.material_list, name='operator_materials'),
    path('materials/<int:material_id>/', views.material_detail, name='operator_material_detail'),
    path('customers/', views.customer_list, name='operator_customers'),
    path('history/', views.order_history, name='operator_history'),
    path('logout/', views.logout_view, name='operator_logout'),
]
