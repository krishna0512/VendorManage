from django.urls import path

from expert.views import ajax as views

urlpatterns = [
    path('invoice/<int:pk>/send_email/', views.email_invoice, name='email-invoice'),
    path('product/<int:pk>/complete/', views.ProductCompleteView.as_view(), name='product-complete'),
    path('product/<int:product_pk>/assignto/<int:worker_pk>/', views.ProductAssignView.as_view(), name='product-assign'),
    path('kit/<int:pk>/change_completion_date/', views.KitChangeCompletionDate.as_view(), name='kit-change-product-completion'),
    path('validate/worker/username/', views.validate_create_worker_username, name='validate-create-worker-username'),
]