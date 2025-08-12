from django.views.generic import DetailView
from datetime import timezone
from django.views import generic, View
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.utils.translation import gettext as _
from django.http import HttpResponseForbidden
from .forms import DoctorProfileForm

from .models import Specialty, Doctor, Appointment
from .forms import AppointmentForm


class SpecialtyListView(generic.ListView):
    model = Specialty
    template_name = 'appointments/specialty_list.html'
    context_object_name = 'specialties'


class DoctorListView(generic.ListView):
    model = Doctor
    template_name = 'appointments/doctor_list.html'
    context_object_name = 'doctors'

    def get_queryset(self):
        specialty_id = self.kwargs.get('specialty_id')
        qs = Doctor.objects.select_related('user', 'specialty').all()
        if specialty_id:
            qs = qs.filter(specialty_id=specialty_id)
        return qs




class DoctorDetailView(DetailView):
    model = Doctor
    template_name = 'appointments/doctor_detail.html'
    context_object_name = 'doctor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # فرم خالی برای GET
        context['appointment_form'] = kwargs.get('appointment_form') or AppointmentForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()  # دکتر فعلی

        # جلوگیری از رزرو توسط خود دکتر
        if request.user == self.object.user:
            messages.error(request, _("You cannot book an appointment with yourself."))
            return redirect('appointments:doctor_detail', pk=self.object.pk)

        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.doctor = self.object

            # چک تکراری بودن نوبت
            if Appointment.objects.filter(
                patient=request.user,
                date=appointment.date,
                time=appointment.time
            ).exists():
                return render(request, 'appointments/duplicate_appointment.html', {
                    'doctor': self.object,
                    'doctor_url': reverse('appointments:doctor_detail', args=[self.object.pk]),
                    'date': appointment.date,
                    'time': appointment.time
                })

            appointment.save()
            messages.success(request, _("Appointment booked successfully!"))
            return redirect('appointments:doctor_detail', pk=self.object.pk)

        # اگر فرم مشکل داشت، دوباره صفحه رو با خطاها نشون بده
        context = self.get_context_data(appointment_form=form)
        return self.render_to_response(context)
class AppointmentCreateView(LoginRequiredMixin, View):
    """
    ایجاد نوبت برای کاربر لاگین کرده (به عنوان Patient)
    """
    def post(self, request, doctor_id):
        doctor = get_object_or_404(Doctor, pk=doctor_id)
        # پیدا کردن پروفایل بیمار برای کاربر فعلی
        if request.user == doctor.user:
            messages.error(request, "You cannot book an appointment with yourself.")
            return redirect(doctor.get_absolute_url())


        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.doctor = doctor
            appointment.patient = request.user
            try:
                appointment.save()
                messages.success(request, "Your appointment has been booked successfully.")
            except Exception as e:
                messages.error(request, f"Error saving appointment: {e}")
            return redirect(doctor.get_absolute_url())

        # اگر فرم معتبر نبود
        context = {
            'doctor': doctor,
            'appointment_form': form,
        }
        return render(request, 'appointments/doctor_detail.html', context)



@method_decorator(login_required, name='dispatch')
class CompleteDoctorProfileView(View):
    template_name = 'appointments/complete_doctor_profile.html'

    def get(self, request):
        if not request.user.is_doctor:
            return redirect('home')

        # یا پروفایل موجود را بگیر، یا جدید بساز
        doctor, created = Doctor.objects.get_or_create(user=request.user)
        form = DoctorProfileForm(instance=doctor)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        if not request.user.is_doctor:
            return redirect('home')

        doctor, created = Doctor.objects.get_or_create(user=request.user)
        form = DoctorProfileForm(request.POST, instance=doctor)

        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been saved successfully.")
            return redirect('doctor-dashboard')

        return render(request, self.template_name, {'form': form})
    

class PatientUpcomingAppointmentsView(LoginRequiredMixin, generic.ListView):
    model = Appointment
    template_name = 'accounts/patient_upcoming_appointments.html'
    context_object_name = 'appointments'

    def get_queryset(self):
        return Appointment.objects.filter(
            patient=self.request.user,
            date__gte=timezone.now().date()
        ).order_by('date', 'time')
