from django.urls import path

from expert.views import invoice as views

urlpatterns = [
    path('', views.InvoiceListView.as_view(), name='invoice-list'),
    path('create/', views.InvoiceCreateView.as_view(), name='invoice-create'),
    path('<slug:slug>/view/printable/', views.InvoicePrintableView.as_view(), name='invoice-printable'),
    path('<slug:slug>/view/', views.InvoiceDetailView.as_view(), name='invoice-detail'),
    path('<slug:slug>/update/', views.InvoiceUpdateView.as_view(), name='invoice-update'),

    path('<int:invoice_pk>/add/<int:challan_pk>/', views.InvoiceChallanOperationView.as_view(), {'operation':'add'}, name='invoice-add-challan'),
    path('<int:invoice_pk>/remove/<int:challan_pk>/', views.InvoiceChallanOperationView.as_view(), {'operation':'remove'}, name='invoice-remove-challan'),
]