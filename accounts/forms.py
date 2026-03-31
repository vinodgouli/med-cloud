from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, MedicalRecord

class PatientSignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'custom-input', 'placeholder': field.label})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'patient'
        if commit:
            user.save()
        return user

class DoctorSignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'custom-input', 'placeholder': field.label})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'doctor'
        if commit:
            user.save()
        return user


class AssignDoctorForm(forms.Form):
    doctor = forms.ModelChoiceField(
        queryset=User.objects.filter(role='doctor'),
        required=True,
        label="Select Doctor",
        widget=forms.Select(attrs={'class': 'custom-input'})
    )

class DoctorSearchForm(forms.Form):
    keyword = forms.CharField(
        max_length=100,
        required=True,
        label="Search Keyword",
        widget=forms.TextInput(attrs={
            'class': 'custom-input',
            'placeholder': 'Enter keyword to search',
            'autocomplete': 'off',
        })
    )




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
