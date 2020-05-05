from django.urls import path

from expert.views import kit as views

urlpatterns = [
    path('', views.KitListView.as_view(), name='kit-list'),
    path('create/', views.KitCreateView.as_view(), name='kit-create'),
    path('<slug:slug>/update/', views.KitUpdateView.as_view(), name='kit-update'),
    path('<slug:slug>/view/', views.KitDetailView.as_view(), name='kit-detail'),
    path('<slug:slug>/delete/', views.KitDeleteView.as_view(), name='kit-delete'),
    path('<int:pk>/uncomplete/', views.KitUncompleteRedirectView.as_view(), name='kit-uncomplete'),
]