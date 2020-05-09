from django.urls import path

from expert.views import worker as views
# from . import views

app_name = 'worker'
urlpatterns = [
    path('', views.WorkerListView.as_view(), name='list'),
    path('create/', views.WorkerCreateView.as_view(), name='create'),
    path('<int:pk>/view/', views.WorkerDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', views.WorkerUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.WorkerDeleteView.as_view(), name='delete'),
]