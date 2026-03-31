from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/patient/', views.patient_signup, name='patient_signup'),
    path('signup/doctor/', views.doctor_signup, name='doctor_signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/patient/', views.patient_dashboard, name='patient_dashboard'),
    path('dashboard/doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('upload_record/', views.patient_upload_record, name='upload_record'),
    path('record/<int:record_id>/decrypt/', views.decrypt_medical_record, name='decrypt_medical_record'),
    path('dashboard/doctor/search/', views.doctor_search, name='doctor_search'),
    path('download-decrypted/<int:record_id>/', views.download_decrypted_file, name='download_decrypted_file'),
    path('decrypt-script/<int:record_id>/', views.decrypt_file_script, name='decrypt_file_script'),
    path('assign-doctor/', views.assign_doctor, name='assign_doctor'),

]
