from django.urls import path

from expert.views import product as views

urlpatterns = [
    path('<int:pk>/update/', views.ProductUpdateView.as_view(), name='product-update'),
    path('create/<int:kit_number>/', views.ProductCreateView.as_view(), name='product-create'),
    path('<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product-delete'),
    path('<int:pk>/view/', views.ProductDetailView.as_view(), name='product-detail'),
    path('<int:pk>/return/', views.ProductReturnRedirectView.as_view(), name='product-return'),
    path('<int:pk>/split/', views.ProductSplitRedirectView.as_view(), name='product-split'),
]