from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, HealthMetric
from datetime import date
import re
from django.core.exceptions import ValidationError
from PIL import Image

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError("Email is required")
        return email.lower().strip()

class UserProfileForm(forms.ModelForm):
    # Include fields from User model that we want to edit
    email = forms.EmailField(required=True)
    username = forms.CharField(disabled=True, required=False)  # Read-only

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            if age < 18:
                raise forms.ValidationError("You must be at least 18 years old to register.")
        return birth_date

    def clean_contact_number(self):
        contact_number = self.cleaned_data.get('contact_number')
        if contact_number:
            contact_number = re.sub(r'\D', '', contact_number)
            if len(contact_number) != 10:
                raise forms.ValidationError("Contact number must have exactly 10 digits.")
        return contact_number

    def clean_height(self):
        height = self.cleaned_data.get('height')
        if height and not (50 <= height <= 300):
            raise forms.ValidationError("Please enter a valid height in centimeters (50-300).")
        return height

    def clean_weight(self):
        weight = self.cleaned_data.get('weight')
        if weight and not (20 <= weight <= 500):
            raise forms.ValidationError("Please enter a valid weight in kilograms (20-500).")
        return weight

    class Meta:
        model = UserProfile
        exclude = ['user', 'bmi', 'profile_completion_percentage', 'last_updated', 'is_verified']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'last_checkup_date': forms.DateInput(attrs={'type': 'date'}),
            'medical_history': forms.Textarea(attrs={'rows': 3}),
            'current_medications': forms.Textarea(attrs={'rows': 3}),
            'chronic_conditions': forms.Textarea(attrs={'rows': 3}),
            'family_medical_history': forms.Textarea(attrs={'rows': 3}),
            'allergies': forms.Textarea(attrs={'rows': 3}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'profile_picture': forms.FileInput(),
        }
        labels = {
            'prakriti': 'Prakriti (Natural Constitution)',
            'vikruti': 'Vikruti (Current Imbalance)',
            'dosha_type': 'Predominant Dosha',
            'bmi': 'BMI (Auto-calculated)',
            'height': 'Height (in cm)',
            'weight': 'Weight (in kg)',
            'temperature': 'Body Temperature (°C)',
            'pulse_rate': 'Pulse Rate (BPM)',
        }
        help_texts = {
            'medical_history': 'List any past surgeries, conditions, or treatments.',
            'current_medications': 'Include both prescription and non-prescription medications.',
            'chronic_conditions': 'List any ongoing health conditions.',
            'dosha_type': 'Select your primary dosha type based on assessment.',
            'prakriti': 'Your natural body constitution.',
            'vikruti': 'Current state of body-mind constitution.',
            'profile_picture': 'Upload a clear, recent photo (optional).',
        }

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email').lower().strip()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email'].lower().strip()
        user.first_name = self.cleaned_data['first_name'].strip()
        user.last_name = self.cleaned_data['last_name'].strip()
        if commit:
            user.save()
        return user

class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture']
        widgets = {
            'profile_picture': forms.FileInput(attrs={'accept': 'image/*'})
        }

    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            if profile_picture.size > 5 * 1024 * 1024:
                raise ValidationError("Image file size must be less than 5MB.")
            try:
                img = Image.open(profile_picture)
                img.verify()
            except Exception:
                raise ValidationError("Invalid image file. Please upload a valid image.")
        return profile_picture

class HealthMetricForm(forms.ModelForm):
    class Meta:
        model = HealthMetric
        exclude = ['user']  # Exclude user field as it will be set in the view
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'sleep_hours': forms.NumberInput(attrs={'step': '0.5', 'min': '0', 'max': '24'}),
            'stress_level': forms.NumberInput(attrs={'min': '1', 'max': '10'}),
            'pulse_rate': forms.NumberInput(attrs={'min': '40', 'max': '200'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'sleep_hours': 'Sleep Hours',
            'stress_level': 'Stress Level (1-10)',
            'pulse_rate': 'Pulse Rate (BPM)',
            'weight': 'Weight (kg)',
            'blood_pressure': 'Blood Pressure (e.g., 120/80)',
        }

class ProfileEditForm(forms.ModelForm):
    # Include fields from User model that we want to edit
    email = forms.EmailField(required=True)
    username = forms.CharField(disabled=True, required=False)  # Read-only

    class Meta:
        model = UserProfile
        exclude = ['user', 'bmi', 'profile_completion_percentage', 'last_updated', 'is_verified']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'last_checkup_date': forms.DateInput(attrs={'type': 'date'}),
            'medical_history': forms.Textarea(attrs={'rows': 3}),
            'current_medications': forms.Textarea(attrs={'rows': 3}),
            'chronic_conditions': forms.Textarea(attrs={'rows': 3}),
            'family_medical_history': forms.Textarea(attrs={'rows': 3}),
            'allergies': forms.Textarea(attrs={'rows': 3}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'profile_picture': forms.FileInput(),
        }