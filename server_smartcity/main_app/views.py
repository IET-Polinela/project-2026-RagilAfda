import builtins

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .models import Report


builtins.PermissionDenied = PermissionDenied

ADMIN_STATUS_VALUES = {'REPORTED', 'VERIFIED', 'IN_PROGRESS', 'RESOLVED'}
ALLOWED_STATUS_TRANSITIONS = {
    'REPORTED': ('VERIFIED',),
    'VERIFIED': ('IN_PROGRESS',),
    'IN_PROGRESS': ('RESOLVED',),
    'RESOLVED': (),
}
STATUS_LABELS = {
    'REPORTED': 'Reported',
    'VERIFIED': 'Verified',
    'IN_PROGRESS': 'In Progress',
    'RESOLVED': 'Resolved',
}


def is_admin_user(user):
    return bool(
        user
        and user.is_authenticated
        and (
            getattr(user, 'is_admin', False)
            or getattr(user, 'is_staff', False)
            or getattr(user, 'is_superuser', False)
        )
    )


class AdminOnlyMixin:
    def dispatch(self, request, *args, **kwargs):
        if not is_admin_user(request.user):
            messages.error(request, "Akses ditolak. Hanya admin.")
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)


def attach_allowed_transitions(reports):
    for report in reports:
        report.allowed_status_transitions = get_allowed_status_transitions(report.status)
        report.admin_status_choices = get_admin_status_choices(report.status)
    return reports


def get_allowed_status_transitions(status):
    return [
        {'value': next_status, 'label': STATUS_LABELS[next_status]}
        for next_status in ALLOWED_STATUS_TRANSITIONS.get(status, set())
    ]


def get_admin_status_choices(status):
    choices = []
    if status in STATUS_LABELS:
        choices.append({
            'value': status,
            'label': STATUS_LABELS[status],
            'selected': True,
        })

    choices.extend(
        {
            'value': transition['value'],
            'label': transition['label'],
            'selected': False,
        }
        for transition in get_allowed_status_transitions(status)
        if transition['value'] != status
    )
    return choices


def get_visible_reports(user):
    queryset = Report.objects.all().order_by('-created_at')

    if not user.is_authenticated:
        return Report.objects.none()

    if user.is_admin:
        return queryset.exclude(status='DRAFT')

    return queryset.filter(Q(reporter=user) | ~Q(status='DRAFT'))


def search_report(request):
    if not is_admin_user(request.user):
        return HttpResponseForbidden()

    query = request.GET.get('q', '')
    reports = get_visible_reports(request.user).filter(title__icontains=query).values()

    return JsonResponse(list(reports), safe=False)


def report_detail_api(request, pk):
    user = getattr(request, 'user', None)
    queryset = get_visible_reports(user) if user else Report.objects.all()
    report = get_object_or_404(queryset, pk=pk)

    return JsonResponse({
        'title': report.title,
        'category': report.category,
        'description': report.description,
        'location': report.location,
        'status': report.status
    })

def home(request):
    return render(request, 'main_app/home.html')


class ReportListView(AdminOnlyMixin, ListView):
    model = Report
    template_name = 'main_app/report_list.html'
    context_object_name = 'reports'

    def get_queryset(self):
        return attach_allowed_transitions(list(get_visible_reports(self.request.user)))


class ReportDetailView(AdminOnlyMixin, DetailView):
    model = Report
    template_name = 'main_app/report_detail.html'

    def get_queryset(self):
        return get_visible_reports(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allowed_status_transitions'] = get_allowed_status_transitions(self.object.status)
        context['admin_status_choices'] = get_admin_status_choices(self.object.status)
        return context


class ReportCreateView(AdminOnlyMixin, CreateView):
    model = Report
    fields = ['title', 'category', 'description', 'location', 'status']
    template_name = 'main_app/add_report.html'
    success_url = reverse_lazy('report_list')

    def form_valid(self, form):
        if not form.instance.reporter_id:
            form.instance.reporter = self.request.user
        if not form.instance.status:
            form.instance.status = 'REPORTED'
        messages.success(self.request, "Laporan berhasil ditambahkan.")
        return super().form_valid(form)


class ReportUpdateView(AdminOnlyMixin, UpdateView):
    model = Report
    fields = ['title', 'category', 'description', 'location', 'status']
    template_name = 'main_app/add_report.html'
    success_url = reverse_lazy('report_list')

    def dispatch(self, request, *args, **kwargs):
        if is_admin_user(request.user):
            raise PermissionDenied("Admin hanya dapat mengubah status laporan.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "Laporan berhasil diupdate.")
        return super().form_valid(form)


class ReportDeleteView(AdminOnlyMixin, DeleteView):
    model = Report
    template_name = 'main_app/confirm_delete.html'
    success_url = reverse_lazy('report_list')

    def dispatch(self, request, *args, **kwargs):
        if is_admin_user(request.user):
            raise PermissionDenied("Admin tidak dapat menghapus laporan.")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        messages.success(self.request, "Laporan berhasil dihapus.")
        return super().post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        if is_admin_user(request.user):
            raise PermissionDenied("Admin tidak dapat menghapus laporan.")
        messages.success(self.request, "Laporan berhasil dihapus.")
        return super().delete(request, *args, **kwargs)


class ReportUpdateStatusView(View):
    def post(self, request, pk):
        if not is_admin_user(request.user):
            messages.error(request, "Akses ditolak. Hanya admin.")
            return redirect('report_list')

        report = get_object_or_404(get_visible_reports(request.user), pk=pk)
        new_status = request.POST.get('new_status') or request.POST.get('status')

        if new_status not in ADMIN_STATUS_VALUES:
            messages.error(request, "Status laporan tidak valid.")
            return redirect('report_list')

        if new_status == report.status:
            messages.info(request, "Status laporan tidak berubah.")
            return redirect('report_list')

        if new_status not in ALLOWED_STATUS_TRANSITIONS.get(report.status, set()):
            messages.error(request, "Transisi status laporan tidak valid.")
            return redirect('report_detail', pk=pk)

        report.status = new_status
        report.save(update_fields=['status', 'updated_at'])

        messages.success(request, f"Status berhasil diubah menjadi {new_status}.")
        return redirect('report_list')
