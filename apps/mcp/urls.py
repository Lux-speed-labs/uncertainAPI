from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.MCPHealthView.as_view(), name='mcp_health'),
    path('capabilities/', views.MCPCapabilitiesView.as_view(), name='mcp_capabilities'),
]