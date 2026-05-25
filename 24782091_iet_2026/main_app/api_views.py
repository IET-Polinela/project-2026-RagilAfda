from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Report
from .permissions import CanAccessDraftReport
from .serializers import ReportSerializer


class ReportViewSet(viewsets.ModelViewSet):
    serializer_class = ReportSerializer

    def get_queryset(self):
        queryset = Report.objects.all().order_by('-created_at')
        user = self.request.user

        if not user.is_authenticated:
            return Report.objects.none()

        if getattr(user, 'is_admin', False):
            if self.action in ['update', 'partial_update']:
                return queryset
            return queryset.exclude(status='DRAFT')

        return queryset.filter(Q(reporter=user) | ~Q(status='DRAFT'))

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
