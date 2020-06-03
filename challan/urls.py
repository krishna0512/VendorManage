from django.urls import path

from . import views

app_name = 'challan'
urlpatterns = [
    path('', views.ChallanListView.as_view(), name='list'),
    path('<slug:slug>/view/', views.ChallanDetailView.as_view(), name='detail'),
    path('<int:pk>/create/', views.ChallanCreateRedirectView.as_view(), name='create'),
    path('<slug:slug>/view/printable/', views.ChallanPrintableView.as_view(), name='printable'),
    path('<slug:slug>/delete/', views.ChallanDeleteView.as_view(), name='delete'),
    path('<int:pk>/update/', views.ChallanUpdateView.as_view(), name='update'),
    # url loading the gatepass 
    path('<int:pk>/gatepass/', views.challan_gatepass, name='gatepass'),
    path('<int:pk>/excel/', views.challan_excel, name='excel'),
]