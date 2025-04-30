
from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name="store"),
    path('category/<slug:category_slug>/', views.store, name="products_by_category"),
    path('category/<slug:category_slug>/<slug:product_slug>/', views.product_detail, name="product_detail"),
    path('search/', views.search, name='search'),
    path('submit_review/<int:product_id>/', views.submit_review, name='submit_review'),
    path('min-max-price-filter/', views.min_max_filter, name="min_max_filter"),

    # Vendor URLs
    path('vendor/add-product/', views.create_product, name='create_product'),
    path('vendor/edit-product/<int:pk>/', views.update_product, name='update_product'),
    path('vendor/products/', views.vendor_product_list, name='vendor_product_list'),
    path('vendor/orders/', views.vendor_order_list, name='vendor_order_list'),
    path('vendor/out-of-stock/products/', views.out_of_stock_products, name='out_of_stock_products'),
]
