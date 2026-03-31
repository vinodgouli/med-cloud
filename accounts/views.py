import os
from django.http import HttpResponse, Http404
import hmac
import boto3
from cryptography.fernet import Fernet,InvalidToken
import hashlib
from .models import User, PatientDoctorAssignment, MedicalRecord, EncryptionKey

from django.db.models import Q
from django.shortcuts import render, redirect,get_object_or_404
from django.conf import settings
from django.contrib.auth import login, authenticate, logout
from .forms import PatientSignUpForm, DoctorSignUpForm
from .forms import MedicalRecordUploadForm,DoctorSearchForm
from django.core.files.base import ContentFile
from .utils import download_from_s3
from .models import PatientDoctorAssignment, MedicalRecord,EncryptionKey
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .utils import decrypt_file,decrypt_bytes,double_decrypt_bytes

def home(request):
    return render(request, 'accounts/home.html')

def patient_signup(request):
    if request.method == 'POST':
        form = PatientSignUpForm(request.POST) 
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('patient_dashboard')
    else:
        form = PatientSignUpForm()
    return render(request, 'accounts/patient_signup.html', {'form': form, 'user_type': 'Patient'})

def doctor_signup(request):
    if request.method == 'POST':
        form = DoctorSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('doctor_dashboard')
    else:
        form = DoctorSignUpForm()
    return render(request, 'accounts/doctor_signup.html', {'form': form, 'user_type': 'Doctor'})

@login_required
def doctor_search(request):
    if request.user.role != 'doctor':
        return redirect('home')

    form = DoctorSearchForm(request.GET or None)
    results = []

    if form.is_valid():
        keyword = form.cleaned_data['keyword'].lower()

        # Get patients assigned to this doctor
        assigned_patients = PatientDoctorAssignment.objects.filter(
            doctor=request.user
        ).values_list('patient', flat=True)

        # Search encrypted keywords in MedicalRecords of assigned patients
        matching_records = []

        # For each patient, get their key and generate token for keyword
        for patient_id in assigned_patients:
            try:
                key = EncryptionKey.objects.get(user_id=patient_id).key
            except EncryptionKey.DoesNotExist:
                continue

            if isinstance(key,str):
                key =key.encode()
            token = hmac.new(key, keyword.encode(), hashlib.sha256).hexdigest()

            # Query MedicalRecords with this token in encrypted_keywords
            matches = MedicalRecord.objects.filter(
                patient_id=patient_id,
                encrypted_keywords__contains=[token]  # JSONField lookup
            )
            matching_records.extend(matches)

        results = list(set(matching_records))

    return render(request, 'accounts/doctor_search.html', {'form': form, 'results': results})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.role == 'patient':
                return redirect('patient_dashboard')
            else:
                return redirect('doctor_dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def patient_dashboard(request):
    if request.user.role != 'patient':
        return redirect('home')

    # Fetch all registered doctors for assigning
    all_doctors = User.objects.filter(role='doctor')

    # Initialize the upload form with this queryset
    form = MedicalRecordUploadForm()
    form.fields['assigned_doctors'].queryset = all_doctors

    return render(request, 'accounts/patient_dashboard.html', {
        'form': form,
        'doctors': all_doctors
    })




def generate_keyword_token(key, keyword):
    return hmac.new(key, keyword.encode(), hashlib.sha256).hexdigest()

@login_required
def patient_upload_record(request):
    if request.user.role != 'patient':
        return redirect('home')

    if request.method == 'POST':
        form = MedicalRecordUploadForm(request.POST, request.FILES)
        if form.is_valid():
            record = form.save(commit=False)
            record.patient = request.user

            # Encrypt the file as before
            key_obj = EncryptionKey.objects.get(user=request.user)
            key_bytes = key_obj.key
            if isinstance(key_bytes, str):
                key_bytes = key_bytes.encode()
            fernet = Fernet(key_bytes)

            uploaded_file = request.FILES['file']
            file_bytes = uploaded_file.read()
            encrypted_bytes = fernet.encrypt(file_bytes)
            record.file.save(uploaded_file.name + '.enc', ContentFile(encrypted_bytes))

            # Handle keywords
            keywords = form.cleaned_data.get('encrypted_keywords', '')
            tokens = [
                hmac.new(key_bytes, kw.strip().lower().encode(), hashlib.sha256).hexdigest()
                for kw in keywords.split(',') if kw.strip()
            ]
            record.encrypted_keywords = tokens
            record.save()

            # Assign selected doctors
            for doctor in form.cleaned_data['assigned_doctors']:
                PatientDoctorAssignment.objects.get_or_create(
                    patient=request.user,
                    doctor=doctor
                )

            return redirect('patient_dashboard')
    else:
        form = MedicalRecordUploadForm()
        form.fields['assigned_doctors'].queryset = User.objects.filter(role='doctor')

    return render(request, 'accounts/upload_record.html', {'form': form})


@login_required
def doctor_dashboard(request):
    if request.user.role != 'doctor':
        return redirect('home')

    # Get patients assigned to this doctor
    assigned_patients = PatientDoctorAssignment.objects.filter(doctor=request.user).values_list('patient', flat=True)

    # Get medical records of assigned patients
    records = MedicalRecord.objects.filter(patient__in=assigned_patients).order_by('-uploaded_at')

    return render(request, 'accounts/doctor_dashboard.html', {'records': records})

@login_required
def decrypt_medical_record(request, record_id):
    try:
        record = MedicalRecord.objects.get(pk=record_id)
    except MedicalRecord.DoesNotExist:
        raise Http404("Record not found")

    if request.user.role == 'doctor':
        pass
    elif request.user != record.patient:
        raise Http404("Not allowed")

    key = EncryptionKey.objects.get(user=record.patient).key
    fernet = Fernet(key.encode() if isinstance(key, str) else key)

    # Download encrypted bytes
    encrypted_bytes = download_from_s3(settings.AWS_STORAGE_BUCKET_NAME, record.file.name)
    try:
        plaintext = fernet.decrypt(encrypted_bytes)
    except InvalidToken:
        return HttpResponse("Decryption failed. Check the key or file.", status=400)



    

    download_name = record.file.name.rsplit('/', 1)[-1].replace('.enc', '')
    resp = HttpResponse(plaintext, content_type="application/pdf")
    resp['Content-Disposition'] = f'attachment; filename="{download_name}"'
    return resp

@login_required
def decrypt_file_script(request, record_id):
    """
    This mimics your standalone script logic but works with your project files on S3.
    """
    # 1️⃣ Get the record
    record = get_object_or_404(MedicalRecord, pk=record_id)

    # 2️⃣ Permissions check
    if request.user.role == 'doctor':
        from .models import PatientDoctorAssignment
        if not PatientDoctorAssignment.objects.filter(doctor=request.user, patient=record.patient).exists():
            return HttpResponse("Not allowed", status=403)
    elif request.user != record.patient:
        return HttpResponse("Not allowed", status=403)

    # 3️⃣ Get the key (exactly like your script)
    key = EncryptionKey.objects.get(user=record.patient).key
    if isinstance(key, str):
        key = key.encode()
    fernet = Fernet(key)

    try:
        # 4️⃣ Download encrypted bytes from S3
        encrypted_bytes = download_from_s3(settings.AWS_STORAGE_BUCKET_NAME, record.file.name)

        # 5️⃣ Decrypt
        decrypted_bytes = fernet.decrypt(encrypted_bytes)

        # 6️⃣ Send decrypted file as download
        original_filename = record.file.name.rsplit('/', 1)[-1].replace('.enc', '')
        response = HttpResponse(decrypted_bytes, content_type="application/pdf")
        response['Content-Disposition'] = f'attachment; filename="{original_filename}"'
        return response

    except InvalidToken:
        return HttpResponse("❌ Decryption failed. Wrong key or corrupted file.", status=400)
    except Exception as e:
        return HttpResponse(f"❌ Error: {e}", status=500)

@login_required
def assign_doctor(request):
    if request.user.role != 'patient':
        return redirect('home')

    from .forms import AssignDoctorForm
    from .models import PatientDoctorAssignment

    if request.method == 'POST':
        form = AssignDoctorForm(request.POST)
        if form.is_valid():
            doctor = form.cleaned_data['doctor']
            # Avoid duplicate assignments
            assignment, created = PatientDoctorAssignment.objects.get_or_create(
                patient=request.user,
                doctor=doctor
            )
            message = (
                f"Successfully assigned to Dr. {doctor.username}."
                if created else "You are already assigned to this doctor."
            )
            return render(request, 'accounts/assign_doctor.html', {'form': form, 'message': message})
    else:
        form = AssignDoctorForm()

    return render(request, 'accounts/assign_doctor.html', {'form': form})

@login_required
def download_decrypted_file(request, record_id):
    record = get_object_or_404(MedicalRecord, pk=record_id)

    # Permissions
    if request.user.role == 'doctor':
        if not PatientDoctorAssignment.objects.filter(doctor=request.user, patient=record.patient).exists():
            return HttpResponse("Not allowed", status=403)
    elif request.user != record.patient:
        return HttpResponse("Not allowed", status=403)

    key_obj = EncryptionKey.objects.get(user=record.patient)
    key = key_obj.key

    encrypted_bytes = download_from_s3(settings.AWS_STORAGE_BUCKET_NAME, record.file.name)

    try:
        # Detect double encryption
        if record.file.name.endswith('.enc.enc'):
            decrypted_bytes = double_decrypt_bytes(encrypted_bytes, key)
        else:
            decrypted_bytes = decrypt_bytes(encrypted_bytes, key)
    except InvalidToken:
        return HttpResponse("Decryption failed: wrong key or corrupted file.", status=400)

    original_filename = record.file.name.rsplit('/', 1)[-1].replace('.enc', '')
    mime_type = 'application/pdf'  # or detect dynamically
    response = HttpResponse(decrypted_bytes, content_type=mime_type)
    response['Content-Disposition'] = f'attachment; filename="{original_filename}"'
    return response
