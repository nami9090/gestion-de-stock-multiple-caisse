from django.db import models
from django.db.models import Sum
from decimal import Decimal

# Create your models here.
class CategoryProduct(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Product(models.Model):

    MANAGEMENT_METHODE_TYPE = [
        ('FIFO','FIFO'),
        ('LIFO','LIFO'),
    ]
    category = models.ForeignKey(
        CategoryProduct,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products"
    )
    name = models.CharField(max_length=200)
    perishable = models.BooleanField(default=False)
    expiration_date = models.DateField(null=True, blank=True)
    management_method = models.CharField(max_length=10, choices=MANAGEMENT_METHODE_TYPE, default='FIFO')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Prix d'achat visible uniquement par admin
    purchase_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    selling_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    minimum_stock = models.IntegerField(default=5)

    def __str__(self):
        return self.name
    
    @property
    def current_stock(self):
        return self.stockentry_set.aggregate(
            total=Sum('remaining_quantity')
        )['total'] or 0
    
    @property
    def profit_margin(self):
        if self.purchase_price and self.selling_price:
            return self.selling_price - self.purchase_price
        return Decimal('0')
    
    @property
    def marge_total(self):
        return self.current_stock * self.profit_margin

    @property
    def stock_value(self):
        entries = self.stockentry_set.all()
        total = Decimal('0')

        for entry in entries:
            if entry.remaining_quantity and entry.total_cost:
                unit_cost = entry.total_cost / entry.quantity
                total += unit_cost * entry.remaining_quantity
        return total
    
class Supplier(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name