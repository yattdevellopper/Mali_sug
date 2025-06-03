# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm

# Importation des vues d'authentification de Django (pour la gestion des mots de passe)
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy # Pour les redirections dans les vues basées sur les classes si nécessaire

# --- Vues d'Authentification de Base ---

def register_view(request):
    """
    Vue d'inscription des utilisateurs.
    Affiche un formulaire pour créer un nouveau compte.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Inscription réussie. Bienvenue sur Shopy Five !")
            
            if user.is_seller:
                return redirect('vendor_dashboard')
            else:
                return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erreur dans le champ '{form.fields[field].label or field}': {error}")
            messages.error(request, "Échec de l'inscription. Veuillez corriger les erreurs ci-dessous.")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    """
    Vue de connexion des utilisateurs.
    Gère l'authentification et redirige l'utilisateur.
    """
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"Vous êtes connecté(e) en tant que {username}.")
                if user.is_seller:
                    return redirect('vendor_dashboard')
                return redirect('home')
            else:
                messages.error(request, "Nom d'utilisateur ou mot de passe invalide.")
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe invalide. Veuillez réessayer.")
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    """
    Vue de déconnexion des utilisateurs.
    Déconnecte l'utilisateur et le redirige vers la page d'accueil.
    """
    logout(request)
    messages.info(request, "Vous avez été déconnecté(e) avec succès.")
    return redirect('home')

# --- Vues de Gestion des Mots de Passe (en utilisant les vues intégrées de Django) ---

# Changement de mot de passe pour un utilisateur connecté
# Note : C'est une instance d'une classe de vue, prête à être utilisée dans urls.py.
# La nommer ici "password_change_view" est une convention, mais c'est la vue de Django.
password_change_view = auth_views.PasswordChangeView.as_view(
    template_name='accounts/password_change_form.html',
    success_url=reverse_lazy('password_change_done') # Redirige vers password_change_done après succès
)

# Page de confirmation après un changement de mot de passe réussi
password_change_done_view = auth_views.PasswordChangeDoneView.as_view(
    template_name='accounts/password_change_done.html'
)

# Formulaire pour demander la réinitialisation du mot de passe (via email)
password_reset_view = auth_views.PasswordResetView.as_view(
    template_name='accounts/password_reset_form.html',
    email_template_name='accounts/password_reset_email.html', # Template pour l'e-mail envoyé
    subject_template_name='accounts/password_reset_subject.txt', # Template pour le sujet de l'e-mail
    success_url=reverse_lazy('password_reset_done') # Redirige vers password_reset_done après succès
)

# Page de confirmation après l'envoi de l'e-mail de réinitialisation
password_reset_done_view = auth_views.PasswordResetDoneView.as_view(
    template_name='accounts/password_reset_done.html'
)

# Formulaire pour définir le nouveau mot de passe (après avoir cliqué sur le lien dans l'e-mail)
password_reset_confirm_view = auth_views.PasswordResetConfirmView.as_view(
    template_name='accounts/password_reset_confirm.html',
    success_url=reverse_lazy('password_reset_complete') # Redirige vers password_reset_complete après succès
)

# Page de confirmation après la réinitialisation du mot de passe réussie
password_reset_complete_view = auth_views.PasswordResetCompleteView.as_view(
    template_name='accounts/password_reset_complete.html'
)