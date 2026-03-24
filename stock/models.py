from django.utils import timezone

from django.db import models
from django.forms import ValidationError
from django.db.models import Sum
from product.models import Product, Supplier
from django.contrib.auth.models import User, Group

# Create your models here.
class StockEntry(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(default=timezone.now)
    quantity = models.PositiveIntegerField()
    remaining_quantity = models.PositiveIntegerField(editable=False, null=True)
    unit_cost = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    total_cost = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    entered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    reason = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):

        if not self.pk:
            self.remaining_quantity = self.quantity
        self.total_cost = self.unit_cost * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"

class StockExit(models.Model):
    EXIT_REASON = [
        ('sale', 'Vente'),
        ('loss', 'Perte'),
        ('damage', 'Produit endommagé'),
        ('adjustment', 'Ajustement'),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    date = models.DateTimeField(default=timezone.now)
    reason = models.CharField(max_length=20, choices=EXIT_REASON)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):

        if not self.pk:
            self.apply_stock_deduction()
        super().save(*args, **kwargs)

    def apply_stock_deduction(self):
        quantity_to_deduct = self.quantity
        if self.product.management_method == 'FIFO':
            entries = self.product.stockentry_set.filter(
                remaining_quantity__gt=0
            ).order_by('date')

        else:  # LIFO
            entries = self.product.stockentry_set.filter(
                remaining_quantity__gt=0
            ).order_by('-date')

        for entry in entries:
            if quantity_to_deduct <= 0:
                break
            if entry.remaining_quantity >= quantity_to_deduct:
                entry.remaining_quantity -= quantity_to_deduct
                entry.save()
                quantity_to_deduct = 0
            else:
                quantity_to_deduct -= entry.remaining_quantity
                entry.remaining_quantity = 0
                entry.save()
        if quantity_to_deduct > 0:
            raise ValueError("Stock insuffisant")