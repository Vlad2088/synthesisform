from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from accounts.models import Customer
from .models import Printer, PrintJob, Material


@login_required
def index(request):
    """Главная: заказчиков — в кабинет, сотрудников — на обзор."""
    if Customer.objects.filter(user=request.user).exists():
        return redirect('profile')

    printers = Printer.objects.all()
    active_jobs = PrintJob.objects.filter(status__in=['printing', 'pending']).count()
    completed_jobs = PrintJob.objects.filter(status='completed').count()
    materials = Material.objects.all()

    context = {
        'printers': printers,
        'printers_count': printers.count(),
        'active_jobs': active_jobs,
        'completed_jobs': completed_jobs,
        'materials': materials,
        'materials_count': materials.count(),
    }
    return render(request, 'printerfarm/index.html', context)
