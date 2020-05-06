from django.urls import path

from expert.views import customer as views

urlpatterns = [
    path('', views.CustomerListView.as_view(), name='customer-list'),
    path('create/', views.CustomerCreateView.as_view(), name='customer-create'),
    path('<int:pk>/view/', views.CustomerDetailView.as_view(), name='customer-detail'),
    path('<int:pk>/update/', views.CustomerUpdateView.as_view(), name='customer-update'),
]