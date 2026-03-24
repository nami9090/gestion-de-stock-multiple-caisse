from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from .models import Sale,SaleItem

# Create your views here.
def validation_sale(request):
    # Récupérer la vente draft la plus récente
    sale = Sale.objects.filter(status="draft").first()
    if not sale:
        messages.warning(request, "Aucune vente en cours.")
        return redirect("sale_list")

    context = {
        "sale": sale,
        "items": sale.items.all()
    }
    return render(request, "validate_sale.html", context)

@login_required
def validate_sale_admin(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    # Vérifier si déjà validée
    if sale.validated_by_admin:
        messages.warning(request, "Cette vente est déjà validée.")
        return redirect("sale:validation_sale")
    # Vérifier qu'il y a des produits
    if not sale.items.exists():
        messages.warning(request, "Impossible de valider une vente vide.")
        return redirect("sale:validation_sale")
    # Validation
    sale.validated_by_admin = True
    sale.validated_at = timezone.now()
    sale.validated_by = request.user
    sale.save()
    messages.success(request, "La vente a été validée par l'administrateur.")
    return redirect("sale:validation_sale")