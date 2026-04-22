from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views import View
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Report


# HOME
def home(request):
    return render(request, 'main_app/home.html')


# LIST (boleh semua)
class ReportListView(ListView):
    model = Report
    template_name = 'main_app/report_list.html'
    context_object_name = 'reports'


# DETAIL (boleh semua)
class ReportDetailView(DetailView):
    model = Report
    template_name = 'main_app/report_detail.html'


# CREATE (HANYA ADMIN)
class ReportCreateView(CreateView):
    model = Report
    fields = ['title', 'category', 'description', 'location']
    template_name = 'main_app/add_report.html'
    success_url = reverse_lazy('report_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin:
            messages.error(request, "Akses ditolak ❌ (Hanya admin)")
            return redirect('report_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "Laporan berhasil ditambahkan ✅")
        return super().form_valid(form)


# UPDATE (HANYA ADMIN)
class ReportUpdateView(UpdateView):
    model = Report
    fields = ['title', 'category', 'description', 'location']
    template_name = 'main_app/add_report.html'
    success_url = reverse_lazy('report_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin:
            messages.error(request, "Akses ditolak ❌ (Hanya admin)")
            return redirect('report_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "Laporan berhasil diupdate ✏️")
        return super().form_valid(form)


# DELETE (HANYA ADMIN)
class ReportDeleteView(DeleteView):
    model = Report
    template_name = 'main_app/confirm_delete.html'
    success_url = reverse_lazy('report_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin:
            messages.error(request, "Akses ditolak ❌ (Hanya admin)")
            return redirect('report_list')
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        messages.success(self.request, "Laporan berhasil dihapus 🗑️")
        return super().post(request, *args, **kwargs)


# WORKFLOW STATUS (HANYA ADMIN)
class ReportUpdateStatusView(View):
    def post(self, request, pk):

        if not request.user.is_authenticated or not request.user.is_admin:
            messages.error(request, "Akses ditolak ❌ (Hanya admin)")
            return redirect('report_list')

        report = get_object_or_404(Report, pk=pk)
        new_status = request.POST.get('status')

        report.status = new_status
        report.save()

        messages.success(request, f"Status berhasil diubah menjadi {new_status} 🚀")

        return redirect('report_list')