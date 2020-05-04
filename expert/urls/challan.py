from django.urls import path

from expert import views

urlpatterns = [
    path('', views.ChallanListView.as_view(), name='challan-list'),
    path('<slug:slug>/view/', views.ChallanDetailView.as_view(), name='challan-detail'),
    path('<int:pk>/init/', views.ChallanInitRedirectView.as_view(), name='challan-init'),
    path('<slug:slug>/view/printable/', views.ChallanPrintableView.as_view(), name='challan-printable'),
    path('<slug:slug>/delete/', views.ChallanDeleteView.as_view(), name='challan-delete'),
    # url loading the gatepass 
    path('<int:pk>/gatepass/', views.challan_gatepass, name='challan-gatepass'),
]