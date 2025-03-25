# models.py
from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name


class Supplier(models.Model):
    company_name = models.CharField(max_length=100)
    contact_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.company_name


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True)
    quantity_in_stock = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sku = models.CharField(max_length=50, unique=False,default=None)
    location = models.ForeignKey('Location', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('product-detail', args=[str(self.id)])

    def is_low_stock(self):
        return self.quantity_in_stock < 10  # Adjust threshold as needed

    def __str__(self):
        return f"{self.name} ({self.sku})"


class InventoryTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('PURCHASE', 'Purchase'),
        ('SALE', 'Sale'),
        ('ADJUSTMENT', 'Adjustment'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    related_order = models.CharField(max_length=100, blank=True)  # For purchase orders or sales orders

    def __str__(self):
        return f"{self.transaction_type} - {self.product.name} ({self.quantity})"


# Optional Models
class StockAlert(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    threshold = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Alert for {self.product.name} below {self.threshold}"


class Location(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"

class InventoryItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"

class InventoryReport(models.Model):
    date = models.DateField()
    total_sales = models.DecimalField(max_digits=10, decimal_places=2)
    total_purchases = models.DecimalField(max_digits=10, decimal_places=2)
    total_adjustments = models.DecimalField(max_digits=10, decimal_places=2)
    total_inventory = models.IntegerField()
    def __str__(self):
        return f"Inventory Report for {self.date}"

