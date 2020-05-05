from django.urls import path

from expert.views import worker as views

urlpatterns = [
    path('', views.WorkerListView.as_view(), name='worker-list'),
    path('create/', views.WorkerCreateView.as_view(), name='worker-create'),
    path('<int:pk>/view/', views.WorkerDetailView.as_view(), name='worker-detail'),
    path('<int:pk>/update/', views.WorkerUpdateView.as_view(), name='worker-update'),
    path('<int:pk>/delete/', views.WorkerDeleteView.as_view(), name='worker-delete'),
]