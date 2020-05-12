from django.urls import path

from . import views

app_name = 'salary'
urlpatterns = [
    path('', views.SalaryListView.as_view(), name='list'),
    path('create/', views.SalaryCreateView.as_view(), name='create'),
]