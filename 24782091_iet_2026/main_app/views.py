from django.shortcuts import render, redirect
from .models import Report
from .forms import ReportForm

# Create your views here.
def home(request):
    reports = Report.objects.all()
    return render(request, 'main_app/home.html', {'reports': reports})

def report_list(request):
    # Mengambil semua data dari model Report
    reports = Report.objects.all() 
    return render(request, 'main_app/report_list.html', {'reports': reports})

def add_report(request):
    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ReportForm()
    return render(request, 'main_app/add_report.html', {'form': form})

from django.shortcuts import get_object_or_404

def update_report(request, pk):
    report = get_object_or_404(Report, pk=pk)
    if request.method == "POST":
        form = ReportForm(request.POST, instance=report)
        if form.is_valid():
            form.save()
            return redirect('report_list')
    else:
        form = ReportForm(instance=report)
    return render(request, 'main_app/add_report.html', {'form': form})

def delete_report(request, pk):
    report = get_object_or_404(Report, pk=pk)
    report.delete()
    return redirect('report_list')