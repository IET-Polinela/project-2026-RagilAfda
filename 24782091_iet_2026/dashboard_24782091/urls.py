from django.urls import path
from .views import DashboardDataView, DashboardView

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('data/', DashboardDataView.as_view(), name='dashboard_data'),
]
