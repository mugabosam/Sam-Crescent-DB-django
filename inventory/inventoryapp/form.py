from .models import *
from django.forms import ModelForm, TextInput


class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = '__all__'
        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
            'parent': TextInput(attrs={'class': 'form-control'}),
        }

class SupplierForm(ModelForm):
    class Meta:
        model = Supplier
        fields = '__all__'
        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
            'email': TextInput(attrs={'class': 'form-control'}),
            'phone': TextInput(attrs={'class': 'form-control'}),
            'address': TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Company Name',
            'email': 'Email',
            'phone': 'Phone',
            'address': 'Address',
        }
class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
            'price': TextInput(attrs={'class': 'form-control'}),
            'description': TextInput(attrs={'class': 'form-control'}),
            'category': TextInput(attrs={'class': 'form-control'}),
            'supplier': TextInput(attrs={'class': 'form-control'}),
            'quantity_in_stock': TextInput(attrs={'class': 'form-control'}),
           'sku': TextInput(attrs={'class': 'form-control'}),
            'location': TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Product Name',
            'price': 'Price',
            'description': 'Description',
            'category': 'Category',
           'supplier': 'Supplier',
            'quantity_in_stock': 'Quantity in Stock',
           'sku': 'SKU',
            'location': 'Location',
        }
class InventoryTransactionForm(ModelForm):
    class Meta:
        model = InventoryTransaction
        fields = '__all__'
        widgets = {
            'product': TextInput(attrs={'class': 'form-control'}),
            'location': TextInput(attrs={'class': 'form-control'}),
            'transaction_type': TextInput(attrs={'class': 'form-control'}),
            'notes': TextInput(attrs={'class': 'form-control'}),
           'related_order': TextInput(attrs={'class': 'form-control'}),
        }
class InventoryItemForm(ModelForm):
    class Meta:
        model = InventoryItem
        fields = '__all__'
        widgets = {
            'product': TextInput(attrs={'class': 'form-control'}),
            'location': TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'product': 'Product',
            'location': 'Location',
            'quantity_in_stock': 'Quantity in Stock',

        }

class InventoryReportForm(ModelForm):
    class Meta:
        model = InventoryReport
        fields = '__all__'
        widgets = {
            'product': TextInput(attrs={'class': 'form-control'}),
            'location': TextInput(attrs={'class': 'form-control'}),
            'from_date': TextInput(attrs={'class': 'form-control'}),
            'to_date': TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'product': 'Product',
            'location': 'Location',
            'from_date': 'From Date',
            'to_date': 'To Date',
        }