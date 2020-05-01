from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.views.generic import TemplateView

from expert import views

app_name = 'expert'
urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name='index'),
    path('send_email/', views.send_email, name='send-email'),
    # path('', auth_views.LoginView.as_view(template_name='expert/index.html'), name='index'),
    path('login/', auth_views.LoginView.as_view(template_name='expert/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('ajax/invoice/<int:pk>/send_email/', views.email_invoice, name='email-invoice'),
    path('ajax/product/<int:pk>/complete/', views.ProductCompleteView.as_view(), name='product-complete'),
    path('ajax/product/<int:product_pk>/assignto/<int:worker_pk>/', views.ProductAssignView.as_view(), name='product-assign'),
    path('ajax/kit/<int:pk>/change_completion_date/', views.KitChangeCompletionDate.as_view(), name='kit-change-product-completion'),
    path('ajax/validate/worker/username/', views.validate_create_worker_username, name='validate-create-worker-username'),

    path('kit/', views.KitListView.as_view(), name='kit-list'),
    path('kit/create/', views.KitCreateView.as_view(), name='kit-create'),
    path('kit/<slug:slug>/update/', views.KitUpdateView.as_view(), name='kit-update'),
    path('kit/<slug:slug>/view/', views.KitDetailView.as_view(), name='kit-detail'),
    path('kit/<slug:slug>/delete/', views.KitDeleteView.as_view(), name='kit-delete'),

    path('product/<int:pk>/update/', views.ProductUpdateView.as_view(), name='product-update'),
    path('product/create/<int:kit_number>/', views.ProductCreateView.as_view(), name='product-create'),
    path('product/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product-delete'),
    path('product/<int:pk>/view/', views.ProductDetailView.as_view(), name='product-detail'),

    path('product/<int:pk>/return/', views.ProductReturnRedirectView.as_view(), name='product-return'),
    path('kit/<int:pk>/uncomplete/', views.KitUncompleteRedirectView.as_view(), name='kit-uncomplete'),
    # path('kit/<int:pk>/uncomplete/', views.kit_uncomplete, name='kit-uncomplete'),

    path('report/<int:year>/<str:month>/<int:day>/', views.ProductDayArchiveView.as_view(), name='report-daily'),
    path('report/<int:year>/<str:month>/', views.ProductMonthArchiveView.as_view(), name='report-monthly'),

    path('challan/<int:pk>/init/', views.ChallanInitRedirectView.as_view(), name='challan-init'),
    path('challan/', views.ChallanListView.as_view(), name='challan-list'),
    path('challan/<slug:slug>/view/', views.ChallanDetailView.as_view(), name='challan-detail'),
    path('challan/<slug:slug>/view/printable/', views.ChallanPrintableView.as_view(), name='challan-printable'),
    path('challan/<slug:slug>/delete/', views.ChallanDeleteView.as_view(), name='challan-delete'),
    # url for downloading the gatepass 
    path('challan/<int:pk>/gatepass/', views.challan_gatepass, name='challan-gatepass'),

    path('invoice/', views.InvoiceListView.as_view(), name='invoice-list'),
    path('invoice/create/', views.InvoiceCreateView.as_view(), name='invoice-create'),
    path('invoice/<slug:slug>/view/printable/', views.InvoicePrintableView.as_view(), name='invoice-printable'),
    path('invoice/<slug:slug>/view/', views.InvoiceDetailView.as_view(), name='invoice-detail'),
    path('invoice/<slug:slug>/update/', views.InvoiceUpdateView.as_view(), name='invoice-update'),

    path('invoice/<int:invoice_pk>/add/<int:challan_pk>/', views.InvoiceChallanOperationView.as_view(), {'operation':'add'}, name='invoice-add-challan'),
    path('invoice/<int:invoice_pk>/remove/<int:challan_pk>/', views.InvoiceChallanOperationView.as_view(), {'operation':'remove'}, name='invoice-remove-challan'),

    path('worker/', views.WorkerListView.as_view(), name='worker-list'),
    path('worker/create/', views.WorkerCreateView.as_view(), name='worker-create'),
    path('worker/<int:pk>/view/', views.WorkerDetailView.as_view(), name='worker-detail'),
    path('worker/<int:pk>/update/', views.WorkerUpdateView.as_view(), name='worker-update'),
    path('worker/<int:pk>/delete/', views.WorkerDeleteView.as_view(), name='worker-delete'),
]
