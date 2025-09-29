from django.urls import path
from . import views

urlpatterns = [
    path('jobs/', views.JobListCreateView.as_view(), name='job_list_create'),
    path('jobs/<uuid:pk>/', views.JobDetailView.as_view(), name='job_detail'),
    path('jobs/<uuid:pk>/cancel/', views.JobCancelView.as_view(), name='job_cancel'),
]