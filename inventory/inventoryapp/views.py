# views.py
from django.contrib.auth import authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q, F, Avg
from django.template.loader import render_to_string
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .form import InventoryItemForm, CategoryForm
from .models import Product, Category, Supplier, InventoryTransaction, Inventory, InventoryItem
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponse
from .models import Category, Supplier
import csv
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.forms import AuthenticationForm
from .models import LoginLog
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.views import View
from .form import CustomUserCreationForm  # We'll create this
from .models import RegistrationLog  # For tracking registrations

# inventory/views.py
from django.views.generic import ListView, View
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
import csv
import xlsxwriter
import io
from .models import Product, Category, Supplier, InventoryTransaction


class ReportListView(ListView):
    template_name = 'inventory/report_list.html'
    context_object_name = 'available_reports'

    def get_queryset(self):
        return [
            {'name': 'Inventory Summary', 'slug': 'inventory-summary'},
            {'name': 'Low Stock Report', 'slug': 'low-stock'},
            {'name': 'Category Analysis', 'slug': 'category-analysis'},
            {'name': 'Supplier Performance', 'slug': 'supplier-performance'},
            {'name': 'Transaction History', 'slug': 'transaction-history'},
        ]


class ReportDownloadView(View):
    report_types = {
        'inventory-summary': {
            'title': 'Inventory Summary Report',
            'queryset': Product.objects.all(),
            'filename': 'inventory_summary',
            'fields': ['name', 'category__name', 'quantity_in_stock', 'price'],
            'headers': ['Product Name', 'Category', 'Current Stock', 'Price'],
        },
        'low-stock': {
            'title': 'Low Stock Report',
            # 'queryset': Product.objects.filter(quantity_in_stock__lt=F('reorder_level')),
            'filename': 'low_stock_report',
            'fields': ['name', 'category__name', 'quantity_in_stock'],
            'headers': ['Product Name', 'Category', 'Current Stock'],
        },
        'category-analysis': {
            'title': 'Category Analysis Report',
            'queryset': Category.objects.annotate(
                product_count=Count('product'),
                total_value=Sum('product__price')
            ),
            'filename': 'category_analysis',
            'fields': ['name', 'product_count', 'total_value'],
            'headers': ['Category', 'Product Count', 'Total Inventory Value'],
        },
        'supplier-performance': {
            'title': 'Supplier Performance Report',
            'queryset': Supplier.objects.annotate(
                product_count=Count('product'),
                # avg_delivery_time=Avg('product__lead_time')
            ),
            'filename': 'supplier_performance',
            'fields': ['name', 'email', 'product_count', 'avg_delivery_time'],
            'headers': ['Supplier Name', 'Email', 'Products Supplied', 'Avg Delivery Time (days)'],
        },
        'transaction-history': {
            'title': 'Transaction History Report',
            'queryset': InventoryTransaction.objects.all(),
            'filename': 'transaction_history',
            'fields': ['product__name', 'transaction_type', 'quantity', 'created_at', 'user__username'],
            'headers': ['Product', 'Transaction Type', 'Quantity', 'Date', 'User'],
        },
    }

    def get(self, request, report_type, format):
        if report_type not in self.report_types:
            return HttpResponse("Invalid report type", status=400)

        report_config = self.report_types[report_type]
        queryset = report_config['queryset']
        filename = report_config['filename']

        # Apply date filters if provided
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if start_date and end_date:
            if report_type == 'transaction-history':
                queryset = queryset.filter(created_at__range=[start_date, end_date])
            elif report_type in ['inventory-summary', 'low-stock']:
                queryset = queryset.filter(updated_at__range=[start_date, end_date])

        if format == 'csv':
            return self.generate_csv(queryset, report_config, filename)
        elif format == 'excel':
            return self.generate_excel(queryset, report_config, filename)
        elif format == 'pdf':
            return self.generate_pdf(queryset, report_config, filename)
        else:
            return HttpResponse("Invalid format", status=400)

    def generate_csv(self, queryset, report_config, filename):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'

        writer = csv.writer(response)
        writer.writerow(report_config['headers'])

        for item in queryset:
            row = []
            for field in report_config['fields']:
                if '__' in field:
                    # Handle related field lookups
                    parts = field.split('__')
                    value = item
                    for part in parts:
                        value = getattr(value, part, '')
                    row.append(str(value))
                else:
                    row.append(str(getattr(item, field, '')))
            writer.writerow(row)

        return response

    def generate_excel(self, queryset, report_config, filename):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()

        # Add header
        bold = workbook.add_format({'bold': True})
        for col, header in enumerate(report_config['headers']):
            worksheet.write(0, col, header, bold)

        # Add data
        for row, item in enumerate(queryset, start=1):
            for col, field in enumerate(report_config['fields']):
                if '__' in field:
                    # Handle related field lookups
                    parts = field.split('__')
                    value = item
                    for part in parts:
                        value = getattr(value, part, '')
                    worksheet.write(row, col, str(value))
                else:
                    worksheet.write(row, col, str(getattr(item, field, '')))

        workbook.close()
        output.seek(0)

        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'
        return response

    def generate_pdf(self, queryset, report_config, filename):
        # You would implement PDF generation here using ReportLab or WeasyPrint
        # This is a placeholder implementation
        from django.template.loader import render_to_string
        from weasyprint import HTML

        html_string = render_to_string('inventory/report_pdf.html', {
            'title': report_config['title'],
            'headers': report_config['headers'],
            'data': [
                [str(getattr(item, field, '')) for field in report_config['fields']]
                for item in queryset
            ],
            'generated_at': timezone.now(),
        })
        html = HTML(string=html_string)
        pdf = html.write_pdf()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
        return response

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

    context = {
        'items': items,
        'search_query': search_query,
    }
    return render(request, 'inventory/item_list.html', context)

#Login View


class LoginView(View):
    template_name = 'inventory/login.html'

    @method_decorator(never_cache)
    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        form = AuthenticationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                auth_login(request, user)
                self._log_login_attempt(user, True)

                # Check if 'next' parameter exists in the request
                next_url = request.POST.get('next', '')
                if next_url:
                    return redirect(next_url)
                return redirect('home')

        # If form is invalid or authentication fails
        username = request.POST.get('username', '')
        if username:
            try:
                user = User.objects.get(username=username)
                self._log_login_attempt(user, False)
            except User.DoesNotExist:
                pass

        messages.error(request, 'Invalid username or password. Please try again.')
        return render(request, self.template_name, {'form': form})

    def _log_login_attempt(self, user, success):
        """Log login attempts to database"""
        LoginLog.objects.create(
            user=user,
            success=success,
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
#logout
def logout_view(request):
    logout(request)
    return redirect('login')




class RegisterView(View):
    template_name = 'inventory/register.html'

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        form = CustomUserCreationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()

            # Log the registration
            self._log_registration(user)

            # Authenticate and login the user
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                auth_login(request, user)
                messages.success(request, 'Registration successful! Welcome to InventoryPro.')
                return redirect('home')

        # If form is invalid
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field.title()}: {error}")

        return render(request, self.template_name, {'form': form})

    def _log_registration(self, user):
        """Log registration to database"""
        RegistrationLog.objects.create(
            user=user,
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )


def itemAdd(request):
    if request.method == 'POST':
        form = InventoryItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('item-list')
    else:
        form = InventoryItemForm()
    return render(request, 'inventory/item_form.html', {'form': form})

def itemEdit(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    if request.method == 'POST':
        form = InventoryItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('item-list')
    else:
        form = InventoryItemForm(instance=item)
    return render(request, 'inventory/item_form.html', {'form': form})

def itemDelete(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('item-list')
    return render(request, 'inventory/item_confirm_delete.html', {'item': item})

def categoryAdd(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CategoryForm()
    return render(request, 'inventory/category_form.html', {'form': form})

def categoryEdit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'inventory/category_form.html', {'form': form})

def categoryDelete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('category_list')
    return render(request, 'inventory/category_confirm_delete.html', {'category': category})

