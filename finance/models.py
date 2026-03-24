from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError
from django.utils import timezone
from django.db.models import Sum
from companie.models import Company

# Create your models here.
class CashRegister(models.Model):
    name = models.CharField(max_length=100)  # ex: Caisse 1
    shop = models.ForeignKey(Company, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)  # ouverte ou fermée
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.shop}"

    def get_balance(self):
        # Somme de toutes les opérations validées
        from finance.models import CashOperation
        total_sales = self.operations.filter(
            operation_type='SALE',
            validated_by_admin=True
        ).aggregate(models.Sum('amount'))['amount__sum'] or 0

        total_expenses = self.operations.filter(
            operation_type='EXPENSE',
            validated_by_admin=True
        ).aggregate(models.Sum('amount'))['amount__sum'] or 0

        return total_sales - total_expenses
    
class Cashier(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    cash_registers = models.ManyToManyField(CashRegister, blank=True, related_name='cashiers', null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    @property
    def today_sales_total(self):
        today = timezone.now().date()
        return self.sales.filter(
            created_at__date=today,
            status='completed'
        ).aggregate(
            total=models.Sum('total_amount')
        )['total'] or 0
    
# Opérations de caisse
class CashOperation(models.Model):

    SALE = 'SALE'
    EXPENSE = 'EXPENSE'
    CLOSURE = 'CLOSURE'
    OTHER = 'OTHER'

    OPERATION_TYPE = [
        (SALE, 'Vente produit'),
        (EXPENSE, 'Dépense'),
        (CLOSURE, 'Clôture de caisse'),
        (OTHER, 'Autre'),
    ]

    cashier = models.ForeignKey(
        'Cashier',
        on_delete=models.PROTECT,
        related_name='operations'
    )

    cash_register = models.ForeignKey(
        CashRegister,
        on_delete=models.PROTECT,
        related_name='operations',
        null=True
    )

    operation_type = models.CharField(max_length=20, choices=OPERATION_TYPE)
    description = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    validated_by_admin = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_operation_type_display()} - {self.amount} ({self.cash_register})"