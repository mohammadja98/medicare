from django.db import models
from django.conf import settings
from django.shortcuts import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model


class Specialty(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Specialty Name'))

    class Meta:
        verbose_name = _('Specialty')
        verbose_name_plural = _('Specialties')

    def __str__(self):
        return self.name


class Doctor(models.Model):
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='doctor_profile',
        limit_choices_to={'is_doctor': True}, # Only link to users marked as doctors
        verbose_name=_('User')
    )
    specialty = models.ForeignKey(
        Specialty,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='doctors',
        verbose_name=_('Specialty')
    )
    biography = models.TextField(verbose_name=_('Biography'), blank=True)
    office_address = models.CharField(max_length=255, verbose_name=_('Office Address'), blank=True)

    class Meta:
        verbose_name = _('Doctor')
        verbose_name_plural = _('Doctors')

    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username}"

    def get_absolute_url(self):
        # We can use the doctor's user ID for the detail view URL.
        return reverse('appointments:doctor_detail', args=[self.user.pk])



# This is the central model for booking appointments.
# It links a patient (CustomUser) to a doctor (Doctor) at a specific time and date.
class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('confirmed', _('Confirmed')),
        ('cancelled', _('Cancelled')),
        ('completed', _('Completed')),
    ]

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name=_('Doctor')
    )
    patient = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name=_('Patient')
    )
    date = models.DateField(verbose_name=_('Appointment Date'))
    time = models.TimeField(verbose_name=_('Appointment Time'))
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Status')
    )
    description = models.TextField(blank=True, verbose_name=_('Description'))

    class Meta:
        verbose_name = _('Appointment')
        verbose_name_plural = _('Appointments')
        # This constraint ensures a patient can't book the same time slot with the same doctor twice.
        unique_together = ('doctor', 'date', 'time', 'patient')

    def __str__(self):
        return f"Appointment with {self.doctor} on {self.date} at {self.time}"
