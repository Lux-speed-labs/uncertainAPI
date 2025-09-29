from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.HealthCheckView.as_view(), name='health_check'),
    path('', views.APIRootView.as_view(), name='api_root'),
]