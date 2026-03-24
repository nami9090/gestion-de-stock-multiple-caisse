#Django Modules
from django.shortcuts import render
from django.template import loader
from django.http import HttpRequest
from django.db.models import Sum, Count, F, DecimalField, ExpressionWrapper
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum
import datetime

#Account app modules
from account.decorators import role_required
#Product app modules
from product.models import Product, Supplier
#Stock app modules
from stock.models import StockEntry, StockExit
#Sale app modules
from sale.models import Sale, SaleItem

# Create your views here.
@login_required
@role_required('Admin','Caisse', 'Gestionnaire_stock')
def admin_dashboard(request):
    group = request.user.groups.first()
    title = "Dashboard"
    if group:
        if group.name == "Admin":
            title = "Admin Dashboard"
        elif group.name == "Caisse":
            title = "Caisse Dashboard"
        elif group.name == "Gestionnaire_stock":
            title = "Gestionnaire Dashboard"
        else:
            return title
    else:
        return title
    today = timezone.now()
    six_months_ago = today - datetime.timedelta(days=180)
    # -------------------------
    # Statistiques clés
    # -------------------------
    total_products = Product.objects.count()
    total_stock = StockEntry.objects.aggregate(total=Sum('quantity'))['total'] or 0
    total_sales = Sale.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    total_suppliers = Supplier.objects.count()
    # -------------------------
    # Inbound: Entrées de stock
    # -------------------------
    inbound_last_6_months = StockEntry.objects.filter(date__gte=six_months_ago)
    # Préparer les données pour Chart.js
    inbound_per_month = {}
    for i in range(6):
        month = (today - datetime.timedelta(days=i*30)).strftime("%b %Y")
        total = inbound_last_6_months.filter(date__month=(today - datetime.timedelta(days=i*30)).month)\
                                     .aggregate(total=Sum('quantity'))['total'] or 0
        inbound_per_month[month] = total
    inbound_current = list(inbound_per_month.values())[0]  # dernier mois
    inbound_average = sum(inbound_per_month.values()) / 6
    inbound_maximum = max(inbound_per_month.values())
    # -------------------------
    # Outbound: Ventes ou sorties
    # -------------------------
    outbound_last_6_months = Sale.objects.filter(created_at__gte=six_months_ago)
    outbound_per_month = {}
    for i in range(6):
        month = (today - datetime.timedelta(days=i*30)).strftime("%b %Y")
        total = outbound_last_6_months.filter(created_at__month=(today - datetime.timedelta(days=i*30)).month)\
                                      .aggregate(total=Sum('total_amount'))['total'] or 0
        outbound_per_month[month] = total
    outbound_current = list(outbound_per_month.values())[0]  # dernier mois
    outbound_average = sum(outbound_per_month.values()) / 6
    outbound_maximum = max(outbound_per_month.values())
    # Representation en terme de pourcentage
    # Inbound stats en %
    inbound_current_pct = (inbound_current / inbound_maximum * 100) if inbound_maximum else 0
    inbound_average_pct = (inbound_average / inbound_maximum * 100) if inbound_maximum else 0
    inbound_maximum_pct = 100  # par définition
    # Outbound stats en %
    outbound_current_pct = (outbound_current / outbound_maximum * 100) if outbound_maximum else 0
    outbound_average_pct = (outbound_average / outbound_maximum * 100) if outbound_maximum else 0
    outbound_maximum_pct = 100
    # -------------------------
    # Préparer le graphique des ventes (line chart)
    # -------------------------
    sales_data_labels = list(outbound_per_month.keys())[::-1]
    sales_data_values = list(outbound_per_month.values())[::-1]
    #Rapport du finance
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
    #------------------------------------------
    # Vente et revenu par jour
    #------------------------------------------
    today_date = timezone.now().date()
    ventes_jour = Sale.objects.filter(created_at__date=today_date).count()
    revenu_jour = Sale.objects.filter(
        created_at__date=today_date
    ).aggregate(total=Sum("total_amount"))["total"]
    context = {
        'total_products': total_products,
        'total_stock': total_stock,
        # 'total_sales': total_sales,
        'total_suppliers': total_suppliers,
        # Inbound stats
        'inbound_current_pct': inbound_current_pct,
        'inbound_average_pct': inbound_average_pct,
        'inbound_maximum_pct': inbound_maximum_pct,
        # Outbound stats
        'outbound_current_pct': outbound_current_pct,
        'outbound_average_pct': outbound_average_pct,
        'outbound_maximum_pct': outbound_maximum_pct,
        # Chart.js data
        'sales_data_labels': sales_data_labels,
        'sales_data_values': sales_data_values,
        'title':title,
        #Rapport financier
        "total_sales": total_sales,
        "cost_of_goods": cost_of_goods,
        "profit": profit,
        #Ventes et revenus par jour
        "ventes_jour":ventes_jour,
        "revenu_jour":revenu_jour,

    }
    return render(request, 'dashboard.html', context)

def dashboard_reports(request):
    today = timezone.now().date()
    ventes_jour = Sale.objects.filter(created_at__date=today).count()
    revenu_jour = Sale.objects.filter(
        created_at__date=today
    ).aggregate(total=Sum("total_amount"))["total"]
    produits = Product.objects.count()
    context = {
        "ventes_jour": ventes_jour,
        "revenu_jour": revenu_jour,
        "produits": produits
    }
    return render(request, "reports/dashboard.html", context)