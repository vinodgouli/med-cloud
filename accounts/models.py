from django.conf import settings
from io import BytesIO
import os
from django.contrib.postgres.fields import ArrayField
from django.db import models
from cryptography.fernet import Fernet
from django.core.files.base import ContentFile
from .utils import encrypt_file,upload_to_s3
from storages.backends.s3boto3 import S3Boto3Storage

from django import forms
from .utils import encrypt_file
from django.core.files.storage import FileSystemStorage

class EncryptedRecord(models.Model):
    blob = models.FileField(upload_to="records/")
# Create your models here.
from django.contrib.auth.models import AbstractUser
fs = FileSystemStorage(location='media/encrypted_files')

class User(AbstractUser):
    ROLE_CHOICES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
class PatientDoctorAssignment(models.Model):
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assigned_doctors')
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patients')
    
    def __str__(self):
        return f"{self.patient.username} assigned to Dr. {self.doctor.username}"



class EncryptionKey(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # Store the Fernet key *as bytes* exactly as returned by Fernet.generate_key()
    key = models.BinaryField()

    def save(self, *args, **kwargs):
        if not self.pk or not self.key:
            self.key = Fernet.generate_key()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Encryption key for {self.user.username}"




class MedicalRecord(models.Model):
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='medical_records'
    )
    # We store the S3 key path in this FileField (no local file I/O is required)
    file = models.FileField(upload_to='medical_records/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    # simple S3-only storage (we’re storing encrypted bytes in this "file")
    encrypted_keywords = models.TextField(blank=True, null=True)  # your searchable tokens

    def save(self, *args, **kwargs):
        # Only perform encryption/upload the first time the object is saved with a file
        if self.file and not self.pk:
            enc_key = EncryptionKey.objects.get(user=self.patient).key  # bytes
            # read uploaded file bytes
            raw = self.file.read()
            # Fernet-encrypt
            encrypted = encrypt_file(BytesIO(raw), enc_key)
            # Give the S3 object an .enc suffix to make it obvious
            s3_key = f"medical_records/{self.patient.id}/{os.path.basename(self.file.name)}.enc"
            upload_to_s3(encrypted, settings.AWS_STORAGE_BUCKET_NAME, s3_key)
            # store only the S3 key path in DB (no local file remains)
            self.file.name = s3_key
        super().save(*args, **kwargs)


class MedicalRecordUploadForm(forms.ModelForm):
    assigned_doctors = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(role='doctor'),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Assign to Doctors"
    )

    class Meta:
        model = MedicalRecord
        fields = ['file', 'encrypted_keywords', 'assigned_doctors']

