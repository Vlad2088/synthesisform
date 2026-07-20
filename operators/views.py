from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from printerfarm.models import Material, Printer, Order, PrintJob
from accounts.models import Customer


def staff_required(view_func):
    """Декоратор: только для is_staff пользователей."""
    decorated = user_passes_test(lambda u: u.is_staff, login_url='/accounts/login/')(view_func)
    return login_required(decorated)


@staff_required
def dashboard(request):
    """Дашборд оператора: сводка заказов, принтеров, материалов."""
    new_count = Order.objects.filter(status='new').count()
    in_progress_count = Order.objects.filter(status='in_progress').count()
    done_count = Order.objects.filter(status='done').count()

    idle_count = Printer.objects.filter(status='idle').count()
    printing_count = Printer.objects.filter(status='printing').count()
    error_count = Printer.objects.filter(status='error').count()

    low_materials = Material.objects.filter(stock_grams__lt=200)

    context = {
        'new_count': new_count,
        'in_progress_count': in_progress_count,
        'done_count': done_count,
        'idle_count': idle_count,
        'printing_count': printing_count,
        'error_count': error_count,
        'low_materials': low_materials,
    }
    return render(request, 'operators/dashboard.html', context)


@staff_required
def order_list(request):
    """Очередь заказов с фильтром по статусу."""
    status_filter = request.GET.get('status', '')
    orders = Order.objects.select_related('customer').all()
    if status_filter:
        orders = orders.filter(status=status_filter)
    orders = orders.order_by('-created_at')
    context = {
        'orders': orders,
        'current_status': status_filter,
    }
    return render(request, 'operators/order_list.html', context)


@staff_required
def order_detail(request, order_id):
    """Карточка заказа: редактирование и создание задания печати."""
    order = get_object_or_404(Order.objects.select_related('customer__user', 'printer').prefetch_related('files'), id=order_id)
    printers = Printer.objects.all()
    materials = Material.objects.all()

    if request.method == 'POST':
        action = request.POST.get('action', '')

        if action == 'update_order':
            new_status = request.POST.get('status', order.status)
            # Приводим 'ready' к 'done' для совместимости с клиентским кабинетом
            if new_status == 'ready':
                new_status = 'done'
            order.status = new_status
            price = request.POST.get('price', '').strip()
            if price:
                order.price = price
            print_time = request.POST.get('print_time', '').strip()
            if print_time:
                try:
                    order.estimated_time_min = int(print_time)
                except ValueError:
                    messages.error(request, 'Время должно быть числом (минуты).')
                    return redirect('operators:operator_order_detail', order_id=order.id)
            if 'printer_id' in request.POST:
                printer_id = request.POST['printer_id'].strip()
                order.printer = Printer.objects.get(id=printer_id) if printer_id else None
            order.save()
            messages.success(request, 'Заказ обновлён.')
            return redirect('operators:operator_order_detail', order_id=order.id)

        elif action == 'create_print_job':
            material_id = request.POST.get('material', '')
            grams_str = request.POST.get('material_used_grams', '').strip()
            if material_id and grams_str:
                material = get_object_or_404(Material, id=material_id)
                grams = float(grams_str)
                if grams > 0 and grams <= material.stock_grams:
                    material.stock_grams -= grams
                    material.save()
                    PrintJob.objects.create(
                        name=f'Заказ #{order.id} — {order.customer.name}',
                        printer=order.printer,
                        material=material,
                        estimated_time_min=order.estimated_time_min or 0,
                        material_used_grams=grams,
                    )
                    if order.status == 'new':
                        order.status = 'in_progress'
                        order.save()
                    messages.success(request, f'Задание печати создано. Списано {grams}г материала.')
                else:
                    messages.error(request, f'Недостаточно материала. Доступно: {material.stock_grams}г')
            else:
                messages.error(request, 'Выберите материал и укажите количество граммов.')
            return redirect('operators:operator_order_detail', order_id=order.id)

    context = {
        'order': order,
        'printers': printers,
        'materials': materials,
        'files': order.files.all(),
    }
    return render(request, 'operators/order_detail.html', context)


@staff_required
def printer_list(request):
    """Список принтеров с состоянием и добавление нового."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        model_name = request.POST.get('model', '').strip()
        if name:
            Printer.objects.create(name=name, model=model_name, status='idle')
            messages.success(request, f'Принтер «{name}» добавлен.')
        else:
            messages.error(request, 'Укажите название принтера.')
        return redirect('operators:operator_printers')

    status_filter = request.GET.get('status', '')
    printers = Printer.objects.select_related('loaded_material').all()
    if status_filter:
        printers = printers.filter(status=status_filter)
    printers = printers.order_by('name')
    context = {
        'printers': printers,
        'current_status': status_filter,
    }
    return render(request, 'operators/printer_list.html', context)


@staff_required
def printer_update(request, printer_id):
    """Смена статуса принтера, заправка материала."""
    printer = get_object_or_404(Printer, id=printer_id)
    materials = Material.objects.all()

    if request.method == 'POST':
        printer.status = request.POST.get('status', printer.status)
        material_id = request.POST.get('loaded_material', '')
        printer.loaded_material = Material.objects.get(id=material_id) if material_id else None
        printer.save()
        messages.success(request, f'Принтер «{printer.name}» обновлён.')
        return redirect('operators:operator_printers')

    context = {
        'printer': printer,
        'materials': materials,
    }
    return render(request, 'operators/printer_update.html', context)


@staff_required
def material_list(request):
    """Склад материалов с добавлением нового."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        manufacturer = request.POST.get('manufacturer', '').strip()
        color = request.POST.get('color', '').strip()
        stock_str = request.POST.get('stock_grams', '0').strip()
        cost_str = request.POST.get('cost_per_gram', '0').strip()

        if not name:
            messages.error(request, 'Укажите название материала.')
            return redirect('operators:operator_materials')

        try:
            stock_grams = float(stock_str) if stock_str else 0
            cost_per_gram = float(cost_str) if cost_str else 0
        except ValueError:
            messages.error(request, 'Некорректные числовые значения.')
            return redirect('operators:operator_materials')

        Material.objects.create(
            name=name,
            manufacturer=manufacturer,
            color=color,
            stock_grams=stock_grams,
            cost_per_gram=cost_per_gram,
        )
        messages.success(request, f'Материал «{name}» добавлен.')
        return redirect('operators:operator_materials')

    materials = Material.objects.all().order_by('name')
    current_filter = None
    if request.GET.get('low_stock'):
        materials = materials.filter(stock_grams__lt=200)
        current_filter = 'low_stock'
    context = {'materials': materials, 'current_filter': current_filter}
    return render(request, 'operators/material_list.html', context)


@staff_required
def material_detail(request, material_id):
    """Карточка материала: пополнение остатка и изменение себестоимости."""
    material = get_object_or_404(Material, id=material_id)

    if request.method == 'POST':
        add_str = request.POST.get('add_grams', '').strip()
        cost_str = request.POST.get('cost_per_gram', '').strip()

        updated = False

        if add_str:
            try:
                add_grams = float(add_str)
                if add_grams <= 0:
                    raise ValueError
            except ValueError:
                messages.error(request, 'Укажите положительное количество граммов.')
                return redirect('operators:operator_material_detail', material_id=material.id)
            material.stock_grams += add_grams
            messages.success(request, f'Остаток «{material.name}» пополнен на {add_grams} г. Теперь: {material.stock_grams + add_grams} г.')
            updated = True

        if cost_str:
            try:
                cost_per_gram = float(cost_str)
                if cost_per_gram < 0:
                    raise ValueError
            except ValueError:
                messages.error(request, 'Укажите корректную себестоимость (₽/г).')
                return redirect('operators:operator_material_detail', material_id=material.id)
            material.cost_per_gram = cost_per_gram
            messages.success(request, f'Себестоимость «{material.name}» обновлена: {cost_per_gram} ₽/г.')
            updated = True

        if not updated:
            messages.error(request, 'Заполните хотя бы одно поле.')
            return redirect('operators:operator_material_detail', material_id=material.id)

        material.save()
        return redirect('operators:operator_material_detail', material_id=material.id)

    context = {'material': material}
    return render(request, 'operators/material_detail.html', context)


@staff_required
def customer_list(request):
    """Список заказчиков."""
    customers = Customer.objects.select_related('user').all().order_by('name')
    context = {'customers': customers}
    return render(request, 'operators/customer_list.html', context)


@staff_required
def order_history(request):
    """История выполненных заказов."""
    orders = Order.objects.filter(status='done').select_related('customer').order_by('-created_at')
    context = {'orders': orders}
    return render(request, 'operators/order_history.html', context)


def logout_view(request):
    """Выход пользователя."""
    logout(request)
    return redirect('accounts:login')
