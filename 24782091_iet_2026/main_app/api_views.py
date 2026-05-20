from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets

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
            return queryset

        return queryset.filter(Q(status='DRAFT', reporter=user) | ~Q(status='DRAFT'))

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, CanAccessDraftReport]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)
