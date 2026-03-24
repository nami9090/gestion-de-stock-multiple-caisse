from django.urls import path, include
from . import views


urlpatterns = [
	path('', views.home, name='home'),    

    #DASHBOARD
    path('', include('dashboard.urls', namespace='dashboard')),
    path('utilisateurs/', include('account.urls', namespace='account')),
    path('rapport/', include('rapports.urls', namespace='rapport')),

    path('vente/', include('sale.urls', namespace='sale')),

    # product management
    path('ajouter-produit/', views.product_create, name='product_create'),
    path('liste-des-produits/', views.product_list_prod, name='product_list_prod'),
    path('update-produit/<int:pk>/', views.product_update, name='product_update'),
    path('delete-produit/<int:pk>/', views.product_delete, name='product_delete'),
    path('detail-produit/<int:pk>/', views.product_detail, name='product_detail'),

    ## categories product
	path('categories-liste/', views.category_list, name='category_list'),
	path('ajouter-categorie/', views.category_create, name='category_create'),
	path('update-categorie/<int:pk>/', views.category_update, name='category_update'),
	path('effacer-categorie/<int:pk>/', views.category_delete, name='category_delete'),

    #Suppliers
	path('fournisseur-liste/', views.supplier_list, name='supplier_list'),
	path('ajouter-fournisseur/', views.supplier_create, name='supplier_create'),
	path('update-fournisseur/<int:pk>/', views.supplier_update, name='supplier_update'),
	path('effacer-fournisseur/<int:pk>/', views.supplier_delete, name='supplier_delete'),

    #Stocks
	path('stock-liste/', views.stock_list, name='stock_list'),
    path('entree-stock/', views.stock_entry_create, name='stock_entry_create'),
    path('sortie-stock/', views.stock_exit_create, name='stock_exit_create'),
    path('historique-sortie-stock/', views.stock_exit_list, name='stock_exit_list'),
    path('historique-entree-stock/', views.stock_entry_list, name='stock_entry_list'),

    #user management
    path('list-users/', views.user_management, name='user_management'),
    path('creer-utilisateur/', views.create_user, name='create_user'),

    #sale management
    path('sale-list/', views.sale_list, name='sale_list'),
    path('sale-create/', views.sale_create, name='sale_create'),
    path('update-sale/<int:sale_id>/', views.update_sale, name='update_sale'),
    path('delete-sale/<int:sale_id>/', views.delete_sale, name='delete_sale'),
    path('sale-invoice/<int:sale_id>/', views.sale_invoice, name='sale_invoice'),

    path('finaliser-vente/', views.sale_finalize, name='sale_finalize'),
    path('vente-detail/<int:pk>/', views.sale_detail, name='sale_detail'),
    path('facture-vente-a4/<int:pk>/', views.sale_invoice, name='sale_invoice'),

    path('sale-create-caisse/', views.sale_create_caisse_multi, name='sale_create_caisse_multi'),
    path('sale-finaliser-caisse/', views.sale_finalize_caisse_multi, name='sale_finalize_caisse_multi'),

    #cashier management
    path('liste-caissiers/', views.cashier_list, name='cashier_list'),
    path('creer-caissier/', views.cashier_create, name='cashier_create'),
    path('update-caissier/<int:pk>/', views.cashier_update, name='cashier_update'),
    path('supprimer-caissier/<int:pk>/', views.cashier_delete, name='cashier_delete'),

    path('liste-caisse-virtuel/', views.cash_register_list, name='cash_register_list'),
    path('enregistrement-caisse/', views.cash_register_manage, name='cash_register_manage'),
    path('toggle_cash_register/<int:pk>/', views.toggle_cash_register, name='toggle_cash_register'),
    path('ouverture-caisse/<int:pk>/', views.cash_register_open, name='cash_register_open'),
    path('fermeture-caisse/<int:pk>/', views.cash_register_close, name='cash_register_close'),

    path('historique-caisse/', views.cashoperation_list, name='cashoperation_list'),
    path('sortie-caisse/', views.cashoperation_create, name='cashoperation_create'),
    path('sortie-caisse-detail/<int:pk>/',views.cashoperation_detail, name='cashoperation_detail'),
    path('cash-operation-valiser/<int:pk>/', views.cashoperation_validate, name='cashoperation_validate'),

]