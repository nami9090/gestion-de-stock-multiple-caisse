from django.shortcuts import render
from django.db.models import Sum, Count, F, DecimalField, ExpressionWrapper
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta

from product.models import Product
from sale.models import Sale, SaleItem
# Create your views here.

def rapport_journalier(request):
    today = timezone.now().date()
    ventes = Sale.objects.filter(
        created_at__date=today, 
        status='completed'
    )
    total_ventes = ventes.count()
    total_montant = ventes.aggregate(
        total=Sum("total_amount")
    )["total"]
    context = {
        "ventes": ventes,
        "total_ventes": total_ventes,
        "total_montant": total_montant,
        "today": today
    }
    return render(request, "rapport_journalier.html",context)


def rapport_hebdomadaire(request):
    today = timezone.now().date()
    start_week = today - timedelta(days=today.weekday())
    end_week = start_week + timedelta(days=6)
    ventes = Sale.objects.filter(
        created_at__date__range=[start_week, end_week],
        status='completed'
    )
    total_ventes = ventes.count()
    total_montant = ventes.aggregate(
        total=Sum("total_amount")
    )["total"]
    context = {
        "ventes": ventes,
        "total_ventes": total_ventes,
        "total_montant": total_montant,
        "start_week": start_week,
        "end_week": end_week
    }
    return render(request, "rapport_hebdomadaire.html",context)


def rapport_mensuel(request):
    today = timezone.now()
    ventes = Sale.objects.filter(
        created_at__year=today.year,
        created_at__month=today.month,
        status='completed'
    )
    total_ventes = ventes.count()
    total_montant = ventes.aggregate(
        total=Sum("total_amount")
    )["total"]
    context = {
        "ventes": ventes,
        "total_ventes": total_ventes,
        "total_montant": total_montant
    }
    return render(request, "rapport_mensuel.html",context)

#Not implemneted
def produits_plus_vendus(request):

    produits = SaleItem.objects.values(
        "product__name"
    ).annotate(
        total_vendu=Sum("quantity")
    ).order_by("-total_vendu")[:10]

    return render(request, "reports/produits.html", {"produits": produits})

#Not implemnted
def rapport_par_caissier(request):

    rapport = Sale.objects.values(
        "register__name",
    ).annotate(
        nombre_ventes=Count("id"),
        total_montant=Sum("total_amount")
    ).order_by("-total_montant")

    return render(request, "reports/par_caissier.html", {"rapport": rapport})


def rapport_caissier_journalier(request):
    today = timezone.now().date()
    rapport = Sale.objects.filter(
        created_at__date=today
    ).values(
        "register__name"
    ).annotate(
        nombre_ventes=Count("id"),
        montant_total=Sum("total_amount"),
        articles_vendus=Sum("items__quantity")
    ).filter(status='completed').order_by("-montant_total")
    context = {
        "rapport": rapport,
        "today": today
    }
    return render(request, "rapport_caissier_journalier.html", context)

def rapport_caissier_hebdomadaire(request):
    today = timezone.now().date()
    start_week = today - timedelta(days=today.weekday())
    end_week = start_week + timedelta(days=6)
    rapport = Sale.objects.filter(
        created_at__date__range=[start_week, end_week]
    ).values(
        "register__name"
    ).annotate(
        nombre_ventes=Count("id"),
        montant_total=Sum("total_amount"),
        articles_vendus=Sum("items__quantity")
    ).filter(status='completed').order_by("-montant_total")
    context = {
        "rapport": rapport,
        "start_week": start_week,
        "end_week": end_week
    }
    return render(request,"rapport_caissier_hebdomadaire.html", context)


def rapport_caissier_mensuel(request):
    today = timezone.now()
    rapport = Sale.objects.filter(
        created_at__year=today.year,
        created_at__month=today.month
    ).values(
        "register__name"
    ).annotate(
        nombre_ventes=Count("id"),
        montant_total=Sum("total_amount"),
        articles_vendus=Sum("items__quantity")
    ).filter(status='completed').order_by("-montant_total")
    context = {
        "rapport": rapport,
        "month": today.month,
        "year": today.year
    }
    return render(request, "rapport_caissier_mensuel.html", context)


def produits_plus_vendus(request):
    total = ExpressionWrapper(
        F("quantity") * F("selling_price"),
        output_field=DecimalField()
    )
    produits = SaleItem.objects.values(
        "product__name"
    ).annotate(
        quantite_vendue=Sum("quantity"),
        nombre_ventes=Count("sale"),
        montant_total=Sum(total)
    ).order_by("-quantite_vendue")[:20]

    context = {
        "produits": produits
    }
    return render(request, "produits_plus_vendus.html", context)

def produits_rupture_stock(request):
    produits = Product.objects.all()
    produits_rupture = [
        p for p in produits if p.current_stock <= 5
    ]
    context = {
        "produits": produits_rupture
    }
    return render(request, "produits_rupture_stock.html", context)


def financial_report(request):
    total_sales = Sale.objects.aggregate(
        total=Sum("total_amount")
    )["total"] or 0
    cost_of_goods = SaleItem.objects.aggregate(
        total=Sum(F("purchase_price") * F("quantity"))
    )["total"] or 0
    profit = SaleItem.objects.aggregate(
        total=Sum(
            (F("selling_price") - F("purchase_price")) * F("quantity")
        )
    )["total"] or 0
    context = {
        "total_sales": total_sales,
        "cost_of_goods": cost_of_goods,
        "profit": profit,
    }
    return render(request, "financial_report.html", context)