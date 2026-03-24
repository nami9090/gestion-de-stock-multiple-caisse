from django.urls import path
from . import views

app_name = "sale"
urlpatterns = [
	path('validation-vente', views.validation_sale, name='validation_sale'),
	path('validate-sale-admin/<int:sale_id>/', views.validate_sale_admin, name='validate_sale_admin'),
]