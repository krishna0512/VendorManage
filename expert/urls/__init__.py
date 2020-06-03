from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.views.generic import TemplateView

from .. import views

app_name = 'expert'
urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name='index'),
    path('send_email/', views.SendEmailView.as_view(), name='send-email'),
    path('complaint_detail/', views.complaint_detail, name='complaint-detail'),
    # path('', auth_views.LoginView.as_view(template_name='expert/index.html'), name='index'),
    path('login/', auth_views.LoginView.as_view(template_name='expert/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('ajax/', include('expert.urls.ajax')),
    # path('product/', include('expert.urls.product')),

    path('report/<int:year>/<str:month>/<int:day>/', views.ProductDayArchiveView.as_view(), name='report-daily'),
    path('report/', views.ReportView.as_view(), name='report'),

]
