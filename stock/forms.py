from django import forms
from .models import StockEntry, StockExit

class StockEntryForm(forms.ModelForm):
    class Meta:
        model = StockEntry
        fields = ['product', 'supplier', 'quantity', 'unit_cost', 'reason']
        widgets = {
            'product': forms.Select(attrs={
                'class': 'form-control'
            }),
            'supplier': forms.Select(attrs={
                'class': 'form-control',
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'unit_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
             'reason': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Vente, Perte, Dégradation'
            }),
        }


class StockExitForm(forms.ModelForm):
    class Meta:
        model = StockExit
        fields = ['product', 'quantity', 'reason']
        widgets = {
            'product': forms.Select(attrs={
                'class': 'form-control'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'reason': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Vente, Perte, Dégradation'
            }),
        }