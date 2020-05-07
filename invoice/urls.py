from django.urls import path

from . import views

app_name = 'invoice'
urlpatterns = [
    path('', views.InvoiceListView.as_view(), name='list'),
    path('create/', views.InvoiceCreateView.as_view(), name='create'),
    path('<slug:slug>/view/printable/', views.InvoicePrintableView.as_view(), name='printable'),
    path('<slug:slug>/view/', views.InvoiceDetailView.as_view(), name='detail'),
    path('<slug:slug>/update/', views.InvoiceUpdateView.as_view(), name='update'),

    path('<int:invoice_pk>/add/<int:challan_pk>/', views.InvoiceChallanOperationView.as_view(), {'operation':'add'}, name='add-challan'),
    path('<int:invoice_pk>/remove/<int:challan_pk>/', views.InvoiceChallanOperationView.as_view(), {'operation':'remove'}, name='remove-challan'),
]