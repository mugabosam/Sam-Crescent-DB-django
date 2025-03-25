from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # Products
    path('products/', views.ProductList.as_view(), name='product_list'),
    path('product/<int:pk>/', views.ProductDetail.as_view(), name='product_detail'),
    path('product/new/', views.ProductCreate.as_view(), name='product_create'),
    path('product/<int:pk>/edit/', views.ProductUpdate.as_view(), name='product_update'),
    path('product/<int:pk>/delete/', views.ProductDelete.as_view(), name='product_delete'),

    # Categories
    path('categories/', views.CategoryList.as_view(), name='category_list'),
    path('category/new/', views.CategoryCreate.as_view(), name='category_create'),

    # Suppliers
    path('suppliers/', views.SupplierList.as_view(), name='supplier_list'),
    path('supplier/new/', views.SupplierCreate.as_view(), name='supplier_create'),
    path('dashboard/', views.dashboard, name='dashboard_list'),
    path('item', views.item_list, name='item-create'),
    path('register/', views.register, name='register'),
]
