from django import forms
from .models import CashOperation, Cashier, CashRegister

class CashOperationForm(forms.ModelForm):
    class Meta:
        model = CashOperation
        fields = ['operation_type', 'description', 'amount']
        widgets = {
            'operation_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'rows':2}),
            'amount': forms.NumberInput(attrs={'class':'form-control'}) 
        }

class CashierForm(forms.ModelForm):
    class Meta:
        model = Cashier
        fields = ['user', 'phone', 'is_active']
        widgets = {
        'user': forms.Select(attrs={
            'class': 'form-control'
        }),
        'phone': forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: 000-000-000'
        }),
        'is_active': forms.CheckboxInput(attrs={
            'class':'form-control'
        })
    }

class CashRegisterForm(forms.ModelForm):
    class Meta:
        model = CashRegister
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Namizana'
        }),
    }

class AssignCashierForm(forms.Form):
    cashier = forms.ModelChoiceField(
        queryset=Cashier.objects.filter(is_active=True),
        label="Choisir un caissier"
    )