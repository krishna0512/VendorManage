from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.KitListAPIView.as_view()),
    path('<int:pk>/', views.KitDetailAPIView.as_view()),
]