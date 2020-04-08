from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.views.generic import TemplateView

from expert import views

app_name = 'expert'
urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name='index'),
    path('kit/', views.KitListView.as_view(), name='kit-list'),
    path('kit/create/', views.KitCreateView.as_view(), name='kit-create'),
    path('kit/<slug:slug>/update/', views.KitUpdateView.as_view(), name='kit-update'),
    path('kit/<slug:slug>/view/', views.KitDetailView.as_view(), name='kit-detail'),
    path('kit/<slug:slug>/delete/', views.KitDeleteView.as_view(), name='kit-delete'),

    path('product/<int:pk>/update/', views.ProductUpdateView.as_view(), name='product-update'),
    path('product/create/<int:kit_number>/', views.ProductCreateView.as_view(), name='product-create'),
    path('product/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product-delete'),
    path('product/<int:pk>/view/', views.ProductDetailView.as_view(), name='product-detail'),

    path('product/<int:product_pk>/assignto/<int:worker_pk>/', views.product_assign, name='product-assign'),
    path('product/<int:pk>/complete/', views.product_complete, name='product-complete'),
    path('product/<int:pk>/return/', views.product_return, name='product-return'),
    path('kit/<int:pk>/uncomplete/', views.kit_uncomplete, name='kit-uncomplete'),

    path('report/<int:year>/<str:month>/<int:day>/', views.ProductDayArchiveView.as_view(), name='report-daily'),
    path('report/<int:year>/<str:month>/', views.ProductMonthArchiveView.as_view(), name='report-monthly'),

    path('challan/<int:pk>/init/', views.challan_init, name='challan-init'),
    path('challan/', views.ChallanListView.as_view(), name='challan-list'),
    path('challan/<slug:slug>/view/', views.ChallanDetailView.as_view(), name='challan-detail'),
    path('challan/<slug:slug>/view/printable/', views.ChallanPrintableView.as_view(), name='challan-printable'),
    path('challan/<slug:slug>/delete/', views.ChallanDeleteView.as_view(), name='challan-delete'),

    path('invoice/create/', views.InvoiceCreateView.as_view(), name='invoice-create'),
    path('invoice/printable', TemplateView.as_view(template_name='expert/invoice_detail_printable.html'), name='invoice-printable'),

    path('worker/', views.WorkerListView.as_view(), name='worker-list'),
    path('worker/create/', views.WorkerCreateView.as_view(), name='worker-create'),
    path('worker/<int:pk>/view/', views.WorkerDetailView.as_view(), name='worker-detail'),
    path('worker/<int:pk>/update/', views.WorkerUpdateView.as_view(), name='worker-update'),
    path('worker/<int:pk>/delete/', views.WorkerDeleteView.as_view(), name='worker-delete'),
]
