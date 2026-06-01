from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django.http import JsonResponse

from .models import Report


def get_visible_reports(user):
    queryset = Report.objects.all().order_by('-created_at')

    if not user.is_authenticated:
        return Report.objects.none()

    if user.is_admin:
        return queryset.exclude(status='DRAFT')

    return queryset.filter(Q(reporter=user) | ~Q(status='DRAFT'))


def search_report(request):
    query = request.GET.get('q', '')
    reports = get_visible_reports(request.user).filter(title__icontains=query).values()

    return JsonResponse(list(reports), safe=False)


def report_detail_api(request, pk):
    report = get_object_or_404(get_visible_reports(request.user), pk=pk)

    return JsonResponse({
        'title': report.title,
        'category': report.category,
        'description': report.description,
        'location': report.location,
        'status': report.status
    })

def home(request):
    return render(request, 'main_app/home.html')


class ReportListView(ListView):
    model = Report
    template_name = 'main_app/report_list.html'
    context_object_name = 'reports'

    def get_queryset(self):
        return get_visible_reports(self.request.user)


class ReportDetailView(DetailView):
    model = Report
    template_name = 'main_app/report_detail.html'

    def get_queryset(self):
        return get_visible_reports(self.request.user)


class ReportCreateView(CreateView):
    model = Report
    fields = ['title', 'category', 'description', 'location']
    template_name = 'main_app/add_report.html'
    success_url = reverse_lazy('report_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.is_admin:
            messages.error(request, "Akses ditolak. Hanya citizen yang dapat membuat laporan.")
            return redirect('report_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.reporter = self.request.user
        if not form.instance.status:
            form.instance.status = 'REPORTED'
        messages.success(self.request, "Laporan berhasil ditambahkan.")
        return super().form_valid(form)


class ReportUpdateView(UpdateView):
    model = Report
    fields = ['title', 'category', 'description', 'location']
    template_name = 'main_app/add_report.html'
    success_url = reverse_lazy('report_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Silakan login terlebih dahulu.")
            return redirect('report_list')

        report = get_object_or_404(Report, pk=kwargs['pk'])
        if request.user.is_admin:
            messages.error(request, "Admin hanya dapat mengubah status laporan.")
            return redirect('report_list')

        if report.reporter_id != request.user.id:
            messages.error(request, "Anda hanya dapat mengedit laporan milik sendiri.")
            return redirect('report_list')

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "Laporan berhasil diupdate.")
        return super().form_valid(form)


class ReportDeleteView(DeleteView):
    model = Report
    template_name = 'main_app/confirm_delete.html'
    success_url = reverse_lazy('report_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Silakan login terlebih dahulu.")
            return redirect('report_list')

        report = get_object_or_404(Report, pk=kwargs['pk'])
        if request.user.is_admin:
            messages.error(request, "Admin tidak dapat menghapus laporan.")
            return redirect('report_list')

        if report.reporter_id != request.user.id:
            messages.error(request, "Anda hanya dapat menghapus laporan milik sendiri.")
            return redirect('report_list')

        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        messages.success(self.request, "Laporan berhasil dihapus.")
        return super().post(request, *args, **kwargs)


class ReportUpdateStatusView(View):
    def post(self, request, pk):
        if not request.user.is_authenticated or not request.user.is_admin:
            messages.error(request, "Akses ditolak. Hanya admin.")
            return redirect('report_list')

        report = get_object_or_404(Report, pk=pk)
        new_status = request.POST.get('status')

        report.status = new_status
        report.save()

        messages.success(request, f"Status berhasil diubah menjadi {new_status}.")
        return redirect('report_list')
