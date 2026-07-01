from rest_framework.routers import DefaultRouter

from .api_views import ReportViewSet

router = DefaultRouter()
router.register('report', ReportViewSet, basename='report')
router.register('reports', ReportViewSet, basename='reports')

urlpatterns = router.urls
