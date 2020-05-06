from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.views.generic import TemplateView

from .. import views

app_name = 'expert'
urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name='index'),
    path('send_email/', views.send_email, name='send-email'),
    # path('', auth_views.LoginView.as_view(template_name='expert/index.html'), name='index'),
    path('login/', auth_views.LoginView.as_view(template_name='expert/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('ajax/', include('expert.urls.ajax')),
    path('kit/', include('expert.urls.kit')),
    path('product/', include('expert.urls.product')),
    path('challan/', include('expert.urls.challan')),
    path('customer/', include('expert.urls.customer')),
    path('invoice/', include('expert.urls.invoice')),
    path('worker/', include('expert.urls.worker')),

    path('report/<int:year>/<str:month>/<int:day>/', views.ProductDayArchiveView.as_view(), name='report-daily'),
    path('report/<int:year>/<str:month>/', views.ProductMonthArchiveView.as_view(), name='report-monthly'),

]
