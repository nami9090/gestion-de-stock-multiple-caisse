from django.urls import path
from . import views

app_name="rapport"

urlpatterns = [
	path('vente/par-jour/', views.rapport_journalier, name='rapport_journalier'),
	path('vente/par-semaine/',views.rapport_hebdomadaire, name='rapport_hebdomadaire'),
	path('vente/par-mois/', views.rapport_mensuel, name='rapport_mensuel'),
	path('caisse/par-jour/', views.rapport_caissier_journalier, name='rapport_caissier_journalier'),
	path('caisse/par-semaine/', views.rapport_caissier_hebdomadaire, name='rapport_caissier_hebdomadaire'),
	path('caisse/par-mois/', views.rapport_caissier_mensuel, name='rapport_caissier_mensuel'),
	path('produits/les-plus-vendus/', views.produits_plus_vendus, name='produits_plus_vendus'),
	path('produits/rupture-en-stock/', views.produits_rupture_stock, name='produits_rupture_stock'),
	path('finance/rapport-financier/', views.financial_report, name='financial_report'),
]