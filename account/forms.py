from django import forms
from django.contrib.auth.models import User, Group
from .models import Profile

class UserCreateForm(forms.ModelForm):
    photo = forms.ImageField(required=False)

    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'class':'form-control'}),
        required=True
    )

    password_confirm = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={'class':'form-control'}),
        required=True
    )

    roles = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=True,
        widget=forms.CheckboxSelectMultiple,
        label = "Role de l'utilisateur"
    )

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'photo', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class':'form-control'}),
            'email': forms.EmailInput(attrs={'class':'form-control'}),
            'password': forms.PasswordInput(attrs={'class':'form-control'}),
            'photo': forms.ClearableFileInput(attrs={'class':'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class':'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Les mots de passe ne correspondent pas")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        # mot de passe hashé correctement
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()
            user.groups.set(self.cleaned_data['roles'])

        return user

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["photo"]
        widgets = {
            'photo': forms.ClearableFileInput(attrs={'class':'form-control'}),
        }
