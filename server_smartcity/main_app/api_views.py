from django.db.models import Count, Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Report
from .permissions import CanAccessDraftReport
from .serializers import ReportSerializer


class ReportPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ReportViewSet(viewsets.ModelViewSet):
    serializer_class = ReportSerializer
    pagination_class = ReportPagination

    def get_queryset(self):
        user = self.request.user
        tab = self.request.query_params.get('tab')
        queryset = Report.objects.all().order_by('-updated_at')

        if not user.is_authenticated:
            return Report.objects.none()

        if getattr(user, 'is_admin', False):
            if tab == 'my_reports':
                return queryset.filter(reporter=user).exclude(status='DRAFT')
            if tab == 'feed':
                return queryset.exclude(status='DRAFT')
            return queryset.exclude(status='DRAFT')

        if tab == 'my_reports':
            return queryset.filter(reporter=user)
        if tab == 'feed':
            return queryset.exclude(status='DRAFT')

        return queryset.filter(~Q(status='DRAFT') | Q(status='DRAFT', reporter=user))

    def get_permissions(self):
        return [IsAuthenticated(), CanAccessDraftReport()]

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)

    def _handle_admin_status_update(self, request, *args, **kwargs):
        if not getattr(request.user, 'is_admin', False):
            return None

        submitted_fields = set(request.data.keys())
        if 'status' not in submitted_fields:
            return Response(
                {'detail': 'Admin wajib mengirim field status.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not submitted_fields.issubset({'status'}):
            return Response(
                {'detail': 'Admin hanya dapat memperbarui status laporan.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data={'status': request.data.get('status')},
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        admin_response = self._handle_admin_status_update(request, *args, **kwargs)
        if admin_response is not None:
            return admin_response
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        admin_response = self._handle_admin_status_update(request, *args, **kwargs)
        if admin_response is not None:
            return admin_response
        return super().partial_update(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        summary_map = {
            'DRAFT': 0,
            'REPORTED': 0,
            'VERIFIED': 0,
            'IN_PROGRESS': 0,
            'RESOLVED': 0,
        }

        summary_rows = (
            self.get_queryset()
            .values('status')
            .annotate(total=Count('id'))
        )

        for row in summary_rows:
            status_key = row.get('status')
            if status_key in summary_map:
                summary_map[status_key] = row.get('total', 0)

        return Response(summary_map)
