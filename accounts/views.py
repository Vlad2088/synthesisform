from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import CustomerProfileForm, CustomerRegistrationForm, OrderEditForm
from .models import Customer
from printerfarm.models import Order, OrderFile


def get_redirect_url(user):
    """Возвращает URL для редиректа после входа в зависимости от роли."""
    if user.is_staff:
        return '/operator/'
    return '/accounts/orders/'


class RoleBasedLoginView(LoginView):
    """LoginView, который направляет операторов в /operator/, клиентов в /accounts/orders/."""
    template_name = 'accounts/login.html'

    def get_success_url(self):
        return get_redirect_url(self.request.user)


class RegisterView(CreateView):
    form_class = CustomerRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect(get_redirect_url(user))


@login_required
def profile(request):
    """Личные данные клиента."""
    customer = Customer.objects.get(user=request.user)
    return render(request, 'accounts/profile.html', {'customer': customer})


@login_required
def profile_edit(request):
    """Редактирование личных данных."""
    customer = Customer.objects.get(user=request.user)
    if request.method == 'POST':
        form = CustomerProfileForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлён.')
            return redirect('profile')
    else:
        form = CustomerProfileForm(instance=customer)
    return render(request, 'accounts/profile_edit.html', {'form': form})


@login_required
def orders(request):
    """Заказы клиента: создание и список."""
    customer = Customer.objects.get(user=request.user)
    if request.method == 'POST':
        description = request.POST.get('description', '').strip()
        if description:
            order = Order.objects.create(customer=customer, description=description)
            files = request.FILES.getlist('files')
            for f in files:
                OrderFile.objects.create(order=order, file=f)
            messages.success(request, 'Заказ успешно создан!')
        else:
            messages.error(request, 'Введите описание заказа.')
        return redirect('orders')
    orders_list = Order.objects.filter(customer=customer).order_by('-created_at')
    return render(request, 'accounts/orders.html', {
        'customer': customer,
        'orders': orders_list,
    })


@login_required
def order_edit(request, order_id):
    """Редактирование заказа."""
    customer = Customer.objects.get(user=request.user)
    order = get_object_or_404(Order, id=order_id, customer=customer)
    if request.method == 'POST':
        form = OrderEditForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            uploaded_files = request.FILES.getlist('files')
            for f in uploaded_files:
                OrderFile.objects.create(order=order, file=f)
            messages.success(request, 'Заказ обновлён.')
            return redirect('orders')
    else:
        form = OrderEditForm(instance=order)
    return render(request, 'accounts/order_edit.html', {
        'form': form,
        'order': order,
    })


def logout_view(request):
    """Выход пользователя."""
    logout(request)
    return redirect('login')
