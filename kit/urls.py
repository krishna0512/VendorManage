from django.urls import path

from . import views

app_name = 'kit'
urlpatterns = [
    path('', views.KitListView.as_view(), name='list'),
    path('create/', views.KitCreateView.as_view(), name='create'),
    path('<slug:slug>/update/', views.KitUpdateView.as_view(), name='update'),
    path('<slug:slug>/view/', views.KitDetailView.as_view(), name='detail'),
    path('<slug:slug>/delete/', views.KitDeleteView.as_view(), name='delete'),
    path('<int:pk>/uncomplete/', views.KitUncompleteRedirectView.as_view(), name='uncomplete'),
    path('<int:pk>/change_completion_date/', views.KitChangeCompletionDate.as_view(), name='change-completion-date'),
]