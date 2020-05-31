from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.KitListAPIView.as_view(), name='api-list'),
    path('<int:pk>/', views.KitDetailAPIView.as_view(), name='api-detail'),
]