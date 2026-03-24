from django.db import models
from django_countries.fields import CountryField
from decimal import Decimal

# Create your models here.
class Company(models.Model):

    BUSINESS_TYPES = (
        ('etablissement', 'Etablissement'),
        ('societe', 'Societe'),
    )

    ESTABLISHMENT_TYPES = (
        ('pme', 'PME'),
        ('ipme', 'IPME'),
        ('ecs', 'Entreprise en commandite simple'),
    )

    COMPANY_TYPES = (
        ('sa', 'Societe par actions'),
        ('sarl', 'Societe a responsabilite limitee'),
        ('personnes', 'Societe de personnes'),
    )

    CURRENCY_CHOICES = (
        ('BIF', 'Franc Burundais (BIF)'),
        ('USD', 'Dollar Americain (USD)'),
        ('EUR', 'Euro (EUR)'),
        ('CDF', 'Franc Congolais (CDF)'),
    )

    name = models.CharField(max_length=200)
    owner_name = models.CharField(max_length=200)
    business_type = models.CharField(max_length=20, choices=BUSINESS_TYPES)
    sub_type = models.CharField(max_length=50, blank=True)
    registration_number = models.CharField(max_length=150)
    country = CountryField()
    province = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    address = models.CharField(max_length=255, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    currency = models.CharField(
        max_length=10,
        choices=CURRENCY_CHOICES,
        default='CDF'
    )
    tva = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    logo = models.ImageField(
        upload_to='company_logo/',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk and Company.objects.exists():
            raise ValidationError("Une seule entreprise est autorisée.")
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name