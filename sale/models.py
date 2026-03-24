from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from decimal import Decimal

from finance.models import Cashier, CashRegister
from product.models import Product
from stock.models import StockExit
from companie.models import Company

# Create your models here.
# Vente et items
class Sale(models.Model):
    STATUS_CHOICES = [
        ('draft', 'En cours'),
        ('completed', 'Finalisée'),
    ]
    cashier = models.ForeignKey(Cashier, on_delete=models.SET_NULL, null=True, related_name='sales')
    register = models.ForeignKey(CashRegister, on_delete=models.SET_NULL, null=True)
    client_name = models.CharField(max_length=200, blank=True, null=True)
    client_phone = models.CharField(max_length=20, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total_profit = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    tax = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    validated_by_admin = models.BooleanField(default=False)
    validated_at = models.DateTimeField(null=True, blank=True)
    def calculate_totals(self):
        company = Company.objects.first()
        total = self.items.aggregate(
            total=Sum(
                ExpressionWrapper(
                    F('quantity') * F('selling_price'),
                    output_field=DecimalField()
                )
            )
        )['total'] or 0
        self.total_amount = total
        # Exemple TVA 16%
        if company:
            self.tax = total * company.tva
        else:
            self.tax = 0
        self.save()
    def __str__(self):
        return f"Sale #{self.id} - {self.total_amount}"

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    @property
    def total_price(self):
        return self.quantity * self.selling_price
    @property
    def profit(self):
        return (self.selling_price - self.purchase_price) * self.quantity
    def save(self, *args, **kwargs):
        if not self.pk:  # seulement si création
            if self.quantity > self.product.current_stock:
                raise ValueError("Stock insuffisant")

            # Création sortie stock
            StockExit.objects.create(
                product=self.product,
                quantity=self.quantity,
                reason='sale',
                performed_by=self.sale.cashier.user
            )
        super().save(*args, **kwargs)
        # Recalculer la vente
        sale = self.sale
        sale.total_amount = sum(item.total_price for item in sale.items.all())
        sale.total_profit = sum(item.profit for item in sale.items.all())
        sale.save()
    def delete(self, *args, **kwargs):
        # Remettre le stock
        self.product.current_stock += self.quantity
        self.product.save()
        super().delete(*args, **kwargs)
        # Recalculer la vente
        sale = self.sale
        sale.total_amount = sum(item.total_price for item in sale.items.all())
        sale.total_profit = sum(item.profit for item in sale.items.all())
        sale.save()
    def __str__(self):
        return str(self.product)