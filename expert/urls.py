from django.contrib.auth import views as auth_views
from django.urls import path, include

from expert import views

app_name = 'expert'
urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name='index'),
    path('kit/', views.KitListView.as_view(), name='kit-list'),
    path('kit/create/', views.KitCreateView.as_view(), name='kit-create'),
    path('kit/<int:pk>/update/', views.KitUpdateView.as_view(), name='kit-update'),
    path('kit/<slug:slug>/view/', views.KitDetailView.as_view(), name='kit-detail'),
    path('kit/<slug:slug>/delete/', views.KitDeleteView.as_view(), name='kit-delete'),

    path('product/<int:pk>/update/', views.ProductUpdateView.as_view(), name='product-update'),
    path('product/create/', views.ProductCreateView.as_view(), name='product-create'),
    path('product/<int:pk>/complete/', views.product_complete, name='product-complete'),

    path('report/<int:year>/<str:month>/<int:day>/', views.ProductDayArchiveView.as_view(), name='report-daily'),
    path('report/<int:year>/<str:month>/', views.ProductMonthArchiveView.as_view(), name='report-montly'),

    path('worker/', views.WorkerListView.as_view(), name='worker-list'),
    path('worker/create/', views.WorkerCreateView.as_view(), name='worker-create'),
    path('worker/<int:pk>/view/', views.WorkerDetailView.as_view(), name='worker-detail'),
]
