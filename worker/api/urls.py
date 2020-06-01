from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.WorkerListAPIView.as_view(), name='api-list'),
    path('<int:pk>/', views.WorkerDetailAPIView.as_view(), name='api-detail'),
]