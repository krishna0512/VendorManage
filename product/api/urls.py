from django.urls import path, include

from . import views

urlpatterns = [
    path('<int:pk>/', views.ProductDetailAPIView.as_view(), name='api-detail'),
]