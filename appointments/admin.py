from django.contrib import admin
from django import forms
from django.contrib.auth import get_user_model

from .models import Specialty, Doctor, Appointment

User = get_user_model()


class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        qs = User.objects.filter(is_doctor=True)
        if self.instance and getattr(self.instance, 'user', None):
            qs = qs | User.objects.filter(pk=self.instance.user.pk)
        self.fields['user'].queryset = qs.distinct()


# class PatientForm(forms.ModelForm):
#     class Meta:
#         model = Patient
#         fields = '__all__'

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         qs = User.objects.filter(is_doctor=False)
#         if self.instance and getattr(self.instance, 'user', None):
#             qs = qs | User.objects.filter(pk=self.instance.user.pk)
#         self.fields['user'].queryset = qs.distinct()


class AppointmentInline(admin.TabularInline):
    model = Appointment
    extra = 0
    fields = ('patient', 'date', 'time', 'status')
    raw_id_fields = ('patient',)
    show_change_link = True


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    form = DoctorForm
    list_display = ('__str__', 'user_email', 'specialty', 'office_address')
    list_select_related = ('user', 'specialty')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'specialty__name')
    list_filter = ('specialty',)
    inlines = [AppointmentInline]
    ordering = ('user__username',)

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'


# @admin.register(Patient)
# class PatientAdmin(admin.ModelAdmin):
#     form = PatientForm
#     list_display = ('__str__', 'user_email', 'insurance_number', 'birth_date')
#     list_select_related = ('user',)
#     search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'insurance_number')
#     ordering = ('user__username',)

#     def user_email(self, obj):
#         return obj.user.email
#     user_email.short_description = 'Email'


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ('name', 'num_doctors')
    search_fields = ('name',)

    def num_doctors(self, obj):
        return obj.doctors.count()
    num_doctors.short_description = 'Number of doctors'


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'patient', 'date', 'time', 'status')
    list_filter = ('status', 'date', 'doctor__specialty')
    search_fields = ('doctor__user__username', 'doctor__user__first_name', 'patient__user__username', 'patient__user__email')
    date_hierarchy = 'date'
    raw_id_fields = ('doctor', 'patient')
    ordering = ('-date', 'time')
