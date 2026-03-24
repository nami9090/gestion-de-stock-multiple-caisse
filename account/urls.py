from django.urls import path
from . import views

app_name='account'

urlpatterns = [
	path('login/', views.login_view, name='login'),
	path('logout-session/', views.logout_view, name='logout'),

	path('listes/', views.gestion_utilisateur, name='gestion_utilisateur'),
	path('creation/', views.creer_utilisateur, name='creer_utilisateur'),
	path('mis a jour/<int:pk>/', views.update_utilisateur, name='update_utilisateur'),
	path('supprimer/<int:user_id>/', views.supprimer_utilisateur, name='supprimer_utilisateur'),
	path('activer-desactiver/<int:id>/', views.activer_desactiver_utilisateur, name='activer_desactiver_utilisateur'),
	path("profile/update/", views.profile_update, name="profile_update"),
]