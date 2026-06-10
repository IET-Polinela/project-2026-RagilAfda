from django.http import JsonResponse
from django.db.models import Count
from django.views import View
from django.views.generic import TemplateView

from main_app.models import Report


class DashboardView(TemplateView):
    template_name = 'dashboard/dashboard.html'


class DashboardDataView(View):
    def get(self, request, *args, **kwargs):
        total_reports = Report.objects.count()
        status_data = Report.objects.values('status').annotate(total=Count('id'))
        category_data = Report.objects.values('category').annotate(total=Count('id'))
        latest_reported = list(
            Report.objects.filter(status='REPORTED').order_by('-id').values()[:5]
        )
        latest_resolved = list(
            Report.objects.filter(status='RESOLVED').order_by('-id').values()[:5]
        )

        return JsonResponse({
            'total_reports': total_reports,
            'status_data': list(status_data),
            'category_data': list(category_data),
            'latest_reported': latest_reported,
            'latest_resolved': latest_resolved,
        })
