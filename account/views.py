from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .utils import redirect_user_by_role
from .forms import UserCreateForm, ProfileForm
from .models import UserActivityLog, Profile
from .decorators import role_required

from companie.models import Company


# Create your views here.
def login_view(request):
    # if request.user.is_authenticated:
    #   return redirect(redirect_user_by_role(user))
    # template = loader.get_template('login.html')
    company = Company.objects.first()
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username = username,
            password = password
        )
        if user is not None:
            login(request, user)
            redirect_url = redirect_user_by_role(user)
            return redirect(redirect_url)
        else:
            messages.warning(request, 'Email ou mot de pass incorect')

    context = {
        'company':company
    }
    return render(request, 'login.html', context)

def logout_view(request):
    logout(request)
    return redirect('account:login')


@login_required
@role_required('Admin')
def gestion_utilisateur(request):
    utilisateurs = User.objects.all().order_by('username')

    user_pagination = Paginator(utilisateurs, 10)
    pages_user = request.GET.get('pages_user')
    user_pages = user_pagination.get_page(pages_user)

    context = {
        'utilisateurs':user_pages
    }
    return render(request, 'gestion_utilisateur.html', context)

@login_required
@role_required('Admin')
def creer_utilisateur(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()

            profile, created = Profile.objects.get_or_create(user=user)

            profile.photo = form.cleaned_data.get("photo")
            profile.save()


            messages.success(request, f"L'utilisateur {user.username} a été créé avec succès !")
            return redirect('account:gestion_utilisateur')
        else:
            print(form.errors)
            messages.error(request, "Erreur : le formulaire est invalide.")
    else:
        form = UserCreateForm()
    context = {
        'form':form
    }
    return render(request, 'form_utilisateur.html', context)

@login_required
@role_required('Admin')
def update_utilisateur(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserCreateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()

            profile, created = Profile.objects.get_or_create(user=user)
            profile.photo = form.cleaned_data.get("photo")
            profile.save()

            messages.success(request, f"L'utilisateur {user.username} a été updated avec succès !")
            return redirect('account:gestion_utilisateur')
        else:
            messages.error(request, "Erreur : le formulaire est invalide.")
    else:
        form = UserCreateForm(instance=user)
    context = {
        'form':form,
        'user':user,
    }
    return render(request, 'form_utilisateur.html', context)

@login_required
@role_required('Admin')
def supprimer_utilisateur(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.user == user:
        messages.error(request, "Vous ne pouvez pas supprimer votre propre compte !")
        return redirect('account:gestion_utilisateur')

    if request.method == 'POST':
        user.delete()
        profile.photo = form.cleaned_data.get("photo")
        profile.delete()
        messages.success(request, f"L'utilisateur {user.username} a été supprimé avec succès !")
        return redirect('account:gestion_utilisateur')
    context = {
        'form':form,
        'user':user,
    }
    return render(request, 'supprimer_user.html', context)


@login_required
@role_required('Admin')
def activer_desactiver_utilisateur(request, id):
    user = get_object_or_404(User, pk=id)
    user.is_active = not user.is_active
    user.save()
    messages.success(request, f"L'utilisateur {user.username} devient {user.is_active}")
    return redirect('account:gestion_utilisateur')

@login_required
@role_required("Admin","Caisse","Gestionnaire_stock")
def profile_update(request):
    profile = request.user.profile

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("dashboard:admin_dashboard")  # redirige après modification
    else:
        form = ProfileForm(instance=profile)

    return render(request, "profile_update.html", {"form": form})