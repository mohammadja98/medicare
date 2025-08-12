from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('specialties/', views.SpecialtyListView.as_view(), name='specialty_list'),
    path('doctors/', views.DoctorListView.as_view(), name='doctor_list_all'),  # همه دکترها
    path('doctors/specialty/<int:specialty_id>/', views.DoctorListView.as_view(), name='doctor_list'),  # فیلتر شده
    path('doctor/<int:pk>/', views.DoctorDetailView.as_view(), name='doctor_detail'),
    path('doctor/complete-profile/', views.CompleteDoctorProfileView.as_view(), name='complete_doctor_profile'),

]
