from django import forms
from .models import Appointment, Doctor

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        exclude = ('patient', 'doctor')  # patient و doctor را در سرور مقداردهی می‌کنیم
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),

        }

class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['specialty', 'biography', 'office_address']
        widgets = {
            'specialty': forms.Select(attrs={'class': 'form-select'}),
            'biography': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'office_address': forms.TextInput(attrs={'class': 'form-control'}),
        }