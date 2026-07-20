from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', views.RoleBasedLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('orders/', views.orders, name='orders'),
    path('orders/<int:order_id>/edit/', views.order_edit, name='order_edit'),
    path('cabinet/', views.profile, name='cabinet'),  # обратная совместимость
]
