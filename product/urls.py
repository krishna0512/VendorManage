from django.urls import path, include

from . import views

app_name = 'product'
urlpatterns = [
    path('api/', include('product.api.urls')),

    path('<int:pk>/update/', views.ProductUpdateView.as_view(), name='update'),
    path('create/<int:kit_number>/', views.ProductCreateView.as_view(), name='create'),
    path('<int:pk>/delete/', views.ProductDeleteView.as_view(), name='delete'),
    path('<int:pk>/view/', views.ProductDetailView.as_view(), name='detail'),
    path('<int:pk>/return/', views.ProductReturnRedirectView.as_view(), name='return'),
    path('<int:pk>/split/', views.ProductSplitRedirectView.as_view(), name='split'),
]