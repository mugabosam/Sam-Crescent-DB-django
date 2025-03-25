from tkinter import Image

from django.contrib import admin
from .models import *

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'quantity_in_stock', 'price')
    search_fields = ('name', 'sku')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    search_fields = ('name',)

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'address')
    search_fields = ('name', 'description', 'address')

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'contact_name', 'email', 'phone')
    search_fields = ('company_name', 'contact_name', 'email', 'phone')

@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ('product', 'transaction_type', 'quantity', 'timestamp', 'notes', 'related_order')
    search_fields = ('product__name', 'transaction_type', 'notes', 'related_order')
    list_filter = ('product', 'transaction_type')

@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = ('product', 'threshold', 'is_active')
    search_fields = ('product__name',)

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'location')
    search_fields = ('product__name', 'location__name')





