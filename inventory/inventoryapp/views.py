# views.py
from django.contrib.auth import authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .form import InventoryItemForm
from .models import Product, Category, Supplier, InventoryTransaction, Inventory, InventoryItem
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponse
from .models import Category, Supplier
import csv


# Product Views
class ProductList(ListView):
    model = Product
    template_name = 'inventory/product_list.html'
    context_object_name = 'products'
    paginate_by = 10

class ProductDetail(DetailView):
    model = Product
    template_name = 'inventory/product_detail.html'

class ProductCreate(CreateView):
    model = Product
    template_name = 'inventory/product_form.html'
    fields = ['name', 'description', 'category', 'supplier', 'price','sku']
    success_url = reverse_lazy('product_list')

class ProductUpdate(UpdateView):
    model = Product
    template_name = 'inventory/product_form.html'
    fields = ['name', 'description', 'category', 'supplier', 'quantity', 'price']
    success_url = reverse_lazy('product_list')

class ProductDelete(DeleteView):
    model = Product
    template_name = 'inventory/product_confirm_delete.html'
    success_url = reverse_lazy('product_list')

# Category Views
class CategoryList(ListView):
    model = Category
    template_name = 'inventory/category_list.html'
    context_object_name = 'categories'

class CategoryCreate(CreateView):
    model = Category
    template_name = 'inventory/category_form.html'
    fields = ['name', 'parent']
    success_url = reverse_lazy('category_list')

# Supplier Views
class SupplierList(ListView):
    model = Supplier
    template_name = 'inventory/supplier_list.html'
    context_object_name = 'suppliers'

class SupplierCreate(CreateView):
    model = Supplier
    template_name = 'inventory/supplier_form.html'
    fields = ['email', 'phone']
    success_url = reverse_lazy('supplier_list')


# views.py
class InventoryItemListView(LoginRequiredMixin, ListView):
    model = Inventory
    template_name = 'inventory/item_list.html'
    context_object_name = 'items'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(category__name__icontains=search_query) |
                Q(supplier__name__icontains=search_query)
            )
        return queryset.select_related('category', 'supplier')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['low_stock_items'] = InventoryItem.objects.filter(
            stock__lte=models.F('low_stock_threshold')
        )[:5]
        return context


class InventoryItemCreateView(LoginRequiredMixin, CreateView):
    model = InventoryTransaction
    form_class = InventoryItemForm
    template_name = 'inventory/item_form.html'
    success_url = reverse_lazy('item-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Item created successfully!')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class InventoryItemUpdateView(LoginRequiredMixin, UpdateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = 'inventory/item_form.html'
    success_url = reverse_lazy('item-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Item updated successfully!')
        return response


class InventoryItemDeleteView(LoginRequiredMixin, DeleteView):
    model = InventoryItem
    template_name = 'inventory/item_confirm_delete.html'
    success_url = reverse_lazy('item-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Item deleted successfully!')
        return super().delete(request, *args, **kwargs)


@login_required
def export_inventory_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="inventory.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Category', 'Supplier', 'Stock', 'Price', 'Low Stock Threshold'])

    items = InventoryItem.objects.select_related('category', 'supplier').all()
    for item in items:
        writer.writerow([
            item.name,
            item.category.name if item.category else '',
            item.supplier.name if item.supplier else '',
            item.stock,
            item.price,
            item.low_stock_threshold
        ])

    return response


@login_required
def inventory_dashboard(request):
    items = InventoryItem.objects.select_related('category', 'supplier')

    # Search functionality
    search_query = request.GET.get('q')
    if search_query:
        items = items.filter(
            Q(name__icontains=search_query) |
            Q(category__name__icontains=search_query) |
            Q(supplier__name__icontains=search_query)
        )

    # Low stock alerts
    low_stock_items = items.filter(stock__lte=models.F('low_stock_threshold'))

    # CSV export
    if 'export' in request.GET:
        return export_inventory_csv(request)

    context = {
        'items': items,
        'search_query': search_query,
        'low_stock_items': low_stock_items,
    }
    return render(request, 'inventory/dashboard.html', context)

def home(request):
    return render(request, 'inventory/home.html')

def dashboard(request):
    return render(request, 'inventory/dashboard.html')


def item_list(request):
    items = InventoryItem.objects.select_related('category', 'supplier')
    # Search functionality
    search_query = request.GET.get('q')
    if search_query:
        items = items.filter(
            Q(name__icontains=search_query) |
            Q(category__name__icontains=search_query) |
            Q(supplier__name__icontains=search_query)
        )
    # Low stock alerts
    low_stock_items = items.filter(stock__lte=models.F('low_stock_threshold'))
    context = {
        'items': items,
        'search_query': search_query,
        'low_stock_items': low_stock_items,
    }
    return render(request, 'inventory/item_list.html', context)

#Login View
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password incorrect!')
            return redirect('login')
    else:
        return render(request, 'inventory/login.html')

#logout
def logout_view(request):
    logout(request)
    return redirect('login')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already taken!')
                return redirect('register')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email already taken!')
                return redirect('register')
            else:
                user = User.objects.create_user(username, email, password)
                user.save()
                login(request, user)
                return redirect('home')
        else:
            messages.error(request, 'Passwords do not match!')
            return redirect('register')
    else:
        return render(request, 'inventory/register.html')

