from django.urls import path, include

from . import views

urlpatterns = [
    path('<int:pk>/', views.ProductDetailAPIView.as_view(), name='api-detail'),
    path('<int:pk>/assign/', views.ProductAssignAPIView.as_view(), name='api-assign'),
]