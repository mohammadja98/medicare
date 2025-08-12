from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from appointments.models import Appointment, Doctor


class RedirectUserView(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        if request.user.is_doctor:
            return redirect(reverse('doctor-dashboard'))
        else:
            return redirect(reverse('patient-dashboard'))



class DoctorDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/doctor_dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        # اطمینان از اینکه فقط پزشک‌ها به این صفحه دسترسی دارند
        if not request.user.is_doctor:
            messages.error(request, "You are not authorized to view this page.")
            return redirect('patient-dashboard')

        # اگر پروفایل دکتر وجود نداشت → هدایت به تکمیل پروفایل
        if not Doctor.objects.filter(user=request.user).exists():
            return redirect('appointments:complete_doctor_profile')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doctor = Doctor.objects.get(user=self.request.user)

        # امروز
        today = timezone.localdate()

        todays_appointments = Appointment.objects.filter(
            doctor=doctor,
            date=today
        )

        # آینده
        upcoming_appointments = Appointment.objects.filter(
            doctor=doctor,
            date__gt=today
        ).order_by('date', 'time')

        # گذشته
        past_appointments = Appointment.objects.filter(
            doctor=doctor,
            date__lt=today
        ).order_by('-date', '-time')

        # تعداد بیماران یکتا
        total_patients = Appointment.objects.filter(
            doctor=doctor
        ).values('patient').distinct().count()

        context.update({
            'todays_appointments': todays_appointments,
            'upcoming_appointments': upcoming_appointments,
            'past_appointments': past_appointments,
            'total_patients': total_patients,
        })
        return context

class PatientDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/patient_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        today = timezone.now().date()

        # نوبت‌های آینده
        upcoming_appointments = Appointment.objects.filter(
            patient=user,
            date__gte=today
        ).order_by('date', 'time')

        # نوبت‌های گذشته
        past_appointments = Appointment.objects.filter(
            patient=user,
            date__lt=today
        ).order_by('-date', '-time')

        # تعداد دکترهای یکتا که بیمار تا حالا ویزیت کرده (confirmed)
        total_doctors_visited = Appointment.objects.filter(
            patient=user,
            status='confirmed'
        ).values('doctor').distinct().count()

        context.update({
            'upcoming_appointments': upcoming_appointments,
            'recent_appointments': upcoming_appointments[:5],
            'past_appointments': past_appointments,
            'past_appointments_count': past_appointments.count(),
            'total_doctors_visited': total_doctors_visited
        })
        return context