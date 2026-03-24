from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
#Product app modules
from product.models import Product, CategoryProduct, Supplier
from product.forms import ProductForm, CategoryForm, SupplierForm
#Product app modules
from stock.forms import StockEntryForm, StockExitForm
from stock.models import StockEntry, StockExit
#Account app modules
from account.forms import UserCreateForm
from account.decorators import role_required
#Sale app modules
from sale.models import Sale, SaleItem
from sale.forms import SaleForm, SaleItemForm
#Finance app modules
from finance.models import Cashier, CashOperation, CashRegister
from finance.forms import AssignCashierForm, CashOperationForm, CashRegisterForm, CashierForm
#Company app modules
from companie.models import Company
#ReportLab modules
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
)
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from reportlab.platypus import HRFlowable
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from reportlab.platypus import KeepTogether
from io import BytesIO
from datetime import datetime
from decimal import Decimal
from reportlab.platypus import ListFlowable, ListItem

# Create your views here.
@login_required
def home(request):
    template = loader.get_template('index.html')

    context = {

    }
    return HttpResponse(template.render(context, request))

@login_required
@role_required("Admin","Gestionnaire_stock")
def product_list(request):
    template = loader.get_template('list_produit.html')
    products = Product.objects.all().order_by('-created_at')
    context = {
        'products':products
    }
    return HttpResponse(template.render(context, request))

# =========================
    # STORE MANAGEMENT
# =========================
@login_required
@role_required("Admin","Gestionnaire_stock")
def stock_list(request):
    template = loader.get_template('stock/list.html')
    group = request.user.groups.first()
    if group:
        if group.name == "Admin":
            stocks = StockEntry.objects.select_related('product', 'supplier', 'entered_by').order_by('-date')
        elif group.name == "Gestionnaire_stock":
            stocks = StockEntry.objects.select_related(
                'product', 'supplier', 'entered_by').filter(entered_by=request.user).order_by('-date')
    context = {
        'stocks':stocks
    }
    return HttpResponse(template.render(context, request))

@login_required
@role_required("Admin","Gestionnaire_stock")
def stock_entry_list(request):
    template = loader.get_template('stock/entry_list.html')
    entries = StockEntry.objects.all().order_by('-date')
    context = {
        'entries':entries
    }
    return HttpResponse(template.render(context, request))

@login_required
@role_required("Admin","Gestionnaire_stock")
def stock_entry_create(request):
    template = loader.get_template('stock/entry_form.html')
    if request.method == "POST":
        form = StockEntryForm(request.POST)

        if form.is_valid():
            entry = form.save(commit=False)
            entry.entered_by = request.user
            entry.save()
            messages.success(request, "Entrée de stock enregistrée.")
            return redirect('stock_entry_list')
    else:
        form = StockEntryForm()
    context = {
        'form':form
    }
    return HttpResponse(template.render(context, request))

@login_required
@role_required("Admin","Gestionnaire_stock")
def stock_exit_list(request):
    template = loader.get_template('stock/exit_list.html')
    exits = StockExit.objects.all().order_by('-date')
    context = {
        'exits':exits
    }
    return HttpResponse(template.render(context, request))

@login_required
@role_required("Admin","Gestionnaire_stock")
def stock_exit_create(request):
    template = loader.get_template('stock/exit_form.html')
    if request.method == "POST":
        form = StockExitForm(request.POST)
        if form.is_valid():
            exit = form.save(commit=False)
            exit.performed_by = request.user
            try:
                exit.save()
                messages.success(request, "Sortie de stock effectuée.")
                return redirect('stock_exit_list')
            except Exception as e:
                messages.error(request, str(e))
    else:
        form = StockExitForm()
    context = {
        'form':form
    }
    return HttpResponse(template.render(context, request))

# ================================
    # PRODUCT CATEGORY MANAGEMENT
# ================================
@login_required
@role_required("Admin","Gestionnaire_stock")
def category_list(request):
    template = loader.get_template('category/list.html')
    categories = CategoryProduct.objects.all().order_by('name')
    context = {
        'categories':categories
    }
    return HttpResponse(template.render(context, request))

@login_required
@role_required("Admin","Gestionnaire_stock")
def category_create(request):
    template = loader.get_template('category/form.html')
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('category_list')
    context = {
        'form':form,
        'title':'Ajouter Categorie de produit'
    }
    return HttpResponse(template.render(context, request))

@login_required
@role_required("Admin","Gestionnaire_stock")
def category_update(request, pk):
    template = loader.get_template('category/form.html')
    categorie = get_object_or_404(CategoryProduct, pk=pk)
    form = CategoryForm(request.POST or None, instance=categorie)
    if form.is_valid():
        form.save()
        return redirect('category_list')
    context = {
        'form':form,
        'title':'Mettre a jour Categorie de produit'
    }
    return HttpResponse(template.render(context, request))

@login_required
@role_required("Admin","Gestionnaire_stock")
def category_delete(request, pk):
    template = loader.get_template('category/confirm_delete.html')
    categorie = get_object_or_404(CategoryProduct, pk=pk)
    if request.method == 'POST':
        categorie.delete()
        return redirect('category_list')
    context = {
        'category':categorie
    }
    return HttpResponse(template.render(context, request))

# =========================
    # SUPPLIER MANAGEMENT
# =========================
@login_required
@role_required("Admin","Gestionnaire_stock")
def supplier_list(request):
    template = loader.get_template('supplier/list.html')
    suppliers = Supplier.objects.all()
    context = {
        'suppliers':suppliers
    }
    return HttpResponse(template.render(context, request))

@login_required
@role_required("Admin","Gestionnaire_stock")
def supplier_create(request):
    template = loader.get_template('supplier/form.html')
    form = SupplierForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Fournisseur ajouté avec succès")
        return redirect('supplier_list')
    context = {
        'form':form,
        'title':'Ajouter fournisseur'
    }
    return HttpResponse(template.render(context, request))

@login_required
@role_required("Admin","Gestionnaire_stock")
def supplier_update(request, pk):
    template = loader.get_template('supplier/form.html')
    supplier = get_object_or_404(Supplier, pk=pk)
    form = SupplierForm(request.POST or None, instance=supplier)
    if form.is_valid():
        form.save()
        messages.success(request, "Fournisseur modifié avec succès")
        return redirect('supplier_list')
    context = {
        'form':form,
        'title':'Modifier fournisseur'
    }
    return HttpResponse(template.render(context, request))

@login_required
@role_required("Admin")
def supplier_delete(request, pk):
    template = loader.get_template('supplier/confirm_delete.html')
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        supplier.delete()
        messages.success(request, "Fournisseur supprimé avec succès")
        return redirect('supplier_list')
    context = {
        'supplier':supplier
    }
    return HttpResponse(template.render(context, request))

# =========================
    # PRODUCT MANAGEMENT
# =========================
@login_required
@role_required("Admin", "Gestionnaire_stock")
def product_list_prod(request):
    template = loader.get_template('product/list.html')
    products = Product.objects.all().order_by('-created_at')
    context = {
        'products':products
    }
    return HttpResponse(template.render(context, request))

@login_required
@role_required("Admin","Gestionnaire_stock")
def product_create(request):
    template = loader.get_template('product/form.html')
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Produit ajouté avec succès")
            return redirect('product_list_prod')
    else:
        form = ProductForm()
    context = {
        'form':form,
        'title': 'Ajouter un produit'
    }
    return HttpResponse(template.render(context, request))

@login_required
@role_required("Admin","Gestionnaire_stock")
def product_update(request, pk):
    template = loader.get_template('product/form.html')
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Produit modifié avec succès")
            return redirect('product_list_prod')
    else:
        form = ProductForm(instance=product)
    context = {
        'form': form,
        'title': 'Modifier le produit'
    }
    return HttpResponse(template.render(context, request))

@login_required
@role_required("Admin","Gestionnaire_stock")
def product_detail(request, pk):
    template = loader.get_template('product/detail.html')
    product = get_object_or_404(Product, pk=pk)
    context = {
        'product':product
    }
    return HttpResponse(template.render(context, request))

@login_required
@role_required("Admin","Gestionnaire_stock")
def product_delete(request, pk):
    template = loader.get_template('product/confirm_delete.html')
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        product.delete()
        messages.success(request, "Produit supprimé avec succès")
        return redirect('product_list_prod')
    context = {
        'product': product
    }
    return HttpResponse(template.render(context, request))

# =========================
    # SALE MANAGEMENT
# =========================
@login_required
@role_required("Admin","Caisse")
def sale_list(request):
    template = loader.get_template('sale/list.html')
    cashier = get_object_or_404(Cashier, user=request.user)
    group = request.user.groups.first()
    title = "Vente | Liste|"
    if group:
        if group.name == "Admin":
            title = "Vente | Liste | Admin"
            sales = Sale.objects.filter(status='completed').order_by('-created_at')
        elif group.name == "Caisse":
            title = "Vente | Liste | Caisse"
            sales = Sale.objects.filter(cashier=cashier,status='completed').order_by('-created_at')
        else:
            return title
    else:
        return title
    # Afficher toutes les ventes si admin, sinon seulement celles du caissier
    # if request.user.is_staff:
    #     sales = Sale.objects.filter(
    #         status='completed'
    #     ).order_by('-created_at')
    # else:
    #     sales = Sale.objects.filter(
    #         cashier=cashier,
    #         status='completed'
    #     ).order_by('-created_at')
    context = {
        'sales':sales,
        'title':title,
    }
    return HttpResponse(template.render(context, request))

@login_required
@role_required("Admin","Caisse")
def sale_invoice(request, sale_id):
    template = loader.get_template('sale/invoice.html')
    sale = get_object_or_404(Sale, id=sale_id)
    context = {
        "sale": sale
    }
    return HttpResponse(template.render(context, request))

@login_required
@role_required("Admin")
def sale_create(request):
    template = loader.get_template('sale/create.html')
    # Récupérer ou créer vente en session
    # shop = ShopSettings.objects.first()
    shop = 'FB'
    #Récupérer ou créer le caissier
    cashier, _ = Cashier.objects.get_or_create(user=request.user)
    #Récupérer ou créer la vente en session
    cashier = Cashier.objects.filter(user=request.user).first()
    #Si cashier n'esxite pas
    if not cashier:
        messages.warning(request, "Vous n'êtes pas enregistré comme caissier.")
        return redirect('sale_list')
    #Si cashier désactivé
    if not cashier.is_active:
        messages.warning(request, "Votre compte caissier est désactivé.")
        return redirect('sale_list')
    sale_id = request.session.get('sale_id')
    if sale_id:
        try:
            sale = Sale.objects.get(id=sale_id, status='draft')
        except Sale.DoesNotExist:
            sale = Sale.objects.create(
                cashier=cashier,
                status='draft'
            )
            request.session['sale_id'] = sale.id
    else:
        sale = Sale.objects.create(
            cashier=cashier,
            status='draft'
        )
        request.session['sale_id'] = sale.id

    sale_form = SaleForm(instance=sale)
    form = SaleItemForm()

    # Ajouter produit à la vente
    if request.method == "POST":

        # Mise à jour infos client
        sale_form = SaleForm(request.POST, instance=sale)
        if sale_form.is_valid():
            sale_form.save()
        # Formulaire produit
        form = SaleItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.sale = sale
            # Remplir automatiquement les prix
            item.selling_price = item.product.selling_price
            item.purchase_price = item.product.purchase_price
            # Vérification stock
            if item.quantity > item.product.current_stock:
                messages.warning(request, "Stock insuffisant.")
            else:
                item.save()
                messages.success(request, "Produit ajouté à la vente.")
                return redirect('sale_create')
    items = sale.items.all()
    context = {
        'sale': sale,
        'items': items,
        'sale_form': sale_form,
        'form': form,
        'shop': shop,
        'cashier': cashier, 
    }
    return HttpResponse(template.render(context, request))

@login_required
@role_required("Admin")
@transaction.atomic
def sale_finalize(request):
    sale_id = request.session.get('sale_id')
    if not sale_id:
        return redirect('sale_create')
    sale = get_object_or_404(Sale, id=sale_id)
    #Sécurité : vérifier propriétaire
    if not request.user.is_staff and sale.cashier.user != request.user:
        messages.error(request, "Action non autorisée.")
        return redirect('sale_list')
    #Vérifier si déjà finalisée
    if sale.status == 'completed':
        messages.warning(request, "Cette vente est déjà finalisée.")
        return redirect('sale_list')
    #Finaliser
    sale.status = 'completed'
    sale.save()
    #Créer opération caisse proprement
    CashOperation.objects.create(
        cashier=sale.cashier,
        operation_type='SALE',
        amount=sale.total_amount,
        description=f"Vente #{sale.id}"
    )
    #Supprimer session
    request.session.pop('sale_id', None)
    messages.success(request, "Vente finalisée avec succès.")
    return redirect('sale_list')

@login_required
@role_required("Admin")
def update_sale(request, sale_id):
    template = loader.get_template('sale/update.html')
    sale = get_object_or_404(Sale, id=sale_id, status='completed')
    sale_form = SaleForm(request.POST or None, instance=sale)
    # Pour simplifier, on met à jour le premier item seulement (tu peux adapter pour plusieurs items)
    first_item = sale.items.first()
    item_form = SaleItemForm(request.POST or None, instance=first_item)
    if request.method == "POST":
        if sale_form.is_valid() and item_form.is_valid():
            sale_form.save()
            item_form.save()
            sale.calculate_totals()  # recalculer total, TVA
            messages.success(request, "Vente actualisée avec succès.")
            # Mettre à jour l'entrée caisse correspondante
            cash_op = CashOperation.objects.filter(operation_type='SALE', description=f"Vente #{sale.id}").first()
            if cash_op:
                cash_op.amount = sale.total_amount
                cash_op.save()
            return redirect('sale_list')
    context = {
        "sale_form": sale_form, 
        "item_form": item_form
    }
    return HttpResponse(template.render(context, request))

@login_required
@role_required("Admin")
def delete_sale(request, sale_id):
    template = loader.get_template('sale/confirm_delete.html')
    sale = get_object_or_404(Sale, id=sale_id, status='completed')
    if request.method == "POST":
        # Supprimer les items (et donc remettre le stock à jour si nécessaire)
        for item in sale.items.all():
            from stock.models import StockExit, StockEntry
            # Optionnel : remettre la quantité en stock
            StockEntry.objects.create(
                product=item.product,
                supplier=None,
                quantity=item.quantity,
                remaining_quantity=item.quantity,
                unit_cost=item.product.purchase_price if hasattr(item.product, "purchase_price") else 0,
                total_cost=(item.quantity * item.product.purchase_price) if hasattr(item.product, "purchase_price") else 0,
                entered_by=request.user,
                reason=f"Annulation vente #{sale.id}"
            )
            # Supprimer la sortie stock existante
            StockExit.objects.filter(product=item.product, reason=f"Vente #{sale.id}").delete()
            messages.success(request, "Annulation vente avec succès.")
        # Supprimer l'entrée caisse
        CashOperation.objects.filter(operation_type='SALE', description=f"Vente #{sale.id}").delete()
        sale.delete()
        return redirect('sale_list')
    context = {
        'sale':sale
    }
    return HttpResponse(template.render(context, request))

@login_required
@role_required("Admin","Caisse")
def sale_detail(request, pk):
    template = loader.get_template('sale/detail.html')
    sale = get_object_or_404(Sale, pk=pk, status="completed")
    items = sale.items.all()
    context = {
        'sale':sale,
        'items':items,
    }
    return HttpResponse(template.render(context, request))

@login_required
@role_required("Admin","Caisse")
def sale_invoice(request, pk):
    sale = get_object_or_404(Sale, id=pk, status="completed")
    shop = Company.objects.first()
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    right_style = ParagraphStyle(
        name="RightAlign",
        parent=styles["Normal"],
        alignment=TA_RIGHT
    )
    # =========================
    # HEADER
    # =========================
    if shop.logo:
        elements.append(Image(shop.logo.path, width=1.5*inch, height=1.5*inch))
    elements.append(Paragraph(f"<b>{shop.name}</b>" or "" , styles["Heading1"]))
    elements.append(Paragraph(shop.address or "", styles["Normal"]))
    elements.append(Paragraph(f"Tél: {shop.phone}" or "" , styles["Normal"]))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
    elements.append(Spacer(1, 15))
    # =========================
    # INFO CLIENT + FACTURE
    # =========================
    invoice_number = f"FACT-{sale.id:05d}"
    date_now = sale.created_at.strftime("%d/%m/%Y")
    info_data = [[
        Paragraph(
            f"<b>Client :</b><br/>{sale.client_name}<br/>{sale.client_phone}",
            styles["Normal"]
        ),
        Paragraph(
            f"<b>Facture N° :</b> {invoice_number}<br/><b>Date :</b> {date_now}",
            right_style
        )
    ]]
    info_table = Table(info_data, colWidths=[3.5*inch, 2.5*inch])
    elements.append(info_table)
    elements.append(Spacer(1, 20))
    # =========================
    # TABLE PRODUITS
    # =========================
    data = [["Produit", "Qté", "Prix U.", "Total"]]
    total_general = Decimal("0.00")
    for item in sale.items.all():
        total = item.quantity * item.selling_price
        total_general += total
        data.append([
            item.product.name,
            str(item.quantity),
            f"{item.selling_price:,.0f} {shop.currency}",
            f"{total:,.0f} {shop.currency}",
        ])
    table = Table(data, colWidths=[2.5*inch, 1*inch, 1.2*inch, 1.2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))
    # =========================
    # TOTALS
    # =========================
    tva_rate = Decimal(shop.tva if shop.tva else 0)
    tva = total_general * (tva_rate / Decimal("100"))
    grand_total = total_general + tva
    totals_data = [
        ["Sous-total :", f"{total_general:,.0f} {shop.currency}"],
        [f"TVA ({tva_rate}%) :", f"{tva:,.0f} {shop.currency}"],
        ["TOTAL :", f"{grand_total:,.0f} {shop.currency}"],
    ]
    totals_table = Table(totals_data, colWidths=[3.7*inch, 1.5*inch])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('LINEABOVE', (0, 2), (-1, 2), 1, colors.black),
    ]))
    elements.append(totals_table)
    elements.append(Spacer(1, 30))
    # =========================
    # FOOTER
    # =========================
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("Merci pour votre confiance :)", styles["Normal"]))
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="facture_{sale.id}.pdf"'
    response.write(pdf)

    return response

# =========================
    # SALE MULTI MANAGEMENT
# =========================
@login_required
@role_required("Admin","Caisse")
def sale_create_caisse_multi(request):
    template = loader.get_template('sale/create_caisse_multi.html')
    #Vérifier caissier actif

    register = CashRegister.objects.filter(
        is_active=True,
        # cashiers__user=request.user
        cashiers__user__groups__name__in=["Admin","Caisse"]
    ).first()

    if not register:
        messages.warning(request, "Aucune caisse ouverte assignée.")
        return redirect("sale_list")

    cashier = Cashier.objects.filter(user=request.user, is_active=True).first()
    if not cashier:
        messages.warning(request, "Votre compte caissier est désactivé.")
        return redirect('sale_list')

    #Vérifier caisse active du caissier
    # cash_register = cashier.cash_registers.filter(is_active=True).first()
    cash_register = CashRegister.objects.filter(is_active=True,cashiers__user__groups__name__in=["Admin", "Caisse"]).first()
    if not cash_register:
        messages.warning(request, "Vous n'avez pas de caisse ouverte.")
        return redirect('sale_list')
    
    if not cash_register:
        messages.warning(request, "Aucune caisse ouverte.")
        return redirect('sale_list')

    # Récupérer ou créer vente en session
    sale_id = request.session.get('sale_id')
    if sale_id:
        sale = Sale.objects.filter(id=sale_id, status='draft').first()
        if not sale:
            sale = Sale.objects.create(register=register, cashier=cashier, status='draft')
            request.session['sale_id'] = sale.id
    else:
        sale = Sale.objects.create(register=register, cashier=cashier, status='draft')
        request.session['sale_id'] = sale.id

    sale_form = SaleForm(instance=sale)
    form = SaleItemForm()

    # Ajouter un produit
    if request.method == "POST":
        sale_form = SaleForm(request.POST, instance=sale)
        if sale_form.is_valid():
            sale = sale_form.save(commit=False)
            sale.cashier = cashier
            sale.save()

        form = SaleItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.sale = sale
            item.selling_price = item.product.selling_price
            item.purchase_price = item.product.purchase_price

            # Vérification stock
            if item.quantity > item.product.current_stock:
                messages.warning(request, f"Stock insuffisant pour {item.product.name}.")
            else:
                item.save()
                messages.success(request, f"{item.product.name} ajouté à la vente.")
                return redirect('sale_create_caisse_multi')

    items = sale.items.all()
    shop = Company.objects.first()
    context = {
        'sale': sale,
        'items': items,
        'sale_form': sale_form,
        'form': form,
        'shop': shop,
        'cash_register': cash_register,
        'cashier': cashier
    }
    return HttpResponse(template.render(context, request))

@login_required
@role_required("Admin","Caisse")
@transaction.atomic
def sale_finalize_caisse_multi(request):
    sale_id = request.session.get('sale_id')
    if not sale_id:
        return redirect('sale_create_caisse_multi')
    sale = get_object_or_404(Sale, id=sale_id, status='draft')
    # Vérifier caissier et caisse
    cashier = sale.cashier
    if not cashier.is_active:
        messages.error(request, "Votre compte caissier est désactivé.")
        return redirect('dashboard:admin_dashboard')
    cash_register = cashier.cash_registers.filter(is_active=True).first()
    if not cash_register:
        messages.error(request, "Vous n'avez pas de caisse ouverte.")
        return redirect('dashboard:admin_dashboard')
    #Vérifier si déjà finalisée
    if sale.status == 'completed':
        messages.warning(request, "Cette vente est déjà finalisée.")
        return redirect('sale_list')
    if not sale.validated_by_admin:
        messages.warning(request, "Cette vente doit être validée par l'administrateur avant de pouvoir la finaliser.")
        return redirect('sale_create_caisse_multi')
    # Finaliser
    sale.status = 'completed'
    sale.save()
    # Créer opération de caisse
    CashOperation.objects.create(
        cashier=cashier,
        cash_register=cash_register,
        operation_type='SALE',
        amount=sale.total_amount,
        description=f"Vente #{sale.id}"
    )
    # Supprimer session
    request.session.pop('sale_id', None)
    messages.success(request, "Vente finalisée avec succès.")
    return redirect('sale_list')

# =========================
    # USER MANAGEMENT
# =========================
@login_required
@role_required("Admin")
def user_management(request):
    template = loader.get_template('user_management.html')

    utilisateurs = User.objects.all().order_by('username')

    user_pagination = Paginator(utilisateurs, 10)
    pages_user = request.GET.get('pages_user')
    user_pages = user_pagination.get_page(pages_user)

    context = {
        'users':user_pages
    }
    return HttpResponse(template.render(context, request))

@login_required
@role_required("Admin")
def create_user(request):
    template = loader.get_template('user_form.html')
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"L'utilisateur {user.username} a été créé avec succès !")
            redirect('user_management')
        else:
            messages.error(request, "Erreur : le formulaire est invalide.")
    else:
        form = UserCreateForm()
        redirect('user_management')
    context = {
        'form':form
    }
    return HttpResponse(template.render(context, request))

# =========================
    # CASHIER MANAGEMENT
# =========================
@login_required
@role_required("Admin")
def cashier_list(request):
    template = loader.get_template('cashier/list.html')
    cashiers = Cashier.objects.all()
    context = {
        'cashiers':cashiers
    }
    return HttpResponse(template.render(context, request))

@login_required
@role_required("Admin")
def cashier_create(request):
    template = loader.get_template('cashier/form.html')
    if request.method == "POST":
        form = CashierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Caissier ajouté avec succès.")
            return redirect("cashier_list")
    else:
        form = CashierForm()
    context = {
        'form':form,
        'title':'Creer un(e) caissier(e)'
    }
    return HttpResponse(template.render(context, request))

@login_required
@role_required("Admin")
def cashier_update(request, pk):
    template = loader.get_template('cashier/form.html')
    cashier = get_object_or_404(Cashier, pk=pk)
    if request.method == 'POST':
        form = CashierForm(request.POST, instance=cashier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Caissier modifié avec succès')
            return redirect('cashier_list')
    else:
        form = CashierForm(instance=cashier)
    context = {
        'form':form,
        'title':'Modifier un(e) caissier(e)'
    }
    return HttpResponse(template.render(context, request))

@login_required
@role_required("Admin")
def cashier_delete(request, pk):
    template = loader.get_template('cashier/confirm_delete.html')
    cashier = get_object_or_404(Cashier, pk=pk)
    if request.method == 'POST':
        cashier.delete()
        messages.success(request, 'Caissier supprimé avec succès')
    context = {
       'cashier':cashier 
    }
    return HttpResponse(template.render(context, request))

# =========================
    # VIRUAL CASHIER MANAGEMENT
# =========================
@login_required
@role_required("Admin")
def cash_register_list(request):
    template = loader.get_template('cashier/register_list.html')
    """Liste toutes les caisses de la boutique"""
    shop = Company.objects.first()  # ou récupère ta boutique actuelle
    cash_registers = CashRegister.objects.filter(shop=shop).order_by('-created_at')
    context = {
        'cash_registers':cash_registers
    }
    return HttpResponse(template.render(context, request))

@login_required
@role_required("Admin")
def cash_register_open(request, pk):
    template = loader.get_template('cashier/register_open.html')
    """Ouvre une caisse"""
    caisse = get_object_or_404(CashRegister, pk=pk)

    if caisse.is_active:
        messages.warning(request, f"{caisse.name} est déjà ouverte.")
    else:
        caisse.is_active = True
        caisse.save()
        messages.success(request, f"{caisse.name} est maintenant ouverte.")
    return redirect('cash_register_list')

@login_required
@role_required("Admin")
def cash_register_close(request, pk):
    """Ferme une caisse"""
    caisse = get_object_or_404(CashRegister, pk=pk)

    if not caisse.is_active:
        messages.warning(request, f"{caisse.name} est déjà fermée.")
    else:
        caisse.is_active = False
        caisse.save()
        messages.success(request, f"{caisse.name} est maintenant fermée.")
    return redirect('cash_register_list')

@login_required
@role_required("Admin")
def cash_register_manage(request):
    template = loader.get_template('cashier/cash_register_manage.html')
    shop = Company.objects.first()
    cash_registers = CashRegister.objects.filter(shop=shop)

    create_form = CashRegisterForm()
    assign_form = AssignCashierForm()

    #Création nouvelle caisse
    if request.method == "POST" and "create_cash_register" in request.POST:
        create_form = CashRegisterForm(request.POST)
        if create_form.is_valid():
            caisse = create_form.save(commit=False)
            caisse.shop = shop
            caisse.is_active = False
            caisse.save()
            messages.success(request, "Nouvelle caisse créée avec succès.")
            return redirect('cash_register_manage')

    #Assignation caissier
    if request.method == "POST" and "assign_cashier" in request.POST:
        caisse_id = request.POST.get("caisse_id")
        caisse = get_object_or_404(CashRegister, id=caisse_id)

        assign_form = AssignCashierForm(request.POST)
        if assign_form.is_valid():
            cashier = assign_form.cleaned_data["cashier"]
            cashier.cash_registers.add(caisse)
            messages.success(request, f"{cashier} assigné à {caisse.name}.")
            return redirect('cash_register_manage')

    context = {
        "cash_registers": cash_registers,
        "create_form": create_form,
        "assign_form": assign_form,
    }
    return HttpResponse(template.render(context, request))

@login_required
@role_required("Admin")
def toggle_cash_register(request, pk):
    caisse = get_object_or_404(CashRegister, pk=pk)

    caisse.is_active = not caisse.is_active
    caisse.save()

    if caisse.is_active:
        messages.success(request, f"{caisse.name} est maintenant ouverte.")
    else:
        messages.warning(request, f"{caisse.name} est maintenant fermée.")

    return redirect('cash_register_manage')

@login_required
@role_required("Admin","Caisse")
def cashoperation_list(request):
    template = loader.get_template('cashier/operation_caisse.html')

    group = request.user.groups.first()
    if group:
        if group.name == "Admin":
            operations = CashOperation.objects.select_related(
                "cashier",
                "cash_register"
            ).order_by("-created_at")
        elif group.name == "Caisse":
            operations = CashOperation.objects.select_related(
                "cashier",
                "cash_register"
            ).filter(cashier__user=request.user).order_by("-created_at")

    context = {
        'operations':operations
    }
    return HttpResponse(template.render(context, request))

@login_required
@role_required("Admin","Caisse")
def cashoperation_create(request):
    template = loader.get_template('cashier/cashoperation_form.html')
    #Vérifier caissier actif
    cashier = Cashier.objects.filter(
        user=request.user,
        is_active=True
    ).first()

    if not cashier:
        messages.warning(request, "Compte caissier invalide.")
        return redirect("cash_register_list")

    #Vérifier caisse ouverte
    cash_register = cashier.cash_registers.filter(
        is_active=True
    ).first()

    if not cash_register:
        messages.warning(request, "Aucune caisse ouverte.")
        return redirect("cash_register_list")

    form = CashOperationForm()

    if request.method == "POST":
        form = CashOperationForm(request.POST)
        if form.is_valid():
            operation = form.save(commit=False)

            #On force les relations
            operation.cashier = cashier
            operation.cash_register = cash_register

            operation.save()

            messages.success(request, "Opération enregistrée avec succès.")
            return redirect("cashoperation_list")
    context = {
        "form": form,
        "cash_register": cash_register
    }
    return HttpResponse(template.render(context, request))

@login_required
@role_required("Admin","Caisse")
def cashoperation_detail(request, pk):
    template = loader.get_template('cashier/cashoperation_detail.html')
    operation = get_object_or_404(
        CashOperation.objects.select_related("cashier", "cash_register"),
        pk=pk
    )
    context = {
        "operation": operation
    }
    return HttpResponse(template.render(context, request))

@login_required
@role_required("Admin")
def cashoperation_validate(request, pk):
    # Récupérer l'opération
    operation = get_object_or_404(CashOperation, pk=pk)

    if operation.validated_by_admin:
        messages.info(request, "Cette opération est déjà validée.")
    else:
        operation.validated_by_admin = True
        operation.save()
        messages.success(request, f"Opération #{operation.id} validée avec succès.")

    return redirect("cashoperation_list")