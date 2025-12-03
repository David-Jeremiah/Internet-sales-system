# forms.py - COMPLETE FIXED VERSION

from django import forms
from .models import Sale, Customer, InternetPackage, Visit, Prospect


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['full_name', 'phone', 'email', 'address', 'id_number']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-zakcom-blue'}),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-zakcom-blue'}),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-zakcom-blue'}),
            'address': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-zakcom-blue',
                'rows': 3}),
            'id_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-zakcom-blue'}),
        }


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['package', 'status', 'sale_date', 'installation_date', 'contract_duration', 'notes']
        widgets = {
            'package': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-zakcom-blue'}),
            'status': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-zakcom-blue'}),
            'sale_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-zakcom-blue',
                'type': 'date'}),
            'installation_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-zakcom-blue',
                'type': 'date'}),
            'contract_duration': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-zakcom-blue'}),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-zakcom-blue',
                'rows': 3}),
        }


class VisitForm(forms.ModelForm):
    class Meta:
        model = Visit
        fields = ['location', 'visit_date', 'visit_time', 'outcome', 'feedback',
                  'price_concern', 'coverage_concern', 'has_existing_provider',
                  'existing_provider_name', 'follow_up_date', 'follow_up_notes']
        widgets = {
            'location': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-zakcom-blue',
                'placeholder': 'e.g., Kololo, ABC Apartments'}),
            'visit_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-zakcom-blue',
                'type': 'date'}),
            'visit_time': forms.TimeInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-zakcom-blue',
                'type': 'time'}),
            'outcome': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-zakcom-blue'}),
            'feedback': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-zakcom-blue',
                'rows': 4, 'placeholder': 'What did the prospect say? Any specific concerns or interests?'}),
            'price_concern': forms.CheckboxInput(
                attrs={'class': 'w-5 h-5 text-zakcom-blue rounded focus:ring-zakcom-blue'}),
            'coverage_concern': forms.CheckboxInput(
                attrs={'class': 'w-5 h-5 text-zakcom-blue rounded focus:ring-zakcom-blue'}),
            'has_existing_provider': forms.CheckboxInput(
                attrs={'class': 'w-5 h-5 text-zakcom-blue rounded focus:ring-zakcom-blue'}),
            'existing_provider_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-zakcom-blue',
                'placeholder': 'e.g., MTN, Airtel'}),
            'follow_up_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-zakcom-blue',
                'type': 'date'}),
            'follow_up_notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-zakcom-blue',
                'rows': 2}),
        }


class ProspectForm(forms.ModelForm):
    class Meta:
        model = Prospect
        fields = ['full_name', 'phone', 'email', 'address', 'location', 'interest_level', 'preferred_package']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-zakcom-blue'}),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-zakcom-blue'}),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-zakcom-blue'}),
            'address': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-zakcom-blue',
                'rows': 2}),
            'location': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-zakcom-blue'}),
            'interest_level': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-zakcom-blue'}),
            'preferred_package': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-zakcom-blue'}),
        }

    # CRITICAL: Make all prospect fields NOT required since prospect is optional
    def __init__(self, *args, **kwargs):
        super(ProspectForm, self).__init__(*args, **kwargs)
        # Make all fields optional
        for field_name in self.fields:
            self.fields[field_name].required = False