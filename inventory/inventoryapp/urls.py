from django.urls import path
from . import views
from .views import LoginView, RegisterView, ReportDownloadView, ReportListView

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
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
    path('item/', views.item_list, name='item-list'),
    path('reports/', ReportListView.as_view(), name='report_list'),
    path('reports/download/<str:report_type>/<str:format>/', ReportDownloadView.as_view(), name='report_download'),
    path('item/Add/', views.itemAdd, name='item-create'),
    path('item/Edit/<int:pk>/', views.itemEdit, name='item_edit'),
    path('item/Delete/<int:pk>/', views.itemDelete, name='item_delete'),
    path('categories/Add/', views.categoryAdd, name='category_add'),
    path('categories/Edit/<int:pk>/', views.categoryEdit, name='category_update'),
    path('categories/Delete/<int:pk>/', views.categoryDelete, name='category_delete'),
]
