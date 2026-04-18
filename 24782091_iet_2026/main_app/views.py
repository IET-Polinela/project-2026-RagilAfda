from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views import View
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Report


# HOME
def home(request):
    return render(request, 'main_app/home.html')


#LIST
class ReportListView(ListView):
    model = Report
    template_name = 'main_app/report_list.html'
    context_object_name = 'reports'


#DETAIL
class ReportDetailView(DetailView):
    model = Report
    template_name = 'main_app/report_detail.html'


#CREATE
class ReportCreateView(CreateView):
    model = Report
    fields = ['title', 'category', 'description', 'location']
    template_name = 'main_app/add_report.html'
    success_url = reverse_lazy('report_list')

    def form_valid(self, form):
        messages.success(self.request, "Laporan berhasil ditambahkan ✅")
        return super().form_valid(form)


#UPDATE
class ReportUpdateView(UpdateView):
    model = Report
    fields = ['title', 'category', 'description', 'location']
    template_name = 'main_app/add_report.html'
    success_url = reverse_lazy('report_list')

    def form_valid(self, form):
        messages.success(self.request, "Laporan berhasil diupdate ✏️")
        return super().form_valid(form)


#DELETE
#class ReportDeleteView(DeleteView):
#    model = Report
#    template_name = 'main_app/confirm_delete.html'
#    success_url = reverse_lazy('report_list')

#   def delete(self, request, *args, **kwargs):
#        messages.success(self.request, "Laporan berhasil dihapus 🗑️")
#        return super().delete(request, *args, **kwargs)

class ReportDeleteView(DeleteView):
    model = Report
    template_name = 'main_app/confirm_delete.html'
    success_url = reverse_lazy('report_list')

    def post(self, request, *args, **kwargs):
        messages.success(self.request, "Laporan berhasil dihapus 🗑️")
        return super().post(request, *args, **kwargs)


#WORKFLOW STATUS
class ReportUpdateStatusView(View):
    def post(self, request, pk):
        report = get_object_or_404(Report, pk=pk)
        new_status = request.POST.get('status')

        report.status = new_status
        report.save()

        messages.success(request, f"Status berhasil diubah menjadi {new_status} 🚀")

        return redirect('report_list')